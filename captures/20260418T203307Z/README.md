# Captura ONPE — 20260418T203307Z

- **Timestamp UTC:** 20260418T203307Z (2026-04-18 20:33:07 UTC)
- **Host:** DETI-0013
- **IP pública:** 38.43.130.179
- **SO:** Windows 11 (AMD64)
- **Git commit al momento de captura:** `d3ed397ef344794d984a89d90529386d797e53a8`
- **Endpoints:** 5

## Verificación

Para comprobar la integridad:

```powershell
py src\capture\verify_manifest.py captures\20260418T203307Z\
```

Todos los archivos deben pasar el check. Un MISMATCH indica modificación
posterior al momento de captura.
