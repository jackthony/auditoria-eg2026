```markdown
# H1 — Técnico (Heterogeneidad Tasa Impugnación por Dpto)

> Generado: 2026-04-21T17:30:00Z · Branch: forensis/H1-20260421

## Qué
- χ²=2897.2, dof=25, p≈0 — 26 deptos no homogéneos
- Extranjero: 26.27% vs global 6.16% → ratio 4.3x, z=42.18
- Loreto: 14.87%, z=18.82 · Ucayali: 12.02%, z=9.64
- Bottom: Arequipa 1.83%, z=−11.70

## Query (reproducible)
```sql
-- χ² homogeneidad impugnación por departamento
SELECT
    departamento,
    COUNT(*)                          AS n_actas,
    SUM(CASE WHEN impugnada THEN 1 END) AS n_imp,
    ROUND(100.0 * SUM(CASE WHEN impugnada THEN 1 END) / COUNT(*), 4) AS pct_imp,
    ROUND(
        (SUM(CASE WHEN impugnada THEN 1 END)
         - COUNT(*) * (SELECT AVG(impugnada::INT) FROM actas_mesa))
        / SQRT(COUNT(*) * (SELECT AVG(impugnada::INT) FROM actas_mesa)
               * (1 - (SELECT AVG(impugnada::INT) FROM actas_mesa))),
    2) AS z_score
FROM actas_mesa
GROUP BY departamento
ORDER BY pct_imp DESC;
```

## Tests
| Test | Estadístico | p | n |
|------|-------------|---|---|
| χ² homogeneidad (Fisher 1925) | χ²=2897.2, dof=25 | 0.00e+00 | 92,766 mesas |
| z-test 1-prop Newcombe — Extranjero | z=42.18 | 0.00e+00 | 2,543 |
| z-test 1-prop Newcombe — Loreto | z=18.82 | 0.00e+00 | 2,697 |
| z-test 1-prop Newcombe — Ucayali | z=9.64 | 0.00e+00 | 1,564 |
| z-test 1-prop Newcombe — Arequipa | z=−11.70 | 0.00e+00 | 4,215 |
| Bonferroni α ajustado | α=0.001923 | — | 26 deptos |

- **Papers:** Newcombe (1998) · Fisher (1925, χ² homog.) · Bonferroni (1936)
- **Effect size (Extranjero vs global):** Cohen h = 2·arcsin(√0.2627) − 2·arcsin(√0.0616) ≈ **0.743** (grande)
- **IC95 Extranjero (Newcombe):** [26.27% ± 1.71%] = [24.56%, 27.98%] — global 6.16% excluido por >19 pp

## Challenge Verdict

**DÉBIL**

| Ataque | Resultado | Impacto en finding |
|--------|-----------|--------------------|
| A1 Confounder geográfico | ⚠️ Parcial | Loreto/Ucayali: narrativa cautelosa |
| A2 n_validos/mesa no controlado | ⚠️ Gap real | Nueva limitación L7 |
| A3 Binomial exacto alternativo | ✅ z=42.17 vs 42.18 ✓ | Extranjero sobrevive |
| A4 Verificación numérica | ✅ Exacto 4to decimal | Datos íntegros |
| A5 Robustez p0 ± 20% | ✅ z∈[36, 50] Extranjero | Conclusión invariante |
| A6 Comparación temporal 2021 | ⚠️ Post-hoc no pre-registrado | Nueva limitación L5 |
| A7 20 deptos intermedios omitidos | ⚠️ Gap transparencia | Nueva limitación L6 |

**Núcleo publicable:** χ² global + Extranjero z=42 tras añadir L4–L7.

**Limitaciones adicionales post-challenge:**
- **L4:** Loreto/Ucayali requieren control por índice conflicto social (DINI/MINDEF).
- **L5:** Comparación Extranjero-2021 (8% → 26.27%) = exploratoria/post-hoc — caveat explícito.
- **L6:** Publicar tabla completa 26 deptos con z-score individual.
- **L7:** Controlar n_validos promedio por mesa dentro de cada depto.

## Reproducir
```bash
rtk py scripts/h1_homogeneidad_impugnacion.py \
    --input data/processed/actas_mesa_eg2026.parquet \
    --output reports/raw_findings/raw_h1_20260421T155339Z.json \
    --alpha-bonferroni 0.001923
```

## Verificación cadena de custodia
| Item | Valor |
|------|-------|
| DB SHA-256 | `<hash-onpe-eg2026-mesa-a-mesa>` |
| Parquet CID IPFS | `<cid-actas-parquet>` |
| Raw finding ref | `reports/raw_findings/raw_h1_20260421T155339Z.json` |
| Capture timestamp | 2026-04-21T15:53:39Z |
| Branch | `forensis/H1-20260421` |

---

*Análisis asistido por [Claude Code](https://claude.ai/referral/Kj5b88VLag) + Polars + DuckDB*
*Datos: HuggingFace Neuracode/onpe-eg2026-mesa-a-mesa*
```

---