# Captura ONPE — 20260419T031241Z

- **Timestamp UTC:** 20260419T031241Z (2026-04-19 03:12:41 UTC)
- **Host:** DETI-0013
- **IP pública:** 38.43.130.179
- **SO:** Windows 11 (AMD64)
- **Git commit al momento de captura:** `5ecfd3cf74adc19f1ebc5627ac44df1c397d348f`
- **Endpoints:** 8

## Verificación

Para comprobar la integridad:

```powershell
py src\capture\verify_manifest.py captures\20260419T031241Z\
```

Todos los archivos deben pasar el check. Un MISMATCH indica modificación
posterior al momento de captura.
