"""
src/analysis/benford.py

Test de Ley de Benford sobre primer dígito de votos.

IMPORTANTE — LIMITACIONES (documentadas en METHODOLOGY.md):
La Ley de Benford-1 produce falsos positivos/negativos en datos electorales
legítimos cuando la magnitud de los conteos no abarca varios órdenes de
magnitud (Deckert, Myagkov & Ordeshook 2011). Por eso este test se usa como
señal complementaria, nunca como evidencia única.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

BENFORD_EXPECTED = {d: np.log10(1 + 1/d) for d in range(1, 10)}


def first_digit(x: float) -> int | None:
    """Primer dígito significativo de un entero positivo."""
    if x is None or x <= 0 or np.isnan(x):
        return None
    s = str(int(x)).lstrip("0")
    return int(s[0]) if s else None


def benford_chi2(values: list[float]) -> dict:
    digits = [first_digit(v) for v in values]
    digits = [d for d in digits if d is not None]
    n = len(digits)
    if n < 30:
        return {"n": n, "sufficient": False}

    observed = {d: digits.count(d) for d in range(1, 10)}
    expected = {d: n * BENFORD_EXPECTED[d] for d in range(1, 10)}
    chi2 = sum((observed[d] - expected[d])**2 / expected[d] for d in range(1, 10))
    p_value = 1 - stats.chi2.cdf(chi2, df=8)

    return {
        "n": n,
        "sufficient": True,
        "chi2": chi2,
        "p_value": p_value,
        "conforms": p_value >= 0.05,
        "observed": observed,
        "expected": {d: round(expected[d], 2) for d in expected},
    }


def run(root: Path | None = None):
    ROOT = root or Path(__file__).resolve().parents[2]
    df = pd.read_csv(ROOT / "data/processed/regiones.csv")

    print("═" * 70)
    print(" C. LEY DE BENFORD — primer dígito de votos")
    print("═" * 70)
    print("Nota: χ² gl=8, α=0.05. Test complementario, no concluyente.")
    print("      Conforme NO prueba limpieza. Desvía NO prueba fraude.\n")

    results = {"per_candidate": {}, "pool": None, "findings": []}

    # Per candidate
    for col, label in [("fuji_v", "Fujimori"), ("rla_v", "López Aliaga"),
                       ("nieto_v", "Nieto"), ("belm_v", "Belmont"),
                       ("sanch_v", "Sánchez")]:
        r = benford_chi2(df[col].tolist())
        if r["sufficient"]:
            verdict = "✓ conforme" if r["conforms"] else "⚠ desvía"
            print(f"  {label:<15}  n={r['n']:>4}  χ²={r['chi2']:>6.2f}  "
                  f"p={r['p_value']:.3f}  {verdict}")
        else:
            print(f"  {label:<15}  n={r['n']:>4}  insuficientes datos (< 30)")
        results["per_candidate"][label] = r

    # Pool
    pool = []
    for col in ["fuji_v", "rla_v", "nieto_v", "belm_v", "sanch_v"]:
        pool.extend(df[col].tolist())
    pr = benford_chi2(pool)
    print()
    if pr["sufficient"]:
        verdict = "✓ conforme" if pr["conforms"] else "⚠ desvía"
        print(f"  POOL (5 cand)   n={pr['n']:>4}  χ²={pr['chi2']:>6.2f}  "
              f"p={pr['p_value']:.3f}  {verdict}")
    results["pool"] = pr

    # Findings
    pool_conforms = pr.get("conforms", False)
    results["findings"].append({
        "severity": "INFO",
        "id": "C1",
        "title": ("Benford (primer dígito, agregado) "
                  + ("conforme" if pool_conforms else "con desviación")),
        "detail": (f"Pool de 5 candidatos × 26 regiones (n={pr['n']}): "
                   f"χ²={pr['chi2']:.2f}, p={pr['p_value']:.3f}. "
                   + ("No se rechaza H0 de conformidad con Benford. "
                      "Recordar: este test tiene limitaciones en datos electorales."
                      if pool_conforms else
                      "Se rechaza H0 de conformidad, pero el test tiene "
                      "limitaciones conocidas. No es evidencia de fraude por sí solo.")),
    })

    return results


if __name__ == "__main__":
    run()
