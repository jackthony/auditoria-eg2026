```markdown
# H12 — Técnico · Mesa 018146 · Concentración JPP

> Generado con [Claude Code](https://claude.ai/referral/Kj5b88VLag)

## Qué
- Mesa 018146: 208/230 votos JPP = **90.43%** vs global 10.91%
- Binomial exacto 1-cola: p = **1.60e-171** (38.7σ sobre media esperada)
- Única mesa con n>100 AND pct_JPP≥90% en universo de 78,605 mesas normales

## Query (reproducible)

```sql
-- DuckDB · dataset: onpe_eg2026_mesas_normales
SELECT
    mesa_id,
    votos_jpp,
    total_validos,
    ROUND(votos_jpp * 1.0 / total_validos, 6)          AS phat,
    1657500.0 / 15196245.0                              AS p0_global,
    total_validos                                        AS n
FROM mesas_normales
WHERE mesa_id = '018146';

-- Universo de anomalías ≥90%
SELECT
    mesa_id,
    votos_jpp,
    total_validos,
    ROUND(votos_jpp * 1.0 / total_validos, 4)           AS pct_jpp
FROM mesas_normales
WHERE (votos_jpp * 1.0 / total_validos) >= 0.90
ORDER BY total_validos DESC;
-- Resultado: 3 mesas; solo 018146 con n>100
```

## Reproducción Python (verificación scipy)

```python
from scipy.stats import binom
import math, scipy

# versión scipy requerida para replicar exacto
print(scipy.__version__)           # registrar en audit log

n, k, p0 = 230, 208, 0.109073
log_p_nat = binom.logsf(k - 1, n, p0)   # P(X >= k) en log natural
log10_p   = log_p_nat / math.log(10)
print(f"log10_p = {log10_p:.2f}")        # esperado: -170.8
print(f"p       = {10**log10_p:.2e}")    # esperado: 1.60e-171

# Robustez paramétrica
for p_alt in [0.30, 0.50, 0.70]:
    lp = binom.logsf(k - 1, n, p_alt) / math.log(10)
    print(f"p0={p_alt} → log10_p={lp:.2f}")
```

> **Nota A4 (challenger):** valor −170.8 NO replicable via Stirling manual
> (error ~20 órdenes). Usar scipy.logsf nativo (Cython/Fortran).
> Cualquier revisor replica en <30 s con bloque anterior.

## Tests

| Test | Estadístico | p-value | n |
|------|-------------|---------|---|
| Binomial exacto 1-cola (Clopper-Pearson) | — | **1.60e-171** | 230 |
| z-test 1-proporción | z = **38.69** | ~1.60e-171 | 230 |
| χ² homogeneidad 2×2 | χ² = **1,497** (1 gl) | <1e-100 | 230 vs 15,196,245 |

- **Effect size:** Cohen h = **1.8396** (muy grande; umbral >0.8)
- **IC 95% Clopper-Pearson:** [0.8588, 0.9391]
- **p0 global:** 0.109073 (1,657,500 / 15,196,245 votos JPP en mesas normales)
- Papers: Clopper & Pearson (1934) Biometrika 26:404-413 · Newcombe (1998) Statist. Med. 17:873-890 · Cohen (1988) Statistical Power Analysis 2ed

## Robustez paramétrica p0

| p0 supuesto | Escenario | log₁₀(p) | p humano |
|-------------|-----------|-----------|----------|
| 0.109073 | Global observacional | −170.8 | 1.60e-171 |
| 0.30 | JPP feudo regional | −81.69 | 2.04e-82 |
| 0.50 | JPP mayoría simple | −38.73 | 1.85e-39 |
| 0.70 | JPP ultra-favorito | −13.15 | 7.15e-14 |

> Rechazo bajo **cualquier** p0 ≤ 0.90 razonable. p0 > ~0.95 para erosionar —
> ese escenario base es per se anómalo.

## Challenge verdict

**SOBREVIVE** (2 debilidades menores de redacción, no de sustancia)

| Ataque | Resultado |
|--------|-----------|
| A1 Confounder geográfico | SOBREVIVE — p0=0.70 → p≈7e-14 |
| A2 Confounder tamaño mesa | SOBREVIVE — n=230 endurece rechazo |
| A3 Método alternativo χ² | SOBREVIVE — χ²≈1497 coincide orden magnitud |
| A4 Verificación numérica exacta | DEBIL-menor — dirección coincide; valor exacto requiere scipy |
| A5 Robustez p0±20% | SOBREVIVE — invariante hasta p0=0.70 |
| A6 Post-hoc / Bonferroni | DEBIL-menor — declarado; superado por 162 órdenes; redacción corregida ↓ |
| A7 Cherry-picking | SOBREVIVE — 3 mesas ≥90% reportadas íntegramente |

**Corrección A6 aplicada (challenger req.):**
> Bonferroni aplicado sobre 78,605 mesas → α_adj = 6.4e-9.
> p observado = 1.6e-171 supera umbral por **162 órdenes de magnitud**.

## Limitaciones declaradas

1. **Post-hoc:** Mesa identificada por búsqueda exhaustiva. Bonferroni aplicado
   y superado (ver A6). Corrección Bonferroni: α_adj = 0.001 / 78,605 = 6.4e-9.
2. **p0 observacional:** Asume homogeneidad nacional. Mitigado con escenarios
   hasta p0=0.70 — todos rechazan masivamente.
3. **No implica intencionalidad.** Puede ser liderazgo local legítimo.
   Requiere verificación de personeros, actas firmadas y observadores.

## Regla de oro

> Anomalía estadística que ONPE debe explicar (personero, acta firmada,
> observador). **No se afirma fraude.**

## Reproducir

```bash
# requiere: rtk ≥ 0.3, scipy ≥ 1.11, duckdb ≥ 0.10
rtk py scripts/h12_mesa018146_binomial.py

# output esperado
# log10_p = -170.80
# p       = 1.60e-171
# cohen_h = 1.8396
# ci95    = [0.8588, 0.9391]
```

## Verificación · Cadena de custodia

| Campo | Valor |
|-------|-------|
| DB SHA-256 | `<hash_db_onpe_eg2026>` |
| Parquet CID (IPFS) | `<cid_parquet_mesas_normales>` |
| Raw finding ref | `reports/raw_findings/raw_h12_stratified_20260421T153803Z.json` |
| Capture timestamp | 2026-04-21T15:38:03Z |
| Challenger timestamp | 2026-04-21T16:45:00Z |
| Spec | `docs/specs/H12.md` |
| Branch | `forensis/H12-20260421T153803Z` |
| Dataset | HuggingFace `Neuracode/onpe-eg2026-mesa-a-mesa` |
```

---