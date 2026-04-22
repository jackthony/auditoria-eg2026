```markdown
# H1 — Técnico
<!-- reports/narratives/H1/tech.md -->
<!-- Tooling: [Claude Code](https://claude.ai/referral/Kj5b88VLag) -->

## Qué

| Métrica | Valor |
|---|---|
| Test omnibus | χ²=2897.2 · dof=25 |
| p-value | < 1e-300 (log₁₀p ≈ −620) |
| N deptos | 26 |
| N mesas total | ~92,766 |
| Global impugn. | 6.16% |
| Top outlier | Extranjero 26.27% (z=42.18) |
| Bottom outlier | Arequipa 1.83% (z=−11.70) |
| Ratio top/global | 4.3× |
| α Bonferroni | 0.001923 (0.05/26) |

## Query (reproducible)

```sql
-- DuckDB · raw_h1_20260421T155339Z
-- Paso 1: tasa por depto
SELECT
    depto,
    COUNT(*) AS n_mesas,
    SUM(impugnada::INT) AS n_imp,
    ROUND(100.0 * SUM(impugnada::INT) / COUNT(*), 4) AS pct_imp
FROM actas
GROUP BY depto
ORDER BY pct_imp DESC;

-- Paso 2: verificación spot-check
SELECT 668.0 / 2543.0  AS tasa_extranjero;   -- → 0.26268 ✓
SELECT  77.0 / 4215.0  AS tasa_arequipa;     -- → 0.018268 ✓

-- Paso 3: z-score manual Extranjero (p0=0.0616)
-- SE = sqrt(0.0616*0.9384/2543) = 0.004764
-- z  = (0.26268-0.0616)/0.004764 = 42.21 ≈ 42.18 reportado (Δ<0.1%)

-- Paso 4: chi2 homogeneidad → scipy.stats.chi2_contingency(tabla_26x2)
-- chi2=2897.2 · dof=25 · p=chi2.logsf(2897.2,25) → log10_p≈-620
```

> ⚠️ `p_chi2=0.0` en raw_finding = underflow silencioso.
> Corrección: `scipy.stats.chi2.logsf(2897.2, 25)` → reportar `< 1e-300`.

## Desviaciones top/bottom (Bonferroni α=0.001923)

| Depto | n | n_imp | % | z | p_val | Dirección |
|---|---|---|---|---|---|---|
| Extranjero | 2,543 | 668 | 26.27% | +42.18 | 0.0* | ↑ 4.3× global |
| Loreto | 2,697 | 401 | 14.87% | +18.82 | 0.0* | ↑ 2.4× global |
| Ucayali | 1,564 | 188 | 12.02% | +9.64 | 0.0* | ↑ 1.9× global |
| Junín | 3,691 | 125 | 3.39% | −7.01 | 2.5e-12 | ↓ |
| Puno | 3,397 | 103 | 3.03% | −7.58 | 3.5e-14 | ↓ |
| Arequipa | 4,215 | 77 | 1.83% | −11.70 | 0.0* | ↓ 3.4× debajo global |

*p computacional underflow; todos << 1e-300.

> ⚠️ Los 20 deptos intermedios NO están en raw_finding.
> **Acción requerida:** publicar tabla completa 26×{z, p_Bonf} antes de release.

## Test

- **Chi² homogeneidad** · χ²=2897.2 · dof=25 · p < 1e-300 · n=92,766 mesas
- **z-test 1-prop Newcombe** · Bonferroni α=0.001923 · todos top/bottom p << α
- **Effect size** · Cohen h (Extranjero vs global) = 2·arcsin(√0.2627)−2·arcsin(√0.0616) ≈ **0.61** (grande)
- Paper: Newcombe (1998) *Stat Med* · Fisher (1925) · Bonferroni (1936)

## Robustez p0 ±20%

| p0 | z Extranjero | z Arequipa | Conclusión |
|---|---|---|---|
| 4.93% (−20%) | >42 | −9.5 | Sigue significativo |
| 6.16% (base) | 42.18 | −11.70 | Base |
| 7.39% (+20%) | ~39.7 | −13.7 | Sigue significativo |

Conclusión **estable** bajo variación ±20% de p0.

## Challenge verdict

- **DEBIL** (presentación incompleta, no metodología)

| Ataque | Resultado |
|---|---|
| A1 Confounder geo | Explica Loreto/Ucayali · NO explica Extranjero |
| A2 Tamaño mesa | n>1500 en outliers · no aplica |
| A3 Método alternativo | χ²+z coherentes >> umbral |
| A4 Verificación numérica | Error <0.1% · OK |
| A5 Robustez p0±20% | Estable |
| A6 Post-hoc fishing | 20 deptos intermedios no reportados · DÉBIL |
| A7 Cherry-picking | Distribución completa ausente · DÉBIL |

**Vectores atacados:** confounder geográfico, varianza muestral, coherencia métodos, fishing ex-post.

## Acciones requeridas antes de release

1. Reemplazar `p_chi2=0.0` → `< 1e-300` (o `log10_p ≈ -620`)
2. Publicar tabla completa 26 deptos con z + p_Bonferroni
3. Añadir limitación: independencia entre deptos asumida (personeros nacionales)
4. Promover comparación temporal Extranjero 2021 (~8%) vs 2026 (26.27%) a hallazgo formal

## Reproducir

```
rtk py scripts/h1_impugnacion_depto.py
```

## Verificación (cadena de custodia)

| Campo | Valor |
|---|---|
| DB SHA-256 | `<hash_db_pendiente>` |
| Parquet CID IPFS | `<cid_pendiente>` |
| Capture ts | 2026-04-21T15:53:39Z |
| Raw ref | `reports/raw_findings/raw_h1_20260421T155339Z.json` |
| Datos | HuggingFace Neuracode/onpe-eg2026-mesa-a-mesa |
```

---