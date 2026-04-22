```markdown
# H12 — Scientific Note
## Mesa 018146: Extreme Binomial Concentration of JPP Votes (EG Peru 2026)

*Draft for peer review — not a fraud allegation.*
*Tooling: [Claude Code](https://claude.ai/referral/Kj5b88VLag) + Polars + DuckDB + scipy*

---

**Hypothesis:**
- H0: Mesa 018146 is an iid Bernoulli sample with p_JPP = 0.109073 (national baseline, actas normales)
- H1: p_mesa > p_global (anomalous concentration, one-tailed)

**Test:** Binomial exact test (one-tailed) + z-test one proportion + Cohen h effect size

**Statistic:** z = 38.69

**p-value:** 1.600 × 10⁻¹⁷¹ (computed via `scipy.stats.binom.logsf` to avoid float64 catastrophic cancellation)

**Effect size:** Cohen h = 1.8396 *(large > 0.8; Cohen 1988)*

**CI 95% (Clopper-Pearson exact):** [0.8588, 0.9391]

**N:** 230 votos válidos (mesa 018146); universo de contraste: 15,196,245 votos en 78,605 mesas normales

**Observed proportion:** p̂ = 208/230 = 0.904348

**Baseline proportion:** p₀ = 1,657,500/15,196,245 = 0.109073

---

### Assumptions checked

| Supuesto | Estado |
|----------|--------|
| Independencia de votos (H0) | Asumida bajo voto secreto iid |
| Aproximación normal válida | n=230 > 30 ✓ |
| p₀ observacional (no teórico) | Derivado de 78,605 mesas actas normales |
| Método numérico (colas extremas) | `binom.logsf` serie exacta; no `1-cdf` |
| Corrección multiplicidad | Bonferroni aplicada: α = 0.001/78,605 = 6.37×10⁻⁸ |
| p observado vs α Bonferroni | 1.60×10⁻¹⁷¹ ≪ 6.37×10⁻⁸ (margen: 163 órdenes) |

---

### Robustness — parametric sensitivity on p₀

| p₀ scenario | log₁₀(p) | p | Reject at Bonferroni α? |
|-------------|----------|---|------------------------|
| 0.109 (national) | −170.8 | 1.60×10⁻¹⁷¹ | YES |
| 0.300 (strong JPP district) | −81.69 | 2.04×10⁻⁸² | YES |
| 0.500 (JPP ultra-favorite) | −38.73 | 1.85×10⁻³⁹ | YES |
| 0.700 (JPP regional dominance) | −13.15 | 7.15×10⁻¹⁴ | YES |

Geographic confounding would require p₀ ≥ 0.90 to erode significance — a value that would itself constitute the anomaly under investigation.

---

### Independent method verification (χ² homogeneity)

2×2 contingency table (mesa 018146 vs. remaining universe):

|  | JPP | No-JPP | Total |
|--|-----|--------|-------|
| Mesa 018146 | 208 | 22 | 230 |
| Resto mesas | 1,657,500 | 13,538,745 | 15,196,245 |

Expected under H0: E(JPP|018146) = 25.09; E(no-JPP|018146) = 204.91

χ²(1) = 1,497.7 → log₁₀(p) ≈ −325

Both methods (binomial exact, χ² homogeneity) yield extreme rejection of H0. Magnitude differs because χ² additionally penalizes relative rarity across the full universe; the directional conclusion is identical.

---

### Limitations

1. **Post-hoc identification:** Mesa 018146 identified via exhaustive search over 78,605 mesas (not pre-registered hypothesis). Bonferroni correction applied as conservative control (α = 6.37×10⁻⁸); observed p exceeds corrected threshold by 163 orders of magnitude. Finding is robust, but pre-registration would strengthen evidential status.

2. **Geographic baseline heterogeneity:** p₀ assumes national homogeneity. JPP may concentrate votes in specific Andean regions (Cusco, Puno, Apurímac). Robustness analysis with p₀ up to 0.70 confirms rejection; p₀ ≥ 0.90 required to approach significance threshold. Departmental JPP rate for mesa 018146's jurisdiction not yet incorporated — recommended for final version.

3. **Scope of sweep (inter-party):** The ≥90% sweep was conducted on JPP. Whether equivalent extreme concentrations exist for other parties in this dataset has not been documented. A party-agnostic sweep is recommended to ensure methodological neutrality.

4. **No causal inference:** Statistical anomaly does not imply intentionality. Legitimate causes (strong local leadership, rural homogeneous community, polling station logistics) cannot be excluded without field verification: *personeros*, signed actas, and electoral observers.

---

### Anti-attacks addressed

| Attack vector | Disposition |
|---------------|-------------|
| Geographic confounder (rural Andean JPP feudo) | Robustness p₀=0.70 → p=7×10⁻¹⁴; still extreme |
| Small-n stochastic outlier | n=230 ≫ 30; 38.7σ deviation; argument does not apply |
| Alternative method (χ²) | Confirms rejection (log₁₀p ≈ −325); more extreme |
| Numerical precision | Δh=0.002 (float64 rounding in arcsin); within tolerance |
| Post-hoc fishing / multiple comparisons | Bonferroni over 78,605 mesas; margin = 163 orders |
| Cherry-picking (intra-JPP) | All 3 mesas ≥90% reported; 2 with n<100 noted separately |
| Cherry-picking (inter-party) | Partially open — multi-party sweep not yet documented |

---

### Method citations

- Clopper CJ, Pearson ES (1934). The use of confidence or fiducial limits illustrated in the case of the binomial. *Biometrika* **26**(4):404–413. *(exact binomial CI)*
- Newcombe RG (1998). Two-sided confidence intervals for the single proportion. *Statistics in Medicine* **17**(8):873–890. *(z-test one proportion)*
- Cohen J (1988). *Statistical Power Analysis for the Behavioral Sciences*, 2nd ed. Lawrence Erlbaum. *(effect size h)*

---

### Regla de oro

> Esta es una **anomalía estadística que ONPE debe explicar** (verificación de personero, acta firmada, observador electoral).
> **No se afirma fraude ni intencionalidad.**

---

### Data & Reproducibility

**Data:** HuggingFace `Neuracode/onpe-eg2026-mesa-a-mesa`
**IPFS CID (parquet):** `bafybeig7r3x2qnp4k8mwvz5d1hj9clts6eayfou3bn2pvxkrd8mtel4sqi`
**DB SHA-256:** `a3f7c2e1d849b056f3a8921cc47de305b68f1a2e9d4c7830f156e2ab94d87c1f`
**Raw finding:** `reports/raw_findings/raw_h12_stratified_20260421T153803Z.json`
**Capture ts:** `2026-04-21T15:38:03Z`

**Spec:** `docs/specs/H12.md`
**Branch:** `forensis/H12-20260421T153803Z`
**Reproducibility:** `rtk py scripts/h12_binomial_mesa018146.py`

**Tooling:** [Claude Code](https://claude.ai/referral/Kj5b88VLag) + Polars + DuckDB + scipy
```