# onpe-proxy-neuracode

Cloudflare Worker — proxy puro para endpoints ONPE del proceso presidencial 2026.

## Deploy (90 segundos)

```bash
cd proxy/onpe-proxy-neuracode
npm install
npx wrangler login        # abre browser, login Cloudflare (1 vez)
npx wrangler deploy       # sube el Worker
# URL final: https://onpe-proxy-neuracode.<tu-subdominio>.workers.dev
```

## Smoke test

```bash
# Local
npx wrangler dev
# en otra terminal:
node smoke.mjs

# Producción
BASE=https://onpe-proxy-neuracode.<tu>.workers.dev node smoke.mjs
```

## Arquitectura (crítico leer)

- **Sin estado.** Ni KV, ni DO, ni DB. Cache edge 30s solo.
- **Allowlist hardcoded** de 6 endpoints ONPE. Cualquier otro path → 404.
- **CORS restringido** a gh-pages + localhost.
- **Anti-redirect-hijack:** si ONPE redirige a host ≠ `onpe.gob.pe`, 502.
- **Cadena de custodia:** el Worker NO es fuente pericial. Solo transporte.
  La evidencia vive en `captures/{tsUTC}/` commiteados en git.

## Headers de respuesta

| Header | Valor |
|--------|-------|
| `X-Proxy-Source` | `neuracode-cf` |
| `X-Proxy-Ts` | ISO timestamp de respuesta |
| `X-Proxy-Cache` | `HIT` o `MISS` |
| `X-Upstream-Status` | Status HTTP de ONPE |
| `X-Upstream-Url` | URL real consultada |

## Ver logs en vivo

```bash
npx wrangler tail
```
