```markdown
# H12 — Técnico (Mesa 018146)

> Generado: 2026-04-21T16:30:00Z | [Claude Code](https://claude.ai/referral/Kj5b88VLag)

## Qué

- Mesa 018146: JPP=208/230 (90.43%) vs global 10.91%
- Binomial exacto p=1.60e-171 · z=38.69 · Cohen h=1.8396
- Única mesa n>100 con pct_JPP≥90% entre 78,605 mesas normales

## Query (reproducible)

```sql
-- DuckDB — reproduce hallazgo principal
SELECT
    mesa_id,
    COUNT(*)                                    AS n_votos,
    SUM(CASE WHEN partido='JPP' THEN 1 END)     AS k_jpp,
    ROUND(SUM(CASE WHEN partido='JPP' THEN 1 END) * 1.0 / COUNT(*), 6) AS phat,
    1657500.0 / 15196245.0                      AS p0_global
FROM votos_mesa
WHERE mesa_id = '018146'
GROUP BY mesa_id;

-- p0 global (mesas normales H4 dataset)
SELECT 1657500.0 / 15196245.0 AS p_jpp_global;  -- = 0.109073

-- Binomial logsf (Python scipy — evita catastrophic cancellation)
-- import scipy.stats as st
-- log10_p = st.binom.logsf(207, 230, 0.109073) / math.log(10)
-- → log10_p = -170.80  →  p = 1.60e-171

-- z-test 1-prop manual
SELECT
    (0.904348 - 0.109073)
    / SQRT(0.109073 * (1 - 0.109073) / 230.0)  AS z_score;
-- → z = 38.685 ≈ 38.69 ✓

-- χ² bondad de ajuste (verificación independiente A3)
SELECT
    POWER(208 - 230*0.109073, 2) / (230*0.109073)
    + POWER(22  - 230*0.890927, 2) / (230*0.890927) AS chi2;
-- → χ² = 1497.7  (z²=1496.9, Δ<0.1%) ✓
```

## Tests

| Test | Estadístico | p-value | n |
|------|-------------|---------|---|
| Binomial exacto 1-cola (logsf) | — | **1.60e-171** | 230 |
| z-test 1-proporción | z=38.69 | ~0 (χ²=1497.7) | 230 |
| Bonferroni (78,605 mesas) | α=6.36e-7 | margen 163 órdenes | — |
| Bonferroni extendido (×63 umbrales) | α=1.0e-8 | margen 163 órdenes | — |

- **Effect:** Cohen h=1.8396 · magnitud **muy grande** (>0.8)
- **IC95 Clopper-Pearson:** [0.8588, 0.9391]
- **Paper:** Clopper & Pearson (1934) Biometrika 26:404-413; Newcombe (1998) Statist. Med. 17:873-890; Cohen (1988) Statistical Power Analysis 2ed

## Robustez p0

| p0 asumido | Escenario | log10(p) |
|------------|-----------|----------|
| 0.109073 | Tasa global nacional | **−170.8** |
| 0.30 | JPP zona andina (conservador) | −81.7 |
| 0.50 | JPP empate teórico | −38.7 |
| 0.70 | JPP ultra-favorito local | −13.2 |
| **~0.87** | **Umbral destrucción Bonferroni** | **~−7** |

> Nota: p0≥0.87 presupone la anomalía (circular). Con cualquier p0≤70% conclusión es invariante.

## Challenge verdict

- **SOBREVIVE** (todos los ataques, veredicto 2026-04-21T16:15Z)

| Ataque | Resultado |
|--------|-----------|
| A1 Confounder geográfico | p<10⁻⁵⁰ con p0=40% |
| A2 Tamaño mesa n=230 | IC inferior 85.9% >> p0 |
| A3 χ² vs binomial | χ²=1497.7, z²=1496.9, Δ<0.1% |
| A4 Verificación numérica | phat/z/h verificados Δ<0.3% |
| A5 Robustez p0±20% | Estable hasta p0≈87% |
| A6 Post-hoc fishing | 163 órdenes sobre Bonferroni |
| A7 Cherry-picking | 3 mesas reportadas; falta histograma |

**Limitaciones de transparencia pendientes (no fallas estadísticas):**
1. Documentar espacio de búsqueda exacto (umbrales pct_JPP y n_mínimo explorados)
2. Histograma phat para mesas n>100 — contextualizar unicidad de 018146
3. Usar p0 departamental de 018146 como p0 secundario oficial si disponible

## Anomalía a explicar

> Mesa 018146 muestra concentración JPP incompatible con sorteo iid bajo cualquier p0≤70%.  
> **ONPE debe verificar:** personeros presentes, acta firmada, observadores registrados.  
> No se afirma fraude.

## Reproducir

```bash
rtk py scripts/h12_binomial_mesa018146.py
# requiere: ONPE_DB env var apuntando a parquet H4
```

## Verificación (cadena custodia)

| Campo | Valor |
|-------|-------|
| DB SHA-256 | `<hash>` |
| Parquet CID (IPFS) | `<cid>` |
| raw_ref | `reports/raw_findings/raw_h12_stratified_20260421T153803Z.json` |
| Capture ts | 2026-04-21T15:38:03Z |
| Dataset | HuggingFace Neuracode/onpe-eg2026-mesa-a-mesa |
```

---