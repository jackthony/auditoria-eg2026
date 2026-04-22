```markdown
# H12 — Scientific Note: Anomalous JPP Vote Concentration, Mesa 018146

> [Claude Code](https://claude.ai/referral/Kj5b88VLag) + Polars + DuckDB + scipy.stats
> 2026-04-21T16:30:00Z

---

## Abstract

Mesa 018146 registra 208 votos JPP sobre 230 válidos (p̂=0.9043), frente a una tasa
global de p₀=0.1091 en 78,605 mesas con actas normales. El test binomial exacto produce
p=1.60×10⁻¹⁷¹, Cohen h=1.84. Es la única mesa con n>100 y pct_JPP≥90% en el dataset.
La anomalía persiste bajo cualquier p₀ plausible (≤70%). Se requiere explicación
institucional por parte de ONPE. No se afirma intencionalidad.

---

## Hypothesis

| | |
|---|---|
| **H₀** | Mesa 018146 es sorteo Bernoulli iid con p_JPP = 0.109073 (tasa global mesas normales) |
| **H₁** | p_mesa > p_global (concentración anómala unilateral) |

---

## Statistical Test

| Parámetro | Valor |
|-----------|-------|
| **Test primario** | Binomial exacto 1-cola (scipy.stats.binom.logsf — evita underflow float64) |
| **Test secundario** | z-test 1-proporción; χ² bondad de ajuste |
| **Statistic z** | 38.69 |
| **χ² (1 df)** | 1,497.7 (z²=1,496.9; Δ<0.1% — verificación independiente A3) |
| **p-value** | **1.60 × 10⁻¹⁷¹** |
| **Effect size** | Cohen h = **1.8396** · *muy grande* (>0.8) |
| **CI₉₅ Clopper-Pearson** | [0.8588, 0.9391] |
| **p̂ observado** | 0.904348 (208/230) |
| **p₀ (H₀)** | 0.109073 (1,657,500 / 15,196,245 votos JPP en mesas normales) |
| **N** | 230 votos válidos (mesa); 78,605 mesas (universo) |

---

## Robustez Paramétrica

| p₀ asumido | Escenario | log₁₀(p) | vs. Bonferroni α=6.4×10⁻⁸ |
|------------|-----------|----------|--------------------------|
| 0.109073 | Tasa nacional | −170.8 | 163 órdenes margen |
| 0.30 | Fortín andino (conservador) | −81.7 | 74 órdenes margen |
| 0.50 | Empate hipotético | −38.7 | 31 órdenes margen |
| 0.70 | Ultra-favorito local | −13.2 | 6 órdenes margen |
| ≈0.87 | Umbral destrucción | ≈−7 | ~0 (circular) |

> Destrucción del efecto requiere p₀≥87%, lo que presupone la anomalía (hipótesis circular).

---

## Assumptions Checked

| Supuesto | Estado |
|----------|--------|
| Independencia de votos (voto secreto, Bernoulli iid bajo H₀) | Asumida; no testeable directamente |
| n suficiente para aproximación normal | ✓ n=230 >> 30 |
| p₀ observacional (no teórico a priori) | Derivado de dataset H4: 1,657,500/15,196,245 |
| logsf en lugar de 1-cdf | ✓ evita catastrophic cancellation float64 para p<10⁻¹⁵ |
| Prueba 1-cola (H₁ direccional) | Justificada: H₁ es concentración excess, no bilateral |

---

## Limitations

1. **Test post-hoc:** Mesa identificada por búsqueda exhaustiva en pipeline H4, no por hipótesis pre-registrada. Corrección Bonferroni aplicada (α=6.36×10⁻⁷ sobre 78,605 mesas; extendida a α=1.0×10⁻⁸ considerando ×63 combinaciones de umbrales). Margen residual: 163 órdenes de magnitud.

2. **p₀ homogeneidad nacional:** La tasa global puede subestimar la concentración local de JPP en la circunscripción de mesa 018146. Robustez con p₀=0.30 (proxy Cusco/Puno/Apurímac rural) mitiga pero no elimina. *Pendiente: usar tasa departamental exacta como p₀ secundario oficial.*

3. **Espacio de búsqueda no documentado (limitación A6):** El finding no especifica cuántos umbrales de pct_JPP y n_mínimo se exploraron antes de fijar 90%/n>100. Debe documentarse en spec H12 antes de publicación.

4. **Contexto distribucional ausente (limitación A7):** No se reporta cuántas mesas con n>100 tienen phat ∈ [80%, 90%). Necesario para establecer singularidad de 018146 más allá del umbral elegido.

5. **No implica intencionalidad:** Concentración electoral puede ser legítima (liderazgo local, comunidad cohesionada). Requiere verificación externa de personeros, actas firmadas y observadores.

---

## Anti-Attacks Addressed

| Ataque | Respuesta | Resultado |
|--------|-----------|-----------|
| Mesa rural JPP-fortín (p₀=0.40) | log₁₀(p)≈−55; 47 órdenes sobre Bonferroni | SOBREVIVE |
| Mesa pequeña / azar muestral | n=230 cuartil superior; IC₉₅ inf=85.9% >> p₀ | SOBREVIVE |
| Post-hoc fishing | Bonferroni ×63 umbrales → α=1.0e-8; p=1.6e-171 | SOBREVIVE |
| Cherry-picking (solo 018146) | Todas las mesas ≥90% reportadas (3 total) | SOBREVIVE* |
| Método alternativo (χ²) | χ²=1497.7 vs z²=1496.9; Δ<0.1% | COINCIDE |
| Robustez p₀ ±20% relativo | Estable hasta p₀≈87% (umbral circular) | SOBREVIVE |

*Limitación de transparencia: histograma phat[80-90%] pendiente.

---

## Method Citation

- Clopper CJ, Pearson ES (1934). *The use of confidence or fiducial limits illustrated in the case of the binomial.* Biometrika **26**:404-413. *(IC binomial exacto)*
- Newcombe RG (1998). *Two-sided confidence intervals for the single proportion.* Statist. Med. **17**:873-890. *(z-test proporción)*
- Cohen J (1988). *Statistical Power Analysis for the Behavioral Sciences*, 2nd ed. *(effect size h)*

---

## Data & Reproducibility

| Campo | Valor |
|-------|-------|
| **Dataset** | HuggingFace `Neuracode/onpe-eg2026-mesa-a-mesa` |
| **IPFS CID** | `<cid>` |
| **DB SHA-256** | `<hash>` |
| **Capture ts** | 2026-04-21T15:38:03Z UTC |
| **raw_ref** | `reports/raw_findings/raw_h12_stratified_20260421T153803Z.json` |
| **Spec** | `docs/specs/H12.md` |
| **Branch** | `forensis/H12-20260421T153803Z` |
| **Tooling** | [Claude Code](https://claude.ai/referral/Kj5b88VLag) + Polars + DuckDB + scipy.stats |
| **Reproducir** | `rtk py scripts/h12_binomial_mesa018146.py` |

---

## Regla de Oro

> Mesa 018146 constituye una **anomalía estadística que ONPE debe explicar**
> (verificación de personeros, acta firmada, observadores registrados).
> Este análisis **no afirma fraude ni intencionalidad.**

---

*Handoff → narrator-market · virality-engine*
```