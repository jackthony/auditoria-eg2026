/**
 * onpe-proxy-neuracode — proxy puro ONPE para auditoria-eg2026.
 *
 * Principios:
 *  - Allowlist estricto de paths (no proxy abierto).
 *  - CORS restringido a orígenes conocidos.
 *  - Cache edge 30s (reduce carga upstream + latencia).
 *  - Header de trazabilidad X-Proxy-Source para cadena de custodia.
 *  - Sin estado (KV/Durable Objects). La evidencia pericial vive en git.
 */

const ALLOWED_PATHS = new Set([
  "/presentacion-backend/proceso/proceso-electoral-activo",
  "/presentacion-backend/proceso/2/elecciones",
  "/presentacion-backend/resumen-general/totales",
  "/presentacion-backend/resumen-general/mapa-calor",
  "/presentacion-backend/eleccion-presidencial/participantes-ubicacion-geografica-nombre",
  "/presentacion-backend/mesa/totales",
]);

function corsHeaders(origin, allowed) {
  const list = allowed.split(",").map((s) => s.trim());
  const ok = list.includes(origin) ? origin : list[0];
  return {
    "Access-Control-Allow-Origin": ok,
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Vary": "Origin",
  };
}

function jsonError(status, msg, cors) {
  return new Response(JSON.stringify({ error: msg, proxy: "neuracode" }), {
    status,
    headers: { "Content-Type": "application/json", ...cors },
  });
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const origin = request.headers.get("Origin") || "";
    const cors = corsHeaders(origin, env.ALLOWED_ORIGINS);

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: cors });
    }
    if (request.method !== "GET") {
      return jsonError(405, "Method not allowed", cors);
    }

    // Allowlist check (sin query string)
    if (!ALLOWED_PATHS.has(url.pathname)) {
      return jsonError(404, `Path not in allowlist: ${url.pathname}`, cors);
    }

    // Cache edge por URL completa
    const cacheKey = new Request(url.toString(), request);
    const cache = caches.default;
    let response = await cache.match(cacheKey);
    if (response) {
      const hit = new Response(response.body, response);
      hit.headers.set("X-Proxy-Cache", "HIT");
      for (const [k, v] of Object.entries(cors)) hit.headers.set(k, v);
      return hit;
    }

    // Forward a ONPE
    const upstreamUrl = env.UPSTREAM + url.pathname + url.search;
    const upstreamReq = new Request(upstreamUrl, {
      method: "GET",
      headers: {
        "User-Agent": "Mozilla/5.0 (compatible; AuditoriaEG2026-Neuracode/1.0; +https://github.com/jackthony/auditoria-eg2026)",
        "Accept": "application/json",
        "Referer": "https://resultadoelectoral.onpe.gob.pe/",
      },
      redirect: "error", // no seguir redirects a otros hosts
    });

    let upstream;
    try {
      upstream = await fetch(upstreamReq, { cf: { cacheTtl: 30, cacheEverything: true } });
    } catch (e) {
      return jsonError(502, `Upstream fetch failed: ${e.message}`, cors);
    }

    // Validar host de respuesta (anti-redirect-hijack)
    const finalUrl = new URL(upstream.url);
    if (!finalUrl.hostname.endsWith("onpe.gob.pe")) {
      return jsonError(502, `Untrusted redirect to ${finalUrl.hostname}`, cors);
    }

    const body = await upstream.arrayBuffer();
    const tsIso = new Date().toISOString();

    response = new Response(body, {
      status: upstream.status,
      headers: {
        "Content-Type": upstream.headers.get("Content-Type") || "application/json",
        "Cache-Control": `public, max-age=${env.CACHE_TTL}`,
        "X-Proxy-Source": "neuracode-cf",
        "X-Proxy-Ts": tsIso,
        "X-Upstream-Status": String(upstream.status),
        "X-Upstream-Url": upstreamUrl,
        ...cors,
      },
    });

    // Guardar en cache edge (no bloquea respuesta)
    ctx.waitUntil(cache.put(cacheKey, response.clone()));

    const out = new Response(response.body, response);
    out.headers.set("X-Proxy-Cache", "MISS");
    return out;
  },
};
