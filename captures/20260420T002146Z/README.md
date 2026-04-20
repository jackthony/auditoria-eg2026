# Captura ONPE — 20260420T002146Z

- **Timestamp UTC:** 20260420T002146Z (2026-04-20 00:21:46 UTC)
- **Host:** DETI-0013
- **IP pública:** 38.43.130.179
- **SO:** Windows 11 (AMD64)
- **Git commit al momento de captura:** `99b751373745101fcafee9ec0a1bb2ae3a81f26f`
- **Endpoints:** 69

## Verificación

Para comprobar la integridad:

```powershell
py src\capture\verify_manifest.py captures\20260420T002146Z\
```

Todos los archivos deben pasar el check. Un MISMATCH indica modificación
posterior al momento de captura.
