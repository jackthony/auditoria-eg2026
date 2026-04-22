# Hallazgos vigentes — auditoria-eg2026

**Fecha:** 2026-04-21 · **DB:** `reports/hallazgos_20260420/eg2026.duckdb` (92,766 mesas · 3.79M actas) · **Parquet HF:** `reports/hf_dataset/onpe_eg2026_mesas_20260420T074202Z.parquet`

## Universo

| Grupo | Rango | N mesas |
|-------|-------|---------|
| Normales | 000001-088064 | 88,063 |
| Especiales 900k+ | 900001-904703 | 4,703 |
| **TOTAL** | — | **92,766** |

## 6 findings blindados (pipeline data-forensic + stats-expert 2026-04-21)

| ID | Severidad | Hallazgo | Métrica |
|----|-----------|----------|---------|
| H1 | CRÍTICO | Sesgo geográfico impugnadas | χ²=2,897 dof=25 · global 6.16% · Extranjero 26.27% (z=42.2) · Loreto 14.87% · Ucayali 12.02% |
| H2 | MEDIA | Partidos vs locales alta-imp (Q80=0.1250) | FP +2.81pp · País Para Todos +0.91pp · JPP +0.89pp · BUEN GOBIERNO -2.12pp |
| H3 | MEDIA | Outliers nulos/blancos (z>3) | 2,320 mesas (2.68%) · San Martín 19.62% · Ucayali 19.44% · Loreto 18.66% |
| H4 | CRÍTICO | JPP concentra 900k+ | **41.65% esp (235,331/565,060) vs 10.91% norm (1,657,500/15,196,245)** · ratio 3.82x · z=698 · χ²=487,171 · Cohen h=0.73 · OR=5.83 |
| H9 | CRÍTICO | BERBÉS Salta cadena custodia | 11/11 impugnadas · log₁₀P=-13.32 · p=4.83e-14 · único local n≥10 al 100% |
| H12 | CRÍTICO | Mesa 018146 Cusco blowout | JPP 208/230=90.43% · log₁₀P=-170.80 · única n>100 al ≥90% entre 78,605 · robusta aun con p0=70% (p=7.15e-14) |

## Reglas

1. Universo = 92,766. Toda métrica nueva usa este total.
2. Mapping prefix→depto = ONPE alfabético con Callao=24.
3. DB autoritativa = `eg2026.duckdb`. Rebuild: `py scripts/build_duckdb_and_fix.py`.
4. Solo métodos del paper registry (`memory/reference_papers_forenses.md`). Benford-1 prohibido.
5. Probabilidades <1e-15 → `binom.logsf` (nunca `1-cdf`).
6. Stack: Polars + DuckDB + PyArrow. Pandas prohibido >100k filas.
7. Defensa pública: "anomalía que ONPE debe explicar", jamás "fraude".

## Artefactos

- raw: `reports/raw_findings/raw_h{1,2,3,4,9,12}_*.json`
- stats: `reports/stat_findings/stat_h{1,2,3,4,9,12}_*.json`
- paper registry: `memory/reference_papers_forenses.md`
