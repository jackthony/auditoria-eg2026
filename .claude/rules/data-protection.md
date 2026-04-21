# Data Protection — Cadena de custodia

> Protege la integridad de evidencia. Violación = pérdida de credibilidad pública.

## Rutas INMUTABLES (jamás editar)

| Ruta | Razón | Sanción |
|---|---|---|
| `captures/{tsUTC}/**` | Raw ONPE con SHA-256 en MANIFEST | Bloquear Edit/Write |
| `captures/{tsUTC}/MANIFEST.jsonl` | Prueba criptográfica L1 | Bloquear |
| `reports/hallazgos_20260420/eg2026.duckdb` | DB autoritativa — solo rebuild | Solo `scripts/build_duckdb_and_fix.py` |
| `reports/hf_dataset/*.parquet` | Pineado en IPFS+HF | No editar, solo reemplazar con nuevo |
| `reports/ipfs_cids.json` | CIDs pineados | Solo append |

## Re-captura

Re-capturar = **carpeta nueva UTC** + commit inmediato. Nunca sobrescribir.

```
captures/20260419T035056Z/   ← original intocable
captures/20260502T120000Z/   ← re-captura nueva
```

## Outputs agentes (escritura restringida)

| Ruta | Quién escribe |
|---|---|
| `reports/raw_findings/raw_h<N>_*.json` | Solo `data-forensic` |
| `reports/stat_findings/stat_h<N>_*.json` | Solo `stats-expert` |
| `reports/narratives/HALL-*/` | Solo `audit-narrator` |

Un agente NO sobrescribe output de otro. Discrepancia → nuevo timestamp.

## Commits peligrosos (bloquear)

- `git push --force` a main/master
- Commit que modifique `captures/**`
- Commit con `.env` (secretos)
- Commit que borre `reports/stat_findings/*` sin ticket asociado

## Verificación obligatoria post-captura

```bash
py src/capture/verify_manifest.py captures/<ts>/
```

Si falla un byte → código ≠ 0 → detener pipeline.

## IPFS re-pin

Nuevos artefactos requieren doble pin (Filebase + Pinata) registrado en `reports/ipfs_cids.json` con SHA-256.
