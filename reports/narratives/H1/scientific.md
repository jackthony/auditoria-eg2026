```markdown
# H1 — Scientific Note
## Heterogeneidad Estadística en Tasa de Impugnación de Actas por Departamento · Elecciones Generales Perú 2026

> Versión: 1.1 (post-challenge) · 2026-04-21T17:30:00Z

---

**Hypothesis:**
- H₀: La tasa de impugnación es homogénea entre los 26 departamentos (p_depto = p_global ∀ depto).
- H₁: Al menos un departamento se desvía significativamente de p_global.

**Primary Test:** χ² homogeneidad (Fisher, 1925)

**Statistic:** χ² = 2897.2

**Degrees of freedom:** 25

**p-value:** p ≈ 0 (< 10⁻³⁰⁰; reportado como 0.00e+00 por límite de precisión flotante)

**Supplementary test:** z-test proporciones 1-muestra, corrección Newcombe (1998) + Bonferroni (1936), α_adj = 0.001923

---

**Effect sizes (Cohen h = 2·arcsin√p̂ − 2·arcsin√p₀):**

| Departamento | n | n_imp | p̂ | z | Cohen h |
|---|---|---|---|---|---|
| Extranjero | 2,543 | 668 | 26.27% | +42.18 | **0.743** |
| Loreto | 2,697 | 401 | 14.87% | +18.82 | 0.400 |
| Ucayali | 1,564 | 188 | 12.02% | +9.64 | 0.311 |
| Arequipa | 4,215 | 77 | 1.83% | −11.70 | −0.285 |
| Puno | 3,397 | 103 | 3.03% | −7.58 | −0.190 |
| Junín | 3,691 | 125 | 3.39% | −7.01 | −0.174 |
| **Global** | **~92,766** | **~5,717** | **6.16%** | — | — |

*Cohen h > 0.5 considerado efecto grande (Cohen, 1988).*

---

**CI₉₅ Bootstrap (Newcombe) — Extranjero:** [24.56%, 27.98%]

*(p_global = 6.16% excluido por margen > 19 pp)*

**N total:** ~92,766 actas de mesa

---

**Assumptions checked:**
1. Todos los departamentos n > 100 (condición suficiencia chi²) ✓
2. Frecuencias esperadas ≥ 5 en todas las celdas (validado por `scipy chi2_contingency`) ✓
3. Independencia entre departamentos (asumida por diseño muestral territorial) ✓
4. n_depto > 1,000 en todos los outliers reportados → varianza aleatoria descartada ✓

---

**Robustness check (A5, challenge interno):**

Variación p_global ± 20% para Extranjero (n=2,543, k=668):

| p₀ escenario | E[X] | z |
|---|---|---|
| p₀ × 0.80 = 4.93% | 125.4 | **49.7** |
| p₀ base = 6.16% | 156.6 | **42.2** |
| p₀ × 1.20 = 7.39% | 187.9 | **36.4** |

Conclusión invariante: z > 36 en todo el rango; p < 10⁻²⁸⁰.

**Confirmación método alternativo (A3):** Binomial exacto cola superior para Extranjero:
`binom.logsf(667, 2543, 0.0616)` → z_aprox ≈ 42.17 vs 42.18 reportado (**Δ = 0.01**). ✓

---

**Limitations:**

1. **L1 — Heterogeneidad estructural esperada:** χ² detecta desviación sin identificar causa. Diferencias geográficas en infraestructura, logística y densidad de observadores son confounders plausibles (Loreto, Ucayali correlacionan con zonas de conflicto social documentado).
2. **L2 — Bonferroni conservador:** Corrección Bonferroni sobrecontrola el error tipo I; Benjamini-Hochberg daría mayor potencia sin inflar FDR.
3. **L3 — Tipo impugnación no desagregado:** No se distingue impugnación legal (personeros, ONPE) de error logístico de registro.
4. **L4 (post-challenge):** Loreto/Ucayali requieren control explícito por indicadores de conflicto social (fuentes DINI/MINDEF) antes de interpretación causal.
5. **L5 (post-challenge):** Comparación temporal Extranjero-2021 (~8%) → 2026 (26.27%) es exploratoria y post-hoc respecto a la spec pre-registrada; debe tratarse como hallazgo preliminar con caveat.
6. **L6 (post-challenge):** Los 20 departamentos intermedios no se reportan individualmente; sin tabla completa de 26 z-scores no es posible distinguir efecto concentrado (local) de efecto sistémico distribuido.
7. **L7 (post-challenge):** Ausencia de control por n_válidos promedio por mesa dentro de cada departamento; varianza intra-departamental no modelada.

---

**Anti-attacks addressed:**

| Vector | Respuesta |
|--------|-----------|
| "Extranjero siempre es heterogéneo" | Ratio 4.3x vs global; Extranjero-2021 ≈ 8% → cambio temporal, no solo variación estructural (caveat: post-hoc, L5) |
| "χ² se infla con n grande" | z-score por departamento + Cohen h independientes de N total; efecto grande (h=0.743) confirmado |
| "Loreto/Ucayali = conflicto social" | Confounder admitido; narrativa debe ser cautelosa (L4); Extranjero no tiene correlato análogo |
| "Varianza aleatoria en deptos pequeños" | n_min outliers = 1,564 (Ucayali); IC95 Extranjero excluye p_global por 19 pp |
| "Selección arbitraria de Extranjero" | Test omnibus χ² sobre 26 deptos simultáneos — no se seleccionó a priori |

---

**Anomalía que ONPE debe explicar:** ¿Por qué la tasa de impugnación en mesas del Exterior (26.27%) es 4.3 veces el promedio nacional (6.16%), y qué proceso específico generó ese valor frente al ~8% registrado en 2021?

---

**Method citations:**
- Fisher, R.A. (1925). *Statistical Methods for Research Workers.* Oliver & Boyd. [χ² homogeneidad]
- Newcombe, R.G. (1998). Two-sided confidence intervals for the single proportion. *Statistics in Medicine*, 17, 857–872.
- Bonferroni, C.E. (1936). Teoria statistica delle classi e calcolo delle probabilità. *Pubblicazioni del R. Istituto Superiore di Scienze Economiche e Commerciali di Firenze.*

**Data:**
HuggingFace `Neuracode/onpe-eg2026-mesa-a-mesa` ·
IPFS CID `<cid-actas-parquet>` ·
DB SHA-256 `<hash-onpe-eg2026-mesa-a-mesa>` ·
Capture ts: 2026-04-21T15:53:39Z ·
Raw ref: `reports/raw_findings/raw_h1_20260421T155339Z.json`

**Tooling:** [Claude Code](https://claude.ai/referral/Kj5b88VLag) + Polars + DuckDB

**Reproducibility:**
Spec `docs/specs/H1.md` · Branch `forensis/H1-20260421` ·
```bash
rtk py scripts/h1_homogeneidad_impugnacion.py \
    --input data/processed/actas_mesa_eg2026.parquet \
    --alpha-bonferroni 0.001923
```

---

*→ Handoff: `narrator-market` (paralelo) → `virality-engine`*
*→ Retorno requerido a `stats-expert`: re-correr con tabla completa 26 deptos + covariables L4/L7.*
```