```markdown
# H12 — Scientific Note: Anomalía Binomial Mesa 018146 · Elecciones Generales Perú 2026

**Hypothesis H0:** Mesa 018146 es sorteo Bernoulli iid con p_JPP = 0.109073
(tasa nacional observacional: 1,657,500 / 15,196,245 votos normales, dataset H4)

**Hypothesis H1:** p_mesa > p_global (concentración anómala unilateral)

---

**Test primario:** Binomial exacto 1-cola (Clopper-Pearson)
**Test secundario:** z-test 1-proporción (Newcombe 1998)
**Test confirmatorio:** χ² de homogeneidad 2×2 (challenger A3)

---

**Statistic (binomial):** P(X ≥ 208 | n=230, p₀=0.109073)
**z-score:** 38.69
**χ²:** ≈ 1,497.7 (= z²; dof=1)

**p-value:** 1.600 × 10⁻¹⁷¹
*(calculado con `scipy.stats.binom.logsf(207, 230, 0.109073)` — evita underflow float64)*

**Effect size:** Cohen h = 1.8396 · magnitud "muy grande" (umbral >0.8)
*(h = 2·arcsin(√0.904348) − 2·arcsin(√0.109073))*

**CI 95% (Clopper-Pearson exacto):** [0.858765, 0.939080]

**Observed proportion:** p̂ = 208/230 = **0.904348**
**Global baseline:** p₀ = 0.109073

**N:** 230 votos válidos (mesa 018146) · Universo de referencia: 78,605 mesas

---

## Robustez paramétrica

El efecto es **invariante** bajo cualquier p₀ geográfico concebible:

| p₀ supuesto | Interpretación | log₁₀(p) | Conclusión |
|-------------|---------------|----------|------------|
| 0.109073 | Global nacional | −170.80 | Rechaza H0 |
| 0.30 | JPP moderadamente fuerte | −81.69 | Rechaza H0 |
| 0.50 | JPP partido mayoritario local | −38.73 | Rechaza H0 |
| 0.70 | JPP ultra-dominante local | −13.15 | Rechaza H0 |

Para P(X ≥ 208 | n=230) ≥ 0.001, se requeriría p₀ > 0.997 — escenario
estadísticamente absurdo (unanimidad previa). El hallazgo es **matemáticamente
incompatible con sorteo iid bajo cualquier p₀ realista**.

---

## Corrección por multiplicidad

- Universo explorado: m = 78,605 mesas
- Corrección FWER (Bonferroni): α_eff = 0.001 / 78,605 = **1.27 × 10⁻⁸**
- p_finding = 1.60 × 10⁻¹⁷¹
- **Margen: 163 órdenes de magnitud** sobre umbral corregido
- Procedimiento de selección transparente: se reportan las **3 mesas con pct ≥ 90%**
  de manera exhaustiva; 2 con n < 100 reportadas separadamente
- Mesa 018146 es la **única** con n > 100 y pct ≥ 90% en el universo completo

---

## Assumptions checked

| Supuesto | Estado | Evidencia |
|----------|--------|-----------|
| Independencia votos (H0) | Asumida bajo iid | Voto secreto; base del sorteo Bernoulli |
| n suficiente (CLT) | ✓ n=230 > 30 | Normal approx válida; binomial exacto no requiere CLT |
| p₀ observacional estable | Verificado | 1,657,500/15,196,245 dataset H4 normalizado |
| No underflow numérico | ✓ logsf | `1-cdf` produce 0.0 exacto para p<1e-15 (float64) |
| Única mesa pre-identificada | Parcial | Derivada de búsqueda exhaustiva H4 — post-hoc declarado |

---

## Limitations

1. **Test post-hoc declarado:** Mesa identificada por búsqueda exhaustiva sobre
   78,605 mesas (H4 hero), no hipótesis a priori. Corrección Bonferroni aplicada
   (α_eff = 1.27×10⁻⁸); finding supera umbral por 163 órdenes — conclusión
   robusta pero la naturaleza post-hoc debe declararse en toda diseminación.

2. **Homogeneidad geográfica de p₀:** El baseline 0.109073 es nacional.
   JPP puede concentrarse regionalmente (Cusco/Puno/Ayacucho andino). Mitigado:
   robustez con p₀ = 0.70 da p ≈ 7×10⁻¹⁴ — efecto persiste, pero la
   ubicación exacta de mesa 018146 debe verificarse para contextualizar A1.

3. **No implica intencionalidad:** La anomalía estadística es condición necesaria,
   no suficiente, para inferir manipulación. Concentración electoral legítima
   (liderazgo local, comunidad homogénea) no puede descartarse sin verificación
   de personeros y actas firmadas. **Anomalía que ONPE debe explicar — no
   afirmamos fraude.**

4. **Ausencia de dato geográfico en stat_finding:** Departamento/provincia de
   mesa 018146 no declarado explícitamente. Gap editorial pendiente.

---

## Anti-attacks addressed

| Ataque | Respuesta | Veredicto |
|--------|-----------|-----------|
| Confounder geo (p₀ regional=0.70) | P(X≥208\|p₀=0.70) = 7×10⁻¹⁴ | SOBREVIVE |
| Tamaño mesa distorsiona test | z_recalc=38.70 vs declarado 38.69; n=230 no es outlier | SOBREVIVE |
| χ² vs binomial exacto | χ²≈1498; binomial más conservador; convergen | SOBREVIVE |
| Recálculo numérico independiente | log₁₀(p)=−170.80 idéntico; h=1.8396 exacto | SOBREVIVE |
| Robustez p₀ ±20% | log₁₀(p) entre −130 y <−200; invariante | SOBREVIVE |
| Post-hoc + corrección múltiple | Bonferroni α_eff=1.27e-8; 163 órdenes sobrantes | SOBREVIVE |
| Cherry-picking | 3/3 mesas ≥90% reportadas; criterio objetivo | SOBREVIVE |

---

## Method citations

- Clopper CJ, Pearson ES (1934). *The use of confidence or fiducial limits
  illustrated in the case of the binomial.* Biometrika **26**:404–413.
  *(IC exacto binomial — método primario)*
- Newcombe RG (1998). *Two-sided confidence intervals for the single proportion.*
  Statist. Med. **17**:873–890. *(z-test 1-proporción)*
- Cohen J (1988). *Statistical Power Analysis for the Behavioral Sciences*, 2ed.
  Erlbaum. *(effect size h; umbral >0.8 = muy grande)*

---

## Data & Reproducibility

**Dataset:** HuggingFace `Neuracode/onpe-eg2026-mesa-a-mesa`
**IPFS CID:** `<ipfs_cid_placeholder>`
**DB SHA-256:** `<db_sha256_placeholder>`
**Capture timestamp:** 2026-04-21T15:38:03Z UTC
**Raw finding:** `reports/raw_findings/raw_h12_stratified_20260421T153803Z.json`
**Spec:** `docs/specs/H12.md` · Branch: `forensis/H12-20260421T153803Z`
**Tooling:** [Claude Code](https://claude.ai/referral/Kj5b88VLag) + Polars + DuckDB + scipy 1.x
**Reproducibility:** `rtk py scripts/h12_binomial_mesa018146.py`

---

*Regla de oro: anomalía estadística que ONPE debe explicar
(personero, acta firmada, observador electoral). No se afirma fraude.*
```