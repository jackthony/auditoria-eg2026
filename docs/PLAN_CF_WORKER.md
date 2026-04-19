# PLAN — Cloudflare Worker `onpe-proxy-neuracode` + captura continua forense

**Fecha:** 2026-04-18
**Owner:** Jack Aguilar (Tony)
**Estado:** APROBADO — arrancar ya.
**Ventana:** 93.48% escrutado, quedan ~2-3 días de cortes relevantes. Deploy en ≤90 min.

---

## Objetivo
Tener captura ONPE 24/7 sin depender de la PC local, **sin sacrificar cadena de custodia forense**. Combinar la velocidad del approach de Renzo (Worker) con la integridad de SHA-256 + git + IP peruana validada.

## Principios (algoritmo Musk)
1. **Cuestionar:** ¿necesitamos KV como Renzo? → **NO**. Los snapshots viven en `captures/{tsUTC}/` commiteados en git. KV = mutable = no forense.
2. **Eliminar:** nada de Durable Objects, nada de base de datos. El Worker es **proxy puro + CORS** + cache agresivo 30s. Nada más.
3. **Simplificar:** 1 Worker, 1 handler, 1 archivo `worker.js` (~60 líneas).
4. **Acelerar:** el loop de captura local sigue siendo quien sella SHA-256. El Worker solo resuelve bloqueo de IP.
5. **Automatizar:** cron trigger del Worker **no guarda nada** — solo warm-cache. La captura inmutable la hace GitHub Actions workflow cada 10 min desde IP de Actions (global) hacia nuestro Worker.

---

## Arquitectura final

```
┌─────────────────────────────────────────────────────────────┐
│  ONPE resultadoelectoral.onpe.gob.pe/presentacion-backend/  │
│  (bloquea datacenters no peruanos)                          │
└─────────────────┬───────────────────────────────────────────┘
                  │ fetch (CF Worker IP pasa el bloqueo)
                  ▼
┌─────────────────────────────────────────────────────────────┐
│  onpe-proxy-neuracode.<user>.workers.dev                    │
│  - Proxy puro con CORS: *                                   │
│  - Cache-Control 30s (Worker edge cache)                    │
│  - Allowlist de paths (no proxy abierto)                    │
│  - Header X-Proxy-Source: neuracode-cf                      │
│  - Rate limit 10 req/s por IP                               │
└─────────────────┬───────────────────────────────────────────┘
                  │
     ┌────────────┴────────────┐
     ▼                         ▼
┌──────────────────┐    ┌──────────────────────────────────┐
│ Frontend         │    │ GitHub Actions (cron cada 10min) │
│ gh-pages         │    │ - Llama Worker                   │
│ - Live data      │    │ - Sella SHA-256                  │
│ - Sin CORS error │    │ - Commit captures/{tsUTC}/       │
└──────────────────┘    │ - Push firmado                   │
                        └──────────────────────────────────┘
                                    │
                                    ▼
                        ┌──────────────────────────────────┐
                        │ Local (Tony) una vez al día      │
                        │ - Pull                           │
                        │ - verify_manifest.py             │
                        │ - Re-sellado con IP peruana      │
                        │   si hay cortes críticos         │
                        └──────────────────────────────────┘
```

**Clave forense:** el Worker NO es la fuente de verdad. Es solo un "relay". La fuente de verdad sigue siendo `captures/{tsUTC}/` en git.

---

## Sub-tickets ordenados (total ~90 min)

### CFW-01 — Bootstrap Worker (15 min)
- Crear cuenta/proyecto CF si no existe
- `npm create cloudflare@latest proxy/onpe-proxy-neuracode`
- Stack: Worker vanilla JS, sin framework
- **Output:** proyecto vacío compilable

### CFW-02 — Proxy handler + allowlist (20 min)
- `proxy/onpe-proxy-neuracode/src/worker.js`
- Allowlist hardcoded de paths ONPE conocidos:
  - `/presentacion-backend/proceso/proceso-electoral-activo`
  - `/presentacion-backend/proceso/2/elecciones`
  - `/presentacion-backend/resumen-general/totales`
  - `/presentacion-backend/resumen-general/mapa-calor`
  - `/presentacion-backend/eleccion-presidencial/participantes-ubicacion-geografica-nombre`
  - `/presentacion-backend/mesa/totales`
- Reenvío con header `Referer: https://resultadoelectoral.onpe.gob.pe/`
- CORS: `Access-Control-Allow-Origin: https://jackthony.github.io`
- Headers de respuesta: `X-Proxy-Source`, `X-Proxy-Ts`, `X-Upstream-Status`
- Timeout 10s, sin redirects (`redirect: "error"`)

### CFW-03 — Rate limit + cache (10 min)
- `cache.default.match(request)` / `cache.default.put(response)`
- TTL 30s en cache edge
- Rate limit: max 10 req/s por IP (headers `cf-connecting-ip`)

### CFW-04 — Deploy + smoke test (10 min)
- `wrangler deploy`
- Verificar los 6 endpoints desde curl con User-Agent real
- Registrar URL final + primer timestamp en `docs/ONPE_API_ENDPOINTS.md`

### CFW-05 — Integrar al frontend + al capture_loop.py local (15 min)
- Cambiar `PROXY_BASE` en `src/capture/fetch_onpe.py` de Renzo al nuestro
- Variable de entorno `ONPE_PROXY_BASE` con fallback al de Renzo si el nuestro cae (resiliencia)
- Commit con nota: "Neuracode proxy reemplaza dependencia de Renzo"

### CFW-06 — GitHub Action cron forense (20 min)
- `.github/workflows/capture.yml`
- Cron: `*/10 * * * *` (cada 10 min)
- Steps:
  1. Checkout
  2. Setup Python
  3. `py make.py capture` → llama Worker, sella SHA-256
  4. `py make.py build analyze`
  5. `py scripts/build_dashboard_json.py`
  6. Commit + push si hay cambios
  7. Deploy a gh-pages
- **Secret obligatorio:** commit-signing key (GPG)

---

## Restricciones forenses (no negociables)

1. **El Worker NO guarda estado.** Cache edge es mutable → no vale como evidencia.
2. **Solo `captures/{tsUTC}/` es fuente pericial.** Worker es transporte.
3. **MANIFEST.jsonl del capture debe incluir:**
   - `url_upstream`: URL real de ONPE (no la del Worker)
   - `url_proxy`: URL del Worker usada
   - `x_proxy_source`: header que el Worker devolvió (autenticidad)
   - `github_run_id`: si fue capturado desde Actions, el run ID (trazabilidad)
4. **Allowlist estricto:** el Worker solo proxea los 6 endpoints documentados. Cualquier otro path → 404. Previene uso como proxy abierto.
5. **No secrets en el Worker.** Si necesitamos API keys, van en `wrangler secret put`.

---

## Riesgos + mitigación

| Riesgo | Prob | Impacto | Mitigación |
|--------|------|---------|-----------|
| CF tumba el Worker por ToS ONPE | Baja | Alto | Fallback a proxy Renzo + documentación que datos son públicos |
| ONPE bloquea User-Agent del Worker | Media | Alto | Rotar UA; si falla, capture manual desde IP peruana |
| Actions cron no corre (cuota free) | Baja | Medio | 2000 min/mes free — alcanzan para 10 min × 3 días |
| Worker abuso third-party | Media | Medio | Allowlist + rate limit + CORS restrictivo |

---

## Métricas de éxito

- [ ] 6/6 endpoints ONPE accesibles via Worker sin 403
- [ ] Frontend GitHub Pages consume Worker sin CORS error
- [ ] GitHub Action corre cada 10 min sin fallos por 24h
- [ ] `captures/` crece con 1 carpeta `{tsUTC}` nueva por cada corte ONPE que cambie
- [ ] `verify_manifest.py` pasa 100% sobre todas las capturas nuevas

---

## Siguiente paso tras este plan
MESA-02 — jalar `/presentacion-backend/mesa/totales` (ya accesible via Worker) y reconciliar suma mesa-a-mesa vs total nacional. Verificación independiente del contaje contable.
