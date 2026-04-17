# Captura ONPE — 20260417T062711Z (seed)

**Captura inicial incluida con el proyecto** para permitir que el pipeline
funcione desde el primer `git clone` sin tener que capturar primero contra
ONPE.

- **Timestamp UTC:** 2026-04-17 06:27:21 UTC
- **Origen:** proxy Cloudflare Worker (onpe-proxy.renzonunez-af.workers.dev)
- **Motivo del proxy:** la captura se generó desde un datacenter, donde ONPE
  bloquea el tráfico directo. Desde una IP peruana residencial, el script
  `src/capture/fetch_onpe.py` llegará al backend ONPE directamente.

## Verificación

```powershell
py src\capture\verify_manifest.py captures\20260417T062711Z\
```
