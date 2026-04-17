# Captura ONPE — 20260417T084114Z

- **Timestamp UTC:** 20260417T084114Z (2026-04-17 08:41:14 UTC)
- **Host:** DETI-0013
- **IP pública:** 190.237.6.208
- **SO:** Windows 11 (AMD64)
- **Git commit al momento de captura:** `9257a0f1a784e7a95c8bfa31e3460a0c961d6a4e`
- **Endpoints:** 5

## Verificación

Para comprobar la integridad:

```powershell
py src\capture\verify_manifest.py captures\20260417T084114Z\
```

Todos los archivos deben pasar el check. Un MISMATCH indica modificación
posterior al momento de captura.
