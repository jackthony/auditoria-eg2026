```markdown
# H1 — Técnico: Heterogeneidad de Tasas de Impugnación por Departamento

## Qué
- χ²=2897.2 · dof=25 · p≈0 · 26 circunscripciones · tasa global 6.16%
- Top outlier: Extranjero 26.27% (z=42.18) · 4.3× media
- Bottom outlier: Arequipa 1.83% (z=−11.70)

## Query (reproducible)
```sql
-- DuckDB · DB SHA-256: PENDIENTE_HASH · Parquet CID: PENDIENTE_CID
SELECT
    depto,
    COUNT(*)                                         AS n_mesas,
    SUM(impugnada::INT)                              AS n_imp,
    ROUND(100.0 * SUM(impugnada::INT) / COUNT(*), 4) AS pct_imp,
    -- z-score Newcombe 1-prop vs p_global=0.0616
    ROUND(
        (SUM(impugnada::INT)::FLOAT / COUNT(*) - 0.0616)
        / SQRT(0.0616 * 0.9384 / COUNT(*)),
        2
    )                                                AS z_newcombe
FROM onpe_mesas
GROUP BY depto
ORDER BY pct_imp DESC;
```

## Test
- **χ² homogeneidad** · χ²=2897.2 · dof=25 · p=0.00e+00 · n=92,766 mesas
- **z-test 1-prop Newcombe** · Bonferroni α=0.001923 (0.05/26)
- Paper: Newcombe (1998) · Fisher (1925) χ² homogeneidad · Bonferroni (1936)
- Effect: No aplica Cohen h global; z individuales como proxy efecto

| Circunscripción | n | n_imp | pct% | z | p_raw |
|---|---|---|---|---|---|
| Extranjero | 2,543 | 668 | 26.2682 | +42.18 | 0.00e+00 |
| Loreto | 2,697 | 401 | 14.8684 | +18.82 | 0.00e+00 |
| Ucayali | 1,564 | 188 | 12.0205 | +9.64 | 0.00e+00 |
| Junín | 3,691 | 125 | 3.3866 | −7.01 | 2.47e−12 |
| Puno | 3,397 | 103 | 3.0321 | −7.58 | 3.46e−14 |
| Arequipa | 4,215 | 77 | 1.8268 | −11.70 | 0.00e+00 |

> ⚠️ Los 20 deptos intermedios no se listan arriba — tabla completa de 26 en `reports/raw_findings/raw_h1_20260421T155339Z.json`.

## Challenge verdict
- **DÉBIL** — hallazgo válido, requiere correcciones antes de audit-narrator
- Vectores atacados: A1 (confounder geográfico), A2 (tamaño mesa no verificable), A7 (tabla parcial)
- Vectores que SOBREVIVEN: A3 (método alternativo z≈42.16≈42.18 ✓), A4 (% verificados exactos ✓), A5 (robusto ±20% p0), A6 (no es post-hoc fishing)

### Correcciones requeridas (pre-publicación)
1. **Extranjero separado:** correr χ² con y sin Extranjero; sin él χ² pierde ~61% del estadístico (≈1118 vs 2897) — sigue significativo, magnitud más honesta.
2. **Tabla 26/26 obligatoria:** reportar z, p_raw, p_Bonferroni para todos los deptos.
3. **Control tamaño mesa:** distribución n_validos/mesa por depto para descartar A2.
4. **Limitación causal explícita:** Loreto/Ucayali tienen hipótesis estructural plausible; χ² no distingue causa.

## Reproducir
```
rtk py scripts/h1_homogeneidad_impugnacion.py
```

## Verificación
- DB SHA-256: `PENDIENTE — poblar tras freeze de datos`
- Parquet CID: `PENDIENTE — poblar tras ipfs add`
- Capture ts: `2026-04-21T15:53:39Z`
- Raw finding: `reports/raw_findings/raw_h1_20260421T155339Z.json`
- Spec: `docs/specs/H1.md` · Branch: `forensis/H1-20260421T155339Z`

---
*Análisis asistido por [Claude Code](https://claude.ai/referral/Kj5b88VLag) + Polars + DuckDB*
```

---