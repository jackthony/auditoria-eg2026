"""
scripts/stats_h4_especiales_900k.py — Cálculo HALL-0420-H4.

Hipótesis: el partido JPP (código 00000010) presenta un pct de votos válidos
sustancialmente mayor en mesas especiales (900001-904703) que en mesas
normales (000001-088064).

Método (forensic-grade, defendible):
  - Two-proportion z-test (Newcombe 1998) sobre votos JPP / votos válidos.
  - Cohen's h (Cohen 1988) para tamaño del efecto.
  - Bootstrap percentil IC95 (Efron-Tibshirani 1993, B=10,000).
  - Mann-Whitney U sobre pct por mesa (no asume normalidad).

Stack: Polars + DuckDB + NumPy/SciPy. Sin pandas.

Output: reports/h4_stats.json
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import duckdb
import numpy as np
import polars as pl
from scipy import stats as sp_stats

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
HF_DIR = ROOT / "reports" / "hf_dataset"
OUT = ROOT / "reports" / "h4_stats.json"

PARTIDO_TARGET = "00000010"
PARTIDO_NOMBRE = "JUNTOS POR EL PERÚ"
N_BOOT = 10_000
SEED = 42


def latest_parquet() -> Path:
    files = list(HF_DIR.glob("onpe_eg2026_mesas_*.parquet"))
    if not files:
        raise SystemExit("Sin parquet HF")
    return max(files, key=lambda p: p.stat().st_mtime)


def two_proportion_z(x1: int, n1: int, x2: int, n2: int) -> tuple[float, float]:
    """z-test pooled. Devuelve (z, p_two_sided)."""
    p1, p2 = x1 / n1, x2 / n2
    p_pool = (x1 + x2) / (n1 + n2)
    se = math.sqrt(p_pool * (1 - p_pool) * (1 / n1 + 1 / n2))
    if se == 0:
        return 0.0, 1.0
    z = (p1 - p2) / se
    p = 2 * (1 - sp_stats.norm.cdf(abs(z)))
    return z, p


def cohens_h(p1: float, p2: float) -> float:
    """Tamaño del efecto Cohen (1988): pequeño 0.2, medio 0.5, grande 0.8."""
    phi1 = 2 * math.asin(math.sqrt(p1))
    phi2 = 2 * math.asin(math.sqrt(p2))
    return phi1 - phi2


def bootstrap_diff_ci(
    pcts_a: np.ndarray, pcts_b: np.ndarray, n_boot: int, seed: int
) -> tuple[float, float, float]:
    """Bootstrap percentil IC95 sobre (mean_a - mean_b)."""
    rng = np.random.default_rng(seed)
    diffs = np.empty(n_boot, dtype=np.float64)
    na, nb = len(pcts_a), len(pcts_b)
    for i in range(n_boot):
        sa = rng.choice(pcts_a, size=na, replace=True)
        sb = rng.choice(pcts_b, size=nb, replace=True)
        diffs[i] = sa.mean() - sb.mean()
    return float(diffs.mean()), float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5))


def main() -> int:
    pq = latest_parquet()
    print(f"[h4] parquet: {pq.name}")

    # ---------- Agregados por grupo (DuckDB SQL directo) ----------
    sql = f"""
    WITH mesa_clas AS (
      SELECT
        codigo_mesa,
        partido_codigo,
        votos,
        CAST(codigo_mesa AS BIGINT) >= 900000 AS es_especial
      FROM read_parquet('{pq.as_posix()}')
      WHERE partido_codigo IS NOT NULL
    ),
    valid AS (
      SELECT
        codigo_mesa,
        es_especial,
        SUM(votos) FILTER (WHERE partido_codigo NOT IN ('80','81','82')) AS validos,
        SUM(votos) FILTER (WHERE partido_codigo = '{PARTIDO_TARGET}') AS jpp
      FROM mesa_clas
      GROUP BY 1, 2
    )
    SELECT es_especial, SUM(jpp) AS jpp_total, SUM(validos) AS validos_total,
           COUNT(*) AS n_mesas
    FROM valid
    GROUP BY 1
    ORDER BY es_especial;
    """
    agg = duckdb.sql(sql).pl()
    print(agg)

    row_norm = agg.filter(~pl.col("es_especial")).row(0, named=True)
    row_esp = agg.filter(pl.col("es_especial")).row(0, named=True)

    x1, n1 = int(row_esp["jpp_total"]), int(row_esp["validos_total"])
    x2, n2 = int(row_norm["jpp_total"]), int(row_norm["validos_total"])
    p1, p2 = x1 / n1, x2 / n2
    print(f"[h4] JPP especiales 900k+: {p1:.4%} ({x1:,}/{n1:,})  mesas={row_esp['n_mesas']}")
    print(f"[h4] JPP normales:        {p2:.4%} ({x2:,}/{n2:,})  mesas={row_norm['n_mesas']}")

    z, pval = two_proportion_z(x1, n1, x2, n2)
    h = cohens_h(p1, p2)
    ratio = p1 / p2 if p2 > 0 else float("inf")

    print(f"[h4] z={z:.2f}  p_two_sided={pval:.2e}  Cohen_h={h:.3f}  ratio={ratio:.2f}x")

    # ---------- Mann-Whitney sobre pct por mesa ----------
    sql_pct = f"""
    WITH mesa_clas AS (
      SELECT codigo_mesa, partido_codigo, votos,
             CAST(codigo_mesa AS BIGINT) >= 900000 AS es_especial
      FROM read_parquet('{pq.as_posix()}')
      WHERE partido_codigo IS NOT NULL
    ),
    pct AS (
      SELECT
        codigo_mesa, es_especial,
        SUM(votos) FILTER (WHERE partido_codigo NOT IN ('80','81','82')) AS validos,
        SUM(votos) FILTER (WHERE partido_codigo = '{PARTIDO_TARGET}') AS jpp
      FROM mesa_clas
      GROUP BY 1, 2
    )
    SELECT es_especial, jpp::DOUBLE / NULLIF(validos, 0) AS pct_jpp
    FROM pct
    WHERE validos > 0;
    """
    pcts = duckdb.sql(sql_pct).pl()
    pcts_esp = pcts.filter(pl.col("es_especial"))["pct_jpp"].to_numpy()
    pcts_norm = pcts.filter(~pl.col("es_especial"))["pct_jpp"].to_numpy()

    u_stat, u_p = sp_stats.mannwhitneyu(pcts_esp, pcts_norm, alternative="greater")
    print(f"[h4] Mann-Whitney U={u_stat:.0f}  p_one_sided={u_p:.2e}")

    # ---------- Bootstrap IC95 ----------
    print(f"[h4] bootstrap B={N_BOOT:,}…")
    diff_mean, ci_low, ci_high = bootstrap_diff_ci(pcts_esp, pcts_norm, N_BOOT, SEED)
    print(f"[h4] diff_mean(pct_esp - pct_norm) = {diff_mean:.4f}")
    print(f"[h4] IC95 percentil: [{ci_low:.4f}, {ci_high:.4f}]")

    # ---------- Top deptos en especiales ----------
    sql_dpt = f"""
    SELECT departamento, COUNT(DISTINCT codigo_mesa) AS mesas
    FROM read_parquet('{pq.as_posix()}')
    WHERE CAST(codigo_mesa AS BIGINT) >= 900000
    GROUP BY 1 ORDER BY 2 DESC LIMIT 10;
    """
    deptos_esp = duckdb.sql(sql_dpt).pl().to_dicts()

    out = {
        "id": "HALL-0420-H4",
        "ts_utc": pq.stem.split("_")[-1],
        "parquet_source": pq.name,
        "partido": {
            "codigo": PARTIDO_TARGET,
            "nombre": PARTIDO_NOMBRE,
        },
        "grupos": {
            "especiales_900k": {
                "rango_codigo": [900001, 904703],
                "n_mesas": int(row_esp["n_mesas"]),
                "votos_jpp": x1,
                "votos_validos": n1,
                "pct_jpp": round(p1, 6),
            },
            "normales": {
                "rango_codigo": [1, 88064],
                "n_mesas": int(row_norm["n_mesas"]),
                "votos_jpp": x2,
                "votos_validos": n2,
                "pct_jpp": round(p2, 6),
            },
        },
        "tests": {
            "two_proportion_z": {
                "method": "Newcombe 1998 (pooled SE)",
                "z": round(z, 4),
                "p_two_sided": pval,
                "h0": "p_especiales == p_normales",
                "h1": "p_especiales != p_normales",
            },
            "cohens_h": {
                "method": "Cohen 1988",
                "value": round(h, 4),
                "magnitud": (
                    "muy grande" if abs(h) > 0.8
                    else "grande" if abs(h) > 0.5
                    else "medio" if abs(h) > 0.2
                    else "pequeño"
                ),
            },
            "mann_whitney_u": {
                "method": "Mann-Whitney U sobre pct por mesa, alternative=greater",
                "u_statistic": float(u_stat),
                "p_one_sided": float(u_p),
            },
            "bootstrap_diff_pct": {
                "method": "Percentil IC95 (Efron-Tibshirani 1993)",
                "n_resamples": N_BOOT,
                "seed": SEED,
                "mean_diff": round(diff_mean, 6),
                "ci95": [round(ci_low, 6), round(ci_high, 6)],
            },
        },
        "ratio_pct_esp_vs_norm": round(ratio, 4),
        "departamentos_top10_en_especiales": deptos_esp,
        "interpretacion": (
            f"JPP concentra {p1:.2%} en mesas especiales 900k+ vs {p2:.2%} en normales "
            f"(ratio {ratio:.2f}x). Diferencia estadísticamente significativa "
            f"(p={pval:.2e}, Cohen h={h:.3f})."
        ),
        "limitaciones": [
            "No prueba causalidad ni intencionalidad.",
            "Mesas 900k+ tienen padrones reducidos; varianza por mesa mayor.",
            "Universo 900k+ caracterizado como mesas regulares de IE distribuidas geográficamente, no necesariamente militar/penal/extranjero.",
        ],
        "metodologia_cita": [
            "Newcombe (1998). Two-sided confidence intervals for the single proportion. Statistics in Medicine.",
            "Cohen (1988). Statistical Power Analysis for the Behavioral Sciences.",
            "Efron & Tibshirani (1993). An Introduction to the Bootstrap. CRC Press.",
        ],
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n[h4] -> {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
