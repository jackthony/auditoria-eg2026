# Hallazgos vigentes — auditoria-eg2026

**Última actualización:** 2026-04-20
**DB autoritativa:** `reports/hallazgos_20260420/eg2026.duckdb` (88,063 mesas · 3.6M actas)
**Findings consolidados:** `reports/hallazgos_20260420/findings_consolidado_0420.json`
**Findings maestros:** `reports/findings.json` (IDs `HALL-0420-H1/H2/H3`)

## Estado crítico (leer antes de cualquier análisis nuevo)

| ID | Severidad | Hallazgo | Métrica |
|----|-----------|----------|---------|
| HALL-0420-H1 | CRÍTICO | Sesgo geográfico impugnadas | Extranjero 26.35% · Loreto 15.3% · Ucayali 12% · global 6.15% |
| HALL-0420-H2 | MEDIA | Partidos concentran en locales alta imp | FP +2.19pp · JPP +0.87pp · BUEN GOBIERNO -1.64pp |
| HALL-0420-H3 | MEDIA | Outliers nulos/blancos | 4,091 mesas (4.65%) · San Martín 19.2% blancos #1 |

## Reglas vigentes

1. **Mapping prefix→depto ONPE = alfabético con Callao=24.** NO usar INEI. Validado 2026-04-20 (ver `scripts/validate_prefix_mapping.py`).
2. **DB autoritativa** = `eg2026.duckdb`. Rebuild con `python scripts/build_duckdb_and_fix.py`.
3. **Antes de afirmar rankings por partido o depto**: abrir `findings_consolidado_0420.json`, copiar cifras literales.
4. **Web/dashboard pendiente de actualizar** con hallazgos H1/H2/H3.

## Pointers

- DB: `reports/hallazgos_20260420/eg2026.duckdb`
- JSON consolidado: `reports/hallazgos_20260420/findings_consolidado_0420.json`
- JSON maestro: `reports/findings.json`
- Scripts: `scripts/build_duckdb_and_fix.py`, `scripts/analyze_hallazgos_0420_v2.py`, `scripts/h1_deep_dive.py`, `scripts/h1_san_martin.py`
- Memoria sesión: `MEMORY.md` → `project_hallazgos_0420.md`
