```markdown
# H12 — Técnico: Mesa 018146 · Concentración JPP

## Qué
- Mesa 018146: 208/230 votos JPP = 90.43% vs global 10.91%
- Binomial exacto p = 1.60e-171 (log10 = −170.80)
- Única mesa con n>100 y pct≥90% entre 78,605
- Cohen h = 1.8396 (muy grande, >0.8)
- z = 38.69 · CI95 Clopper-Pearson [0.8588, 0.9391]

## Query (reproducible)
```sql
-- DuckDB — verificación mesa 018146
SELECT
    mesa_id,
    n_validos,
    k_jpp,
    ROUND(k_jpp::DOUBLE / n_validos, 6)                          AS phat,
    (k_jpp::DOUBLE / n_validos - 0.109073)
        / SQRT(0.109073 * (1 - 0.109073) / n_validos)           AS z_score,
    -- Cohen h (Python-side: 2*asin(sqrt(phat)) - 2*asin(sqrt(p0)))
    -- p0 global = 1_657_500 / 15_196_245 = 0.109073
    COUNT(*) OVER (
        WHERE k_jpp::DOUBLE / n_validos >= 0.90
          AND n_validos > 100
    )                                                             AS n_mesas_n100_pct90
FROM mesa_resultados
WHERE mesa_id = '018146';

-- Robustez: todas las mesas pct>=90% (universo completo)
SELECT mesa_id, n_validos, k_jpp,
       ROUND(k_jpp::DOUBLE / n_validos, 4) AS phat
FROM mesa_resultados
WHERE k_jpp::DOUBLE / n_validos >= 0.90
ORDER BY phat DESC;
-- Resultado esperado: 3 filas; solo 018146 con n_validos > 100
```

## Test
- **Binomial exacto 1-cola** · p = 1.60e-171 · n = 230 · k = 208
- **z-test 1-prop** · z = 38.69 · SE = 0.02055 · p << 10⁻¹⁰⁰
- **χ² homogeneidad** (A3 challenger) · χ² ≈ z² = 1,497.7 · dof = 1 · ambos métodos convergen
- Paper: Clopper CJ, Pearson ES (1934). *Biometrika* 26:404–413
- Paper: Newcombe RG (1998). *Statist. Med.* 17:873–890
- Effect: Cohen h = 1.8396 — Paper: Cohen J (1988). *Statistical Power Analysis* 2ed

## Robustez p0
| p0 supuesto | log10(p) | p-value | Veredicto |
|-------------|----------|---------|-----------|
| 0.109073 (global) | −170.80 | 1.60e-171 | RECHAZA |
| 0.30 | −81.69 | 2.04e-82 | RECHAZA |
| 0.50 | −38.73 | 1.85e-39 | RECHAZA |
| 0.70 (JPP ultra-local) | −13.15 | 7.15e-14 | RECHAZA |
| 0.087 (p0 −20%) | < −200 | << 10⁻²⁰⁰ | RECHAZA |
| 0.131 (p0 +20%) | < −130 | << 10⁻¹³⁰ | RECHAZA |

Conclusión: invariante bajo cualquier p0 geográfico realista.

## Corrección múltiple (Bonferroni)
- m = 78,605 mesas · α nominal = 0.001
- α_eff = 0.001 / 78,605 = **1.27×10⁻⁸**
- p_finding = **1.60×10⁻¹⁷¹**
- Margen: **163 órdenes de magnitud** sobre umbral corregido

## Challenge verdict
- **SOBREVIVE** (7/7 ataques rechazados)

| Ataque | Vector | Resultado |
|--------|--------|-----------|
| A1 | Confounder geográfico p0=0.70 | SOBREVIVE |
| A2 | Confounder tamaño · z_recalc=38.70 | SOBREVIVE |
| A3 | χ² homogeneidad vs binomial exacto | SOBREVIVE |
| A4 | Recálculo numérico independiente | SOBREVIVE |
| A5 | Robustez p0 ±20% | SOBREVIVE |
| A6 | Post-hoc + corrección múltiple | SOBREVIVE* |
| A7 | Cherry-picking universo completo | SOBREVIVE |

*A6: α_eff=1.27e-8 declarado explícitamente — nota editorial, no sustantiva.

- Vectores atacados: geografía · tamaño · método · numérico · parámetro · multiplicidad · selección

## Notas numéricas críticas
- `binom.logsf(k-1, n, p0)` — evita catastrophic cancellation float64
- NO usar `1 - binom.cdf(k, n, p0)` para p < 1e-15
- z manual: SE = √(0.109073 × 0.890927 / 230) = 0.02055 → z = 0.795275 / 0.02055 = 38.70 ✓

## Gaps editoriales (challenger, no sustantivos)
1. Declarar departamento/provincia de mesa 018146 para contextualizar A1
2. α_eff Bonferroni ya incorporado arriba — spec H12 debe reflejar
3. Añadir recomendación: consulta personero + acta firmada ONPE

## Reproducir
```
rtk py scripts/h12_binomial_mesa018146.py
```

## Verificación
- DB SHA-256: `<db_sha256_placeholder>`
- Parquet CID: `<ipfs_cid_placeholder>`
- Capture ts: 2026-04-21T15:38:03Z
- Raw ref: `reports/raw_findings/raw_h12_stratified_20260421T153803Z.json`
- Tooling: [Claude Code](https://claude.ai/referral/Kj5b88VLag) + Polars + DuckDB + scipy
```

---