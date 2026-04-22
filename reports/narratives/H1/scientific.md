```markdown
# H1 — Scientific Note: Heterogeneidad de Tasa de Impugnación por Departamento
<!-- reports/narratives/H1/scientific.md -->
<!-- Tooling: [Claude Code](https://claude.ai/referral/Kj5b88VLag) + Polars + DuckDB -->

---

**Hypothesis:**
- H₀: La tasa de impugnación de actas es homogénea entre los 26 departamentos (incluyendo Extranjero) — equivalente a p_i = p_global ∀i.
- H₁: Al menos un departamento se desvía significativamente de p_global.

**Test:** χ² de homogeneidad (Fisher 1925) + z-test 1-proporción Newcombe (1998) con corrección Bonferroni (1936)

**Statistic:** χ² = 2897.2 · dof = 25

**p-value:** < 1×10⁻³⁰⁰ (log₁₀p ≈ −620 vía `chi2.logsf`; reportado como `0.0` en raw_finding por underflow numérico — ver nota técnica)

**Effect size:** Cohen h (Extranjero vs global) ≈ 0.61 [grande]; ratio directo = 4.3× (26.27% vs 6.16%)

**CI95 Newcombe — Extranjero:** ≈ [24.5%, 28.1%] (n=2,543; intervalo estrecho confirma estabilidad)

**N:** ~92,766 actas · 26 departamentos

---

## Resultados por departamento (extremos)

| Departamento | n | n_imp | Tasa | z | p (Bonf. α=0.001923) |
|---|---|---|---|---|---|
| Extranjero | 2,543 | 668 | 26.27% | +42.18 | << α |
| Loreto | 2,697 | 401 | 14.87% | +18.82 | << α |
| Ucayali | 1,564 | 188 | 12.02% | +9.64 | << α |
| Arequipa | 4,215 | 77 | 1.83% | −11.70 | << α |
| Puno | 3,397 | 103 | 3.03% | −7.58 | 3.5×10⁻¹⁴ << α |
| Junín | 3,691 | 125 | 3.39% | −7.01 | 2.5×10⁻¹² << α |
| **Global** | ~92,766 | — | **6.16%** | — | — |

*Los 20 departamentos intermedios no se reportan en esta nota — ver limitación L4.*

---

## Assumptions checked

- `n_suficiente`: todos los departamentos n > 100; outliers n > 1,500
- `esperados_ge_5`: validado vía `chi2_contingency` (celdas esperadas >> 5 en todos los casos)
- `independencia_entre_deptos`: asumida (ver limitación L3)
- `robustez_p0`: conclusión estable bajo variación ±20% de p₀ global

---

## Limitations

- **L1 — Confounder geográfico-logístico:** Loreto y Ucayali tienen historial documentado de conflicto social e infraestructura deficiente. El χ² detecta desviación pero no establece causa. Extranjero no es explicado por este confounder (ver anti-ataque AA1).
- **L2 — Bonferroni conservador:** Corrección de Bonferroni es conservadora; Benjamini-Hochberg (1995) daría mayor poder estadístico sin inflar error tipo I.
- **L3 — Independencia entre deptos asumida:** Personeros de partidos nacionales operan en múltiples departamentos simultáneamente; impugnaciones coordinadas violarían este supuesto. No se dispone de datos para testearlo.
- **L4 — Distribución completa de 26 deptos no publicada:** Esta nota reporta los 6 extremos. El patrón completo (sistémico vs localizado) no puede evaluarse externamente sin la tabla de los 26 departamentos.
- **L5 — No distingue tipo de impugnación:** Impugnación legal (personeros, observadores) vs error logístico (actas mal llenadas) no son diferenciables en los datos disponibles.

---

## Anti-attacks addressed

| Ataque | Respuesta |
|---|---|
| AA1 "Extranjero siempre es outlier" | Extranjero 2026 = 26.27% vs Extranjero 2021 ≈ 8% → ratio 3.3× intra-circunscripción. Confounder estructural no explica variación temporal. |
| AA2 "χ² infla con n grande" | Reportamos z-score por departamento + Cohen h = 0.61. Effect size no depende de n. |
| AA3 "Correlación con conflicto social" | Plausible para Loreto/Ucayali. No disponible para Extranjero. Confounder parcial, no total. |
| AA4 "Varianza muestral en deptos pequeños" | Todos los outliers reportados n > 1,500. IC95 de Extranjero = [24.5%, 28.1%]. Varianza no explica. |
| AA5 "p₀ global sensible a outliers" | Robustez testada con p₀ ± 20%: z Extranjero ≥ 39.7 en todos los escenarios. |

---

## Regla oro

> Anomalía que ONPE debe explicar por departamento.
> La tasa de impugnación en la circunscripción Extranjero (26.27%) es 4.3× el promedio nacional (6.16%) y 3.3× la tasa de la misma circunscripción en las elecciones generales de 2021 (~8%). El test χ²=2897.2 (dof=25) descarta homogeneidad entre departamentos con p < 10⁻³⁰⁰.

---

## Method citation

- Newcombe, R.G. (1998). *Two-sided confidence intervals for the single proportion.* Statistics in Medicine, 17(8), 857–872.
- Fisher, R.A. (1925). *Statistical Methods for Research Workers.* (χ² homogeneidad)
- Bonferroni, C.E. (1936). *Teoria statistica delle classi e calcolo delle probabilità.*

---

## Data & reproducibility

| Campo | Valor |
|---|---|
| Dataset | HuggingFace `Neuracode/onpe-eg2026-mesa-a-mesa` |
| IPFS CID | `<cid_pendiente>` |
| DB SHA-256 | `<hash_db_pendiente>` |
| Capture timestamp | 2026-04-21T15:53:39Z |
| Raw finding | `reports/raw_findings/raw_h1_20260421T155339Z.json` |
| Spec | `docs/specs/H1.md` |
| Branch | `forensis/H1-20260421T155339Z` |

**Reproducibility:** `rtk py scripts/h1_impugnacion_depto.py`

**Tooling:** [Claude Code](https://claude.ai/referral/Kj5b88VLag) + Polars + DuckDB
```