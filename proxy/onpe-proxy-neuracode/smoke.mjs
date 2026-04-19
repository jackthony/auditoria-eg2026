#!/usr/bin/env node
/**
 * Smoke test contra el Worker desplegado.
 * Uso: BASE=https://onpe-proxy-neuracode.<user>.workers.dev node smoke.mjs
 */
const BASE = process.env.BASE || "http://localhost:8787";
const PATHS = [
  "/presentacion-backend/proceso/proceso-electoral-activo",
  "/presentacion-backend/proceso/2/elecciones",
  "/presentacion-backend/resumen-general/totales?idEleccion=10&tipoFiltro=eleccion",
  "/presentacion-backend/resumen-general/mapa-calor?idEleccion=10&tipoFiltro=total",
  "/presentacion-backend/eleccion-presidencial/participantes-ubicacion-geografica-nombre?idEleccion=10&tipoFiltro=eleccion",
  "/presentacion-backend/mesa/totales?tipoFiltro=eleccion",
];

let ok = 0, fail = 0;
for (const p of PATHS) {
  const url = BASE + p;
  try {
    const r = await fetch(url, { headers: { Origin: "https://jackthony.github.io" } });
    const src = r.headers.get("x-proxy-source");
    const up = r.headers.get("x-upstream-status");
    const cache = r.headers.get("x-proxy-cache");
    const size = (await r.arrayBuffer()).byteLength;
    if (r.ok) {
      ok++;
      console.log(`OK  ${r.status} ${cache || "-"} ${src || "-"} up=${up || "-"} ${size}B  ${p}`);
    } else {
      fail++;
      console.log(`ERR ${r.status} ${p}`);
    }
  } catch (e) {
    fail++;
    console.log(`FAIL ${e.message} ${p}`);
  }
}
console.log(`\n${ok}/${PATHS.length} OK, ${fail} fail`);
process.exit(fail === 0 ? 0 : 1);
