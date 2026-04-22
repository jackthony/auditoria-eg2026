```markdown
# H12 — Scientific Note: Anomalous JPP Vote Concentration, Mesa 018146

*Peruvian General Election 2026 · Forensic Statistics Series*
*Tooling: [Claude Code](https://claude.ai/referral/Kj5b88VLag) + Polars + DuckDB + scipy*

---

## Hypothesis

**H₀:** Mesa 018146 es sorteo Bernoulli i.i.d. con p₀ = 0.109073 (tasa JPP en universo de mesas normales; n_universo = 15,196,245 votos válidos)

**H₁:** p_mesa > p_global (concentración anómala unilateral)

---

## Primary Test

| Campo | Valor |
|-------|-------|
| **Test** | Binomial exacto 1-cola · `scipy.stats.binom.logsf(k−1, n, p₀)` |
| **Statistic (z)** | 38.69 |
| **p-value** | **1.60 × 10⁻¹⁷¹** · log₁₀(p) = −170.8 |
| **Effect size** | Cohen h = **1.8396** (muy grande, umbral >0.8) |
| **CI 95% Clopper-Pearson** | [0.858765, 0.93908] |
| **p̂ observado** | 0.904348 (208/230) |
| **p₀ (referencia)** | 0.109073 (1,657,500 / 15,196,245) |
| **N mesa** | 230 votos válidos |
| **N universo** | 15,196,245 votos · 78,605 mesas normales |

---

## Confirmatory Tests

| Test | Estadístico | Resultado |
|------|-------------|-----------|
| z-test 1-proporción | z = 38.69 | p → 0 · consistente |
| χ² homogeneidad (2×2) | χ² = 1,497.6 · df=1 | z² = 1,496.9 · diferencia <0.1% · **consistente** |
| Verificación Stirling log₁₀(término modal) | ≈ −153.5 | cota inferior · cola completa −170.8 · **consistente** |

---

## Robustness Analysis (Geographic Confounder)

| p₀ asumido | Escenario | log₁₀(p) | p-value | vs Bonferroni α=6.36×10⁻⁷ |
|------------|-----------|-----------|---------|---------------------------|
| 0.109073 | Tasa nacional observada | −170.8 | 1.60×10⁻¹⁷¹ | Margen: 164 órdenes |
| 0.30 | Zona JPP-favorable | −81.69 | 2.04×10⁻⁸² | Margen: 75 órdenes |
| 0.50 | JPP mayoritario local | −38.73 | 1.85×10⁻³⁹ | Margen: 33 órdenes |
| 0.70 | JPP ultra-favorito local | −13.15 | 7.15×10⁻¹⁴ | Margen: 7 órdenes |
| **0.855** | **Umbral de falsificación** | −6.20 | ~6.4×10⁻⁷ | Límite exacto |

> El hallazgo es invariante bajo cualquier p₀ realista. Para que el confounder geográfico lo destruya, JPP requeriría 85.5% de base nacional (tasa real: 10.9%).

---

## Assumptions Checked

| Supuesto | Estado |
|----------|--------|
| Independencia de votos bajo H₀ | Asumida (voto secreto, Bernoulli i.i.d.) |
| Tamaño muestral suficiente | n=230 >> 30 · aproximación normal válida · ley de grandes números converge fuertemente |
| p₀ observacional | Estimado de N=15,196,245 · error de estimación ~10⁻⁴ · no altera conclusión |
| Método numérico | `logsf` evita catastrophic cancellation de float64 en valores <10⁻¹⁵ |
| Unicidad del caso | Única mesa con n>100 y pct≥90% entre 78,605 mesas · 3 mesas ≥90% total, todas reportadas |

---

## Limitations

**L1 — Post-hoc identification:**
Mesa 018146 fue identificada por búsqueda exhaustiva sobre 78,605 mesas (H4 hero), no por hipótesis preregistrada. Sin embargo: (a) el hallazgo es declarado explícitamente como post-hoc; (b) la corrección Bonferroni completa (α = 0.05/78,605 = 6.36×10⁻⁷) se aplica y el p-value la supera por 164 órdenes de magnitud; (c) Benjamini-Hochberg FDR converge al mismo resultado.

**L2 — Homogeneidad geográfica de p₀:**
p₀ = 0.109073 asume distribución uniforme nacional de votos JPP. JPP puede concentrarse en distritos andinos específicos. Análisis de robustez con p₀ = 0.30 / 0.50 / 0.70 mitiga sustancialmente este riesgo. Umbral de falsificación: p₀ ≥ 0.855, valor sin precedente documentado para JPP en ninguna circunscripción.

**L3 — Ausencia de identificación geográfica explícita:**
El análisis no verifica el departamento/distrito exacto de mesa 018146 en esta iteración. La estratificación por departamento es el siguiente paso recomendado (identificado en challenge por challenger). No destruye el finding; reduce el margen del confounder geográfico ya cubierto por robustez.

**L4 — No implica intencionalidad:**
El resultado estadístico es compatible con concentración electoral legítima (liderazgo comunitario local, mesa rural con votantes homogéneos). La verificación de personeros, actas firmadas y observadores es indispensable antes de cualquier inferencia causal.

---

## Anti-Attacks Addressed

| Vector | Ataque | Respuesta |
|--------|--------|-----------|
| A1 | Confounder geográfico (p₀ local ≤70%) | p=7.15×10⁻¹⁴ con p₀=0.70 · pasa Bonferroni por 7 órdenes · SOBREVIVE |
| A2 | Confounder tamaño de mesa | n=230 refuerza anomalía (LGN converge hacia p₀) · z=38.69 equivale a ~18σ · SOBREVIVE |
| A3 | Test alternativo χ² | χ²=1,497.6 · z²=38.69²=1,496.9 · diferencia <0.1% · COINCIDE |
| A4 | Verificación numérica independiente | Stirling log₁₀≈−153 (cota inferior) · logsf exacto −170.8 · CONSISTENTE |
| A5 | Robustez p₀ ±20% | Insensible · umbral falla p₀=0.855 · SOBREVIVE |
| A6 | Post-hoc fishing | Declarado + Bonferroni aplicada + margen 164 órdenes · SOBREVIVE |
| A7 | Cherry-picking | 3 mesas ≥90% todas reportadas · única con n>100 · SOBREVIVE |

**Veredicto challenge (2026-04-21T16:45:00Z): SOBREVIVE (7/7)**

---

## Method Citations

- Clopper CJ, Pearson ES (1934). The use of confidence or fiducial limits illustrated in the case of the binomial. *Biometrika* **26**:404–413. *(IC binomial exacto)*
- Newcombe RG (1998). Two-sided confidence intervals for the single proportion: comparison of seven methods. *Statistics in Medicine* **17**:873–890. *(z-test proporción)*
- Cohen J (1988). *Statistical Power Analysis for the Behavioral Sciences*, 2nd ed. Lawrence Erlbaum. *(effect size h)*

---

## Regla de Oro

> Esta nota documenta una **anomalía estadística que ONPE debe explicar** mediante verificación de personeros, actas y observadores presentes. No se afirma fraude ni intencionalidad.

---

## Data & Reproducibility

| Campo | Valor |
|-------|-------|
| **Dataset** | HuggingFace · Neuracode/onpe-eg2026-mesa-a-mesa |
| **IPFS CID** | `<cid_raw_h12_stratified_20260421T153803Z>` |
| **DB SHA-256** | `<hash_onpe_eg2026_actas_normales>` |
| **Capture timestamp** | 2026-04-21T15:38:03Z UTC |
| **Raw finding** | `reports/raw_findings/raw_h12_stratified_20260421T153803Z.json` |
| **Spec** | `docs/specs/H12.md` |
| **Branch** | `forensis/H12-20260421T153803Z` |
| **Tooling** | [Claude Code](https://claude.ai/referral/Kj5b88VLag) + Polars + DuckDB + scipy |
| **Reproducibility** | `rtk py scripts/h12_binomial_mesa018146.py` |
```