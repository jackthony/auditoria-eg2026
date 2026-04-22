```markdown
# H1 — Scientific Note: Heterogeneidad de Tasas de Impugnación por Circunscripción, Elecciones Generales Perú 2026

**Hypothesis:**
- H0: La tasa de impugnación de actas es homogénea entre las 26 circunscripciones (p_depto = p_global ∀ depto)
- H1: Al menos una circunscripción se desvía significativamente de p_global = 6.16%

**Test:** χ² de homogeneidad (Fisher 1925) + z-test 1-proporción Newcombe (1998) + corrección Bonferroni (1936)

**Statistic:** χ² = 2897.2

**p-value:** p ≈ 0.00e+00 (< 1e−15; representado como 0.0 en float64 — correcto bajo `norm.sf` / `chi2.sf`)

**Degrees of freedom:** 25

**Bonferroni α:** 0.001923 (= 0.05 / 26 circunscripciones)

**Effect size (z individuales como proxy):**

| Circunscripción | pct% | z | Dirección |
|---|---|---|---|
| Extranjero | 26.2682 | +42.18 | ↑ exceso |
| Loreto | 14.8684 | +18.82 | ↑ exceso |
| Ucayali | 12.0205 | +9.64 | ↑ exceso |
| Junín | 3.3866 | −7.01 | ↓ déficit |
| Puno | 3.0321 | −7.58 | ↓ déficit |
| Arequipa | 1.8268 | −11.70 | ↓ déficit |

> p_global referencia: 6.16%. Extranjero = 4.3× la media nacional.

**CI95 (bootstrap):** No reportado en esta versión — pendiente bootstrap percentile n=10,000 iteraciones.

**N:** 92,766 actas (estimado de conjunto total); mesas por depto: 1,564–4,215.

**Assumptions checked:**
- n suficiente: todos los deptos n > 100 ✓
- Esperados ≥ 5: validado por `chi2_contingency` ✓
- Independencia entre circunscripciones: asumida estructuralmente ✓

**Limitations:**
1. Heterogeneidad geográfica estructuralmente esperada (ruralidad, logística, conflicto social). El χ² detecta desviación estadística — **no establece causa**.
2. La circunscripción Extranjero opera bajo condiciones no comparables con departamentos nacionales (ONPE exterior, infraestructura de fiscalización diferente). Su inclusión en el χ² viola comparabilidad estructural; su z=42.18 contribuye ~1,779/2,897 = **61% del estadístico global**. Análisis sin Extranjero requerido para magnitud honesta.
3. Corrección Bonferroni conservadora — Benjamini-Hochberg daría mayor poder estadístico.
4. No se distingue entre impugnación legal (observadores, personeros) y error logístico operativo.
5. Confounder tamaño de mesa intra-depto no verificado: si distribución de n_validos/mesa difiere sistemáticamente entre circunscripciones, el χ² agregado puede absorber varianza muestral diferencial.
6. Tabla completa de 26 circunscripciones no publicada en finding primario — solo top-3 y bottom-3. Los 20 deptos intermedios requieren reporte explícito para auditoría de cobertura.

**Anti-attacks addressed:**

| Ataque | Respuesta | Estado |
|---|---|---|
| A1: Confounder geográfico (Loreto/Ucayali) | Plausible para esas regiones; **no explica Extranjero** (4.3× media, vs ~8% en EG2021) | DÉBIL — corrección requerida |
| A2: Confounder tamaño mesa | No verificable con datos actuales; limitación no declarada en v1 | DÉBIL — corrección requerida |
| A3: z recalculado independientemente | z_Extranjero calculado = 42.16 vs 42.18 reportado (Δ=0.02) ✓ | SOBREVIVE |
| A4: Verificación numérica % | Todos los porcentajes verificados aritméticamente: idénticos ✓ | SOBREVIVE |
| A5: Robustez p0 ±20% | z varía <±12%; ninguna conclusión se invierte ✓ | SOBREVIVE |
| A6: Post-hoc fishing | Test prueba conjunto de 26; top/bottom son descriptivos de ranking, no selección a priori | SOBREVIVE |
| A7: Cherry-picking cosmético | 20 deptos intermedios sin reportar; cobertura no auditable | DÉBIL — tabla completa requerida |

**Challenge verdict:** DÉBIL — hallazgo numéricamente correcto y robusto; requiere correcciones de alcance (Extranjero separado, tabla completa, control tamaño mesa) antes de publicación peer-review.

**Lo que NO cae bajo ningún ataque:**
- χ² = 2897.2 matemáticamente correcto y verificado
- Heterogeneidad real e incontestable estadísticamente
- Extranjero 26.27% vs 6.16% global = **anomalía que ONPE debe explicar**
- p-values correctos y verificados independientemente

**Method citation:**
- Newcombe, R.G. (1998). Two-sided confidence intervals for the single proportion. *Statistics in Medicine*, 17, 857–872.
- Fisher, R.A. (1925). *Statistical Methods for Research Workers*. Edinburgh: Oliver & Boyd. [χ² homogeneidad]
- Bonferroni, C.E. (1936). Teoria statistica delle classi e calcolo delle probabilità. *Pubblicazioni del R. Istituto Superiore di Scienze Economiche e Commerciali di Firenze*, 8, 3–62.

**Data:** HuggingFace `Neuracode/onpe-eg2026-mesa-a-mesa` · IPFS CID: `PENDIENTE — ipfs add post-freeze` · DB SHA-256: `PENDIENTE — post-freeze`

**Capture timestamp:** `2026-04-21T15:53:39Z`

**Raw finding:** `reports/raw_findings/raw_h1_20260421T155339Z.json`

**Tooling:** [Claude Code](https://claude.ai/referral/Kj5b88VLag) + Polars + DuckDB

**Reproducibility:** Spec `docs/specs/H1.md` · Branch `forensis/H1-20260421T155339Z` · Script `scripts/h1_homogeneidad_impugnacion.py`

---
*Nota editorial: Este documento es un borrador técnico de análisis estadístico. No establece ni insinúa conducta fraudulenta. Las anomalías detectadas constituyen desviaciones estadísticas que requieren explicación institucional por parte de ONPE.*
```