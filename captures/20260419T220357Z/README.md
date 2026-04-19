# Captura ONPE — 20260419T220357Z

- **Timestamp UTC:** 20260419T220357Z (2026-04-19 22:03:57 UTC)
- **Host:** DETI-0013
- **IP pública:** 38.43.130.179
- **SO:** Windows 11 (AMD64)
- **Git commit al momento de captura:** `829870de96949f72bcdfcf9e047644a464ec02b5`
- **Endpoints:** 8

## Verificación

Para comprobar la integridad:

```powershell
py src\capture\verify_manifest.py captures\20260419T220357Z\
```

Todos los archivos deben pasar el check. Un MISMATCH indica modificación
posterior al momento de captura.
