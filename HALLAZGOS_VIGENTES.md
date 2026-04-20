# Hallazgos vigentes — auditoria-eg2026

**Última actualización:** 2026-04-20 (v2-92k + cross-checks blindados H9/H12)
**DB autoritativa:** `reports/hallazgos_20260420/eg2026.duckdb` (**92,766 mesas · 3.79M actas**)
**Parquet HF:** `reports/hf_dataset/onpe_eg2026_mesas_20260420T074202Z.parquet`
**Findings consolidados:** `reports/hallazgos_20260420/findings_consolidado_0420.json` (H1-H4 sincronizados) + `reports/menu_publicacion.md` (H9/H12 en validación)
**Findings maestros:** `reports/findings.json` (IDs `HALL-0420-H1/H2/H3/H4`)
**Web endpoint:** `web/api/findings.json` (mismos 4 findings)

## Universo v2 (corregido 2026-04-20)

| Grupo | Rango código | N mesas | Confirmado |
|-------|--------------|---------|------------|
| Normales | 000001-088064 (gap 087704) | 88,063 | ONPE 100% por depto |
| Especiales 900k+ | 900001-904703 | 4,703 | recuperadas tras fix walker |
| **TOTAL** | — | **92,766** | barrido bordes OK (`reports/universe_check.json`) |

## Estado crítico (6 findings vivos)

| ID | Severidad | Hallazgo | Métrica clave |
|----|-----------|----------|---------------|
| HALL-0420-H1 | CRÍTICO | Sesgo geográfico impugnadas | Extranjero 26.27% (z=42.2) · Loreto 14.87% · Ucayali 12.02% · global 6.16% · χ²=2,897 (Bonferroni pasa) |
| HALL-0420-H2 | MEDIA | Partidos concentran en locales alta-imp | FP +2.07pp · JPP +0.88pp · BUEN GOBIERNO -1.62pp |
| HALL-0420-H3 | MEDIA | Outliers nulos/blancos | **5,304 mesas (5.72%)** · San Martín 19.62% blancos #1 · Loreto mesas 900k+ >90% blancos |
| HALL-0420-H4 | CRÍTICO | JPP concentra en mesas 900k+ | **JPP 41.65% en 4,700 esp vs 10.91% en normales** · ratio 3.82x · z=698 · χ²=487,171 · OR=5.83 · Cohen h=0.73 · IC95 [29.46%, 30.79%] · per-depto 2.6-4.2× (Lib 4.16, Loreto 3.62, Areq 3.37, Piura 3.10, Ucayali 3.00, Lima 2.93, Lamb 2.82, Áncash 2.61) — NO artefacto regional |
| HALL-0420-H9 | CRÍTICO (validación) | BERBÉS Salta — cadena custodia | Consulado Salta, 11/11 mesas impugnadas (100%) · p=4.83e-14 (**1 entre 20 billones**) · binomial exacto vs tasa global 6.1585% |
| HALL-0420-H12 | CRÍTICO (validación) | Mesa 018146 Cusco — blowout emblemático | JPP 208/230 = **90.43%** · única mesa normal ≥90% entre 78,706 (0.0013%) · binomial p=0 exacto · 2do Cívico Obras 4.35% |

## Reglas vigentes

1. **Universo = 92,766 mesas**. Toda métrica nueva debe usar este total.
2. **Mapping prefix→depto ONPE = alfabético con Callao=24.** NO usar INEI. Validado 2026-04-20.
3. **DB autoritativa** = `eg2026.duckdb`. Rebuild con `py scripts/build_duckdb_and_fix.py`.
4. **Antes de afirmar rankings por partido o depto**: abrir `findings_consolidado_0420.json`, copiar cifras literales.
5. **Solo métodos no refutados** (z-test Newcombe, Cohen h, bootstrap Efron-Tibshirani, Mann-Whitney). Benford-1 prohibido.
6. **Stack obligatorio:** Polars + DuckDB + PyArrow. Pandas prohibido para >100k filas.
7. **Cualquier afirmación pública usa H4 con la regla de oro:** "anomalía que ONPE debe explicar", nunca "fraude".
8. **Findings stale eliminados (no recuperar):** R1, A1, A2, C1, D1-D3, E1, G1, A0, F1, M1-M3, A-AUS-1/2/3, MESA-IMP-1/2.
9. **H9 y H12 en validación:** documentados en `reports/menu_publicacion.md` + `reports/storytelling_pack.md` (piezas 4, 5). Pendiente: sincronizar a `findings_consolidado_0420.json` + `findings.json` + `web/api/findings.json` con `scripts/sync_findings_v2.py` extendido.
10. **Descartados (no tocar):** H5 (trivial OK identidad), H13 Klimek standalone (negativo, pero se usa DENTRO de H4 como honestidad), H14 Beber-Scacco (artefacto power-law), H16 mesas gemelas (sin paper directo).

## Pointers

- DB: `reports/hallazgos_20260420/eg2026.duckdb`
- Stats H4: `reports/h4_stats.json`
- Scripts vigentes:
  - `scripts/build_duckdb_and_fix.py` (rebuild duckdb desde parquet)
  - `scripts/analyze_hallazgos_0420_v2.py` (H1/H2/H3)
  - `scripts/stats_h4_especiales_900k.py` (H4)
  - `scripts/sync_findings_v2.py` (sincroniza 3 findings.json)
  - `scripts/test_universe_complete.py` (barrido bordes ONPE)
- Tests: `tests/test_dataset_integrity.py` (12 tests, polars+duckdb)
- Walker: `src/capture/fetch_onpe_mesas_async.py` (default ranges 1-88064 + 900001-904703)
- Memoria sesión: `MEMORY.md` → `project_hallazgos_0420.md`, `feedback_data_libs.md`
