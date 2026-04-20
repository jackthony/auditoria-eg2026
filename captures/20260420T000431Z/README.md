# Captura ONPE — 20260420T000431Z

- **Timestamp UTC:** 20260420T000431Z (2026-04-20 00:04:31 UTC)
- **Host:** DETI-0013
- **IP pública:** 38.43.130.179
- **SO:** Windows 11 (AMD64)
- **Git commit al momento de captura:** `d2415f1e46dc61ddda06345aed1e93c5c97e2f48`
- **Endpoints:** 8

## Verificación

Para comprobar la integridad:

```powershell
py src\capture\verify_manifest.py captures\20260420T000431Z\
```

Todos los archivos deben pasar el check. Un MISMATCH indica modificación
posterior al momento de captura.
