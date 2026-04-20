/**
 * onpe-proxy-neuracode — proxy puro ONPE para auditoria-eg2026.
 */

const ALLOWED_PATHS = new Set([
  "/presentacion-backend/proceso/proceso-electoral-activo",
  "/presentacion-backend/proceso/2/elecciones",
  "/presentacion-backend/resumen-general/totales",
  "/presentacion-backend/resumen-general/mapa-calor",
  "/presentacion-backend/resumen-general/elecciones",
  "/presentacion-backend/eleccion-presidencial/participantes-ubicacion-geografica-nombre",
  "/presentacion-backend/mesa/totales",
  "/presentacion-backend/actas",
  "/presentacion-backend/actas/observadas",
  "/presentacion-backend/ubigeos/departamentos",
  "/presentacion-backend/ubigeos/provincias",
  "/presentacion-backend/ubigeos/distritos",
]);

const ALLOWED_PREFIXES = [
  "/presentacion-backend/actas/",  // /actas/{id}
];

function corsHeaders(origin, allowedCsv) {
  const list = (allowedCsv || "").split(",").map((s) => s.trim()).filter(Boolean);
  const ok = list.includes(origin) ? origin : (list[0] || "*");
  return {
    "Access-Control-Allow-Origin": ok,
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Vary": "Origin",
  };
}

function jsonResp(status, obj, cors) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { "Content-Type": "application/json", ...cors },
  });
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const origin = request.headers.get("Origin") || "";
    const cors = corsHeaders(origin, env.ALLOWED_ORIGINS);

    try {
      if (request.method === "OPTIONS") {
        return new Response(null, { status: 204, headers: cors });
      }
      if (request.method !== "GET") {
        return jsonResp(405, { error: "Method not allowed" }, cors);
      }
      const pathOk = ALLOWED_PATHS.has(url.pathname) ||
        ALLOWED_PREFIXES.some((p) => url.pathname.startsWith(p));
      if (!pathOk) {
        return jsonResp(404, { error: `Path not in allowlist: ${url.pathname}` }, cors);
      }

      // Cache key: URL string simple.
      const cacheKey = new Request(url.toString(), { method: "GET" });
      const cache = caches.default;
      const cached = await cache.match(cacheKey);
      if (cached) {
        const hit = new Response(cached.body, cached);
        for (const [k, v] of Object.entries(cors)) hit.headers.set(k, v);
        hit.headers.set("X-Proxy-Cache", "HIT");
        return hit;
      }

      // Fetch upstream.
      const upstreamUrl = env.UPSTREAM + url.pathname + url.search;
      const upstream = await fetch(upstreamUrl, {
        method: "GET",
        headers: {
          "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
          "Accept": "application/json, text/plain, */*",
          "Accept-Language": "es-PE,es;q=0.9,en;q=0.8",
          "Accept-Encoding": "gzip, deflate",
          "Referer": "https://resultadoelectoral.onpe.gob.pe/",
          "Origin": "https://resultadoelectoral.onpe.gob.pe",
          "X-Requested-With": "XMLHttpRequest",
          "Sec-Fetch-Dest": "empty",
          "Sec-Fetch-Mode": "cors",
          "Sec-Fetch-Site": "same-origin",
          "Sec-Ch-Ua": '"Not(A:Brand";v="99", "Google Chrome";v="140", "Chromium";v="140"',
          "Sec-Ch-Ua-Mobile": "?0",
          "Sec-Ch-Ua-Platform": '"Windows"',
          "Priority": "u=1, i",
          "Connection": "keep-alive",
        },
      });

      // Validar que la respuesta final viene de onpe.gob.pe.
      let finalHost = "";
      try { finalHost = new URL(upstream.url).hostname; } catch {}
      if (finalHost && !finalHost.endsWith("onpe.gob.pe")) {
        return jsonResp(502, { error: `Untrusted redirect to ${finalHost}` }, cors);
      }

      const body = await upstream.arrayBuffer();
      const ttl = parseInt(env.CACHE_TTL || "30", 10);
      const response = new Response(body, {
        status: upstream.status,
        headers: {
          "Content-Type": upstream.headers.get("Content-Type") || "application/json",
          "Cache-Control": `public, max-age=${ttl}`,
          "X-Proxy-Source": "neuracode-cf",
          "X-Proxy-Ts": new Date().toISOString(),
          "X-Upstream-Status": String(upstream.status),
          "X-Upstream-Url": upstreamUrl,
          ...cors,
        },
      });

      if (upstream.status === 200) {
        ctx.waitUntil(cache.put(cacheKey, response.clone()));
      }
      const out = new Response(response.body, response);
      out.headers.set("X-Proxy-Cache", "MISS");
      return out;
    } catch (e) {
      return jsonResp(502, { error: "proxy_error", message: String(e && e.message || e) }, cors);
    }
  },
};
