# Captura ONPE — 20260419T025134Z

- **Timestamp UTC:** 20260419T025134Z (2026-04-19 02:51:34 UTC)
- **Host:** DETI-0013
- **IP pública:** 38.43.130.179
- **SO:** Windows 11 (AMD64)
- **Git commit al momento de captura:** `(no commit aún)`
- **Endpoints:** 6

## Verificación

Para comprobar la integridad:

```powershell
py src\capture\verify_manifest.py captures\20260419T025134Z\
```

Todos los archivos deben pasar el check. Un MISMATCH indica modificación
posterior al momento de captura.
