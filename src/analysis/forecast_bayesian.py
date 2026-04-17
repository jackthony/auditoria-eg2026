"""Proyección bayesiana jerárquica del margen final Sánchez vs López Aliaga.

Metodología basada en:
- Linzer, D. (2013) "Dynamic Bayesian Forecasting of Presidential Elections
  in the States", Journal of the American Statistical Association.
- Cohn, N. (NYT) — "The Upshot" Election Needle methodology.
- AP Elections Research — Race Call protocol.
- Gelman & Hill (2007) "Data Analysis Using Regression and
  Multilevel/Hierarchical Models", Cambridge University Press.

Modelo:
  Para cada región r y cada simulación m:
    1. share_r ~ Dirichlet(alpha_r)
       donde alpha_r = votos actuales por candidato en la región r.
       Esto da la distribución posterior del share regional, asumiendo
       que las actas ya contadas son una muestra representativa del total
       regional (supuesto MCAR-within-region, estándar en election-night).

    2. integration_rate_r ~ Beta(a, b)
       Tasa a la que las actas impugnadas/pendientes de la región r se
       resuelven e integran al conteo (vs se anulan). Parametrizamos
       tres escenarios:
         - Pesimista (anti-Sánchez): Beta(2, 5)  → media ≈ 0.29
         - Central:                  Beta(5, 5)  → media ≈ 0.50
         - Optimista (pro-Sánchez):  Beta(5, 2)  → media ≈ 0.71

    3. votos_pendientes_r = actas_fuera_r × vv_por_acta_r × integration_rate_r
       votos_por_candidato_r = votos_pendientes_r × share_r

    4. Agregar a nivel nacional y computar margen final.

Output:
  - P(RLA > Sánchez) = probabilidad posterior de cruce.
  - Distribución del margen final (p5, p25, p50, p75, p95).
  - Regiones pivote (las que más mueven el margen en varianza).
  - Resultados por escenario (pesimista/central/optimista).

Uso:
    py src/analysis/forecast_bayesian.py

Salida:
    reports/forecast.json  (para dashboard + PDF)
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "reports" / "forecast.json"

# Reproducibilidad: misma seed siempre.
RNG = np.random.default_rng(seed=20260417)

N_SIM = 10_000

SCENARIOS = {
    "pesimista": (2.0, 5.0),
    "central": (5.0, 5.0),
    "optimista": (5.0, 2.0),
}

CANDIDATES = ["fuji_v", "rla_v", "nieto_v", "belm_v", "sanch_v"]
CAND_NAMES = ["Fujimori", "López Aliaga", "Nieto", "Belmont", "Sánchez"]


def simulate(reg: pd.DataFrame, beta_a: float, beta_b: float, n_sim: int = N_SIM):
    """Corre n_sim simulaciones del modelo jerárquico y devuelve el margen
    final Sánchez − RLA en cada simulación, más los votos totales agregados."""
    n_reg = len(reg)

    # Dirichlet alpha = votos actuales por candidato + prior débil (+1 smoothing).
    alphas = reg[CANDIDATES].to_numpy(dtype=float) + 1.0  # (n_reg, 5)

    # Votos válidos por acta en cada región (estimador de la región).
    vv_acta = (reg["vv"] / reg["contabilizadas"]).to_numpy()
    actas_fuera = (reg["enviadasJee"] + reg["pendientes_calc"]).to_numpy()

    # Muestrear shares regionales: shape (n_sim, n_reg, 5).
    shares = np.zeros((n_sim, n_reg, 5))
    for r in range(n_reg):
        shares[:, r, :] = RNG.dirichlet(alphas[r], size=n_sim)

    # Muestrear integration_rate por región y simulación: (n_sim, n_reg).
    integration = RNG.beta(beta_a, beta_b, size=(n_sim, n_reg))

    # Votos que entran al conteo por región y simulación.
    votos_fuera = actas_fuera * vv_acta  # (n_reg,)
    votos_entran = integration * votos_fuera  # (n_sim, n_reg)

    # Votos por candidato = votos_entran × share por candidato.
    # shape: (n_sim, n_reg, 5) × (n_sim, n_reg, 1) → (n_sim, n_reg, 5)
    votos_cand = shares * votos_entran[:, :, None]

    # Agregar a nivel nacional: (n_sim, 5)
    votos_cand_tot = votos_cand.sum(axis=1)

    # Votos actuales (los ya contados) a nivel nacional.
    votos_actuales = reg[CANDIDATES].sum().to_numpy()

    # Votos finales simulados = actuales + pendientes integrados.
    votos_final = votos_actuales + votos_cand_tot  # (n_sim, 5)

    # Margen Sánchez − RLA.
    idx_sanch = CANDIDATES.index("sanch_v")
    idx_rla = CANDIDATES.index("rla_v")
    margen = votos_final[:, idx_sanch] - votos_final[:, idx_rla]

    return margen, votos_final


def quantile_summary(arr: np.ndarray) -> dict:
    return {
        "p5": float(np.percentile(arr, 5)),
        "p25": float(np.percentile(arr, 25)),
        "p50": float(np.percentile(arr, 50)),
        "p75": float(np.percentile(arr, 75)),
        "p95": float(np.percentile(arr, 95)),
        "mean": float(np.mean(arr)),
        "std": float(np.std(arr)),
    }


def pivote_analysis(reg: pd.DataFrame) -> list[dict]:
    """Identifica las regiones que más mueven el margen en el escenario
    central. Métrica: actas_fuera × vv_por_acta × |share_sanch − share_rla|."""
    vv_acta = reg["vv"] / reg["contabilizadas"]
    actas_fuera = reg["enviadasJee"] + reg["pendientes_calc"]
    votos_fuera = actas_fuera * vv_acta
    share_s = reg["sanch_v"] / reg["vv"]
    share_r = reg["rla_v"] / reg["vv"]
    delta = votos_fuera * (share_s - share_r)
    out = (
        pd.DataFrame({
            "region": reg["name"],
            "actas_fuera": actas_fuera.astype(int),
            "votos_fuera": votos_fuera.astype(int),
            "share_sanch": share_s.round(4),
            "share_rla": share_r.round(4),
            "delta_esperado": delta.round(0),
        })
        .assign(abs_delta=lambda d: d["delta_esperado"].abs())
        .sort_values("abs_delta", ascending=False)
        .drop(columns="abs_delta")
        .head(10)
    )
    return out.to_dict(orient="records")


def main():
    reg = pd.read_csv(ROOT / "data" / "processed" / "regiones.csv")

    margen_actual = int(reg["sanch_v"].sum() - reg["rla_v"].sum())

    results = {}
    for name, (a, b) in SCENARIOS.items():
        margen_sim, _ = simulate(reg, a, b)
        p_cruce = float((margen_sim < 0).mean())  # P(RLA > Sánchez)
        results[name] = {
            "beta_params": {"a": a, "b": b, "mean_integration": a / (a + b)},
            "p_rla_supera_sanchez": p_cruce,
            "p_sanchez_mantiene": 1 - p_cruce,
            "margen_final": quantile_summary(margen_sim),
        }

    # Escenario agregado: mezcla uniforme de los tres (máxima incertidumbre).
    margen_mix = []
    for a, b in SCENARIOS.values():
        m, _ = simulate(reg, a, b, n_sim=N_SIM // 3)
        margen_mix.append(m)
    margen_mix = np.concatenate(margen_mix)
    p_cruce_mix = float((margen_mix < 0).mean())

    # Histograma del margen (escenario central) para gráfico.
    margen_central, _ = simulate(reg, *SCENARIOS["central"])
    bins = np.linspace(margen_central.min(), margen_central.max(), 41)
    counts, edges = np.histogram(margen_central, bins=bins)
    hist = [
        {"center": float((edges[i] + edges[i + 1]) / 2), "count": int(counts[i])}
        for i in range(len(counts))
    ]

    out = {
        "methodology": {
            "model": "Bayesian hierarchical Dirichlet-Multinomial with Beta prior on JEE integration rate",
            "references": [
                "Linzer, D. (2013) JASA — Dynamic Bayesian Forecasting of Presidential Elections",
                "Cohn, N. (NYT) — Election Needle methodology",
                "Gelman & Hill (2007) — Multilevel Hierarchical Models",
                "AP Elections Research — Race Call protocol",
            ],
            "n_simulations": N_SIM,
            "seed": 20260417,
        },
        "estado_actual": {
            "sanchez": int(reg["sanch_v"].sum()),
            "rla": int(reg["rla_v"].sum()),
            "margen": margen_actual,
            "actas_fuera": int((reg["enviadasJee"] + reg["pendientes_calc"]).sum()),
            "votos_fuera_estimado": int(((reg["enviadasJee"] + reg["pendientes_calc"]) * reg["vv"] / reg["contabilizadas"]).sum()),
        },
        "escenarios": results,
        "escenario_mixto": {
            "descripcion": "Mezcla uniforme de pesimista/central/optimista (máxima incertidumbre sobre tasa JEE)",
            "p_rla_supera_sanchez": p_cruce_mix,
            "p_sanchez_mantiene": 1 - p_cruce_mix,
            "margen_final": quantile_summary(margen_mix),
        },
        "regiones_pivote": pivote_analysis(reg),
        "histograma_central": hist,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK: {OUT}")
    print(f"Margen actual: {margen_actual:+,} (Sánchez - RLA)")
    print(f"P(RLA supera Sánchez):")
    for k, v in results.items():
        print(f"  {k:10s}: {v['p_rla_supera_sanchez']:.1%}  (margen p50={v['margen_final']['p50']:+,.0f})")
    print(f"  mixto     : {p_cruce_mix:.1%}")


if __name__ == "__main__":
    main()
