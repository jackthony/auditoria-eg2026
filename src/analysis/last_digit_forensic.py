"""
Test forense de último dígito (Mebane 2006, Beber & Scacco 2012).

Detección de adulteración manual de vote counts: bajo conteo genuino a gran
escala, el último dígito de los totales debe distribuirse uniformemente
(p=0.1 cada dígito). Manipulación humana introduce preferencia por dígitos
"redondos" (0, 5) o aversión a dígitos consecutivos idénticos.

Referencias:
- Mebane, W. (2006). Election Forensics: Vote Counts and Benford's Law.
- Beber, B. & Scacco, A. (2012). What the Numbers Say: A Digit-Based Test
  for Election Fraud. Political Analysis, 20(2), 211-234.

Aplicado a: votos absolutos por candidato por región (Perú EG2026, 26 regiones
× 5 candidatos = 130 observaciones por candidato set).

Honestidad: con n=26 por candidato, la prueba chi-cuadrado tiene poder limitado.
Se reportan todos los candidatos, incluso si RLA sale limpio.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
REG = ROOT / "data" / "processed" / "regiones.csv"
OUT = ROOT / "reports" / "last_digit.json"

CANDIDATES = ["fuji_v", "rla_v", "nieto_v", "belm_v", "sanch_v"]
LABEL = {
    "fuji_v": "Fujimori",
    "rla_v": "López Aliaga (RLA)",
    "nieto_v": "Nieto",
    "belm_v": "Belmont",
    "sanch_v": "Sánchez",
}


def last_digit_test(counts: np.ndarray) -> dict:
    """Chi-cuadrado test contra uniforme (p=0.1 por dígito).

    Filtra conteos <10 (Beber & Scacco: solo cuentas con ≥2 dígitos).
    """
    filtered = counts[counts >= 10]
    n = len(filtered)
    if n == 0:
        return {"n": 0, "error": "no observations ≥10"}

    last = filtered % 10
    observed = np.bincount(last, minlength=10)
    expected = np.full(10, n / 10.0)

    # Chi-cuadrado
    chi2, p_value = stats.chisquare(observed, expected)

    # Mean last digit — bajo uniforme, esperanza = 4.5, var = 8.25
    mean_ld = float(last.mean())
    z_mean = (mean_ld - 4.5) / np.sqrt(8.25 / n)
    p_mean = 2 * (1 - stats.norm.cdf(abs(z_mean)))

    # Fracción con dígitos "redondos" (0, 5)
    round_frac = float(((last == 0) | (last == 5)).mean())
    z_round = (round_frac - 0.2) / np.sqrt(0.2 * 0.8 / n)
    p_round = 2 * (1 - stats.norm.cdf(abs(z_round)))

    return {
        "n": int(n),
        "observed_counts": observed.tolist(),
        "expected_count_per_digit": float(n / 10.0),
        "chi2": float(chi2),
        "chi2_p_value": float(p_value),
        "mean_last_digit": mean_ld,
        "z_mean_last_digit": float(z_mean),
        "p_mean_last_digit": float(p_mean),
        "round_digit_fraction": round_frac,
        "z_round_digits": float(z_round),
        "p_round_digits": float(p_round),
        "verdict": (
            "SOSPECHOSO" if p_value < 0.05 or p_round < 0.05
            else "CONFORME"
        ),
    }


def run() -> dict:
    df = pd.read_csv(REG)

    out: dict = {
        "method": "Mebane 2006 / Beber-Scacco 2012 last-digit uniformity test",
        "granularity": "regional (26 departamentos Perú)",
        "sample_filter": "counts >= 10 (two digits minimum)",
        "significance": "alpha=0.05, bilateral",
        "candidates": {},
    }

    for cand in CANDIDATES:
        counts = df[cand].values.astype(int)
        out["candidates"][LABEL[cand]] = last_digit_test(counts)

    # También en total: todos los conteos
    all_counts = np.concatenate([df[c].values.astype(int) for c in CANDIDATES])
    out["pooled_all_candidates"] = last_digit_test(all_counts)

    # Finding
    suspects = [
        name for name, res in out["candidates"].items()
        if res.get("verdict") == "SOSPECHOSO"
    ]
    out["finding"] = {
        "id": "M1",
        "severity": "MEDIA" if suspects else "INFO",
        "description": (
            "Último dígito de vote counts regional conforme a uniforme"
            if not suspects
            else f"Desviación uniforme en: {', '.join(suspects)}"
        ),
        "suspects": suspects,
        "caveat": (
            "n=26 por candidato, poder estadístico limitado. "
            "Un resultado 'CONFORME' no descarta manipulación a otras escalas "
            "(mesa, acta). Pedido formal de data mesa-a-mesa necesario."
        ),
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    return out


if __name__ == "__main__":
    res = run()
    print(f"M1 last-digit test:")
    for cand, r in res["candidates"].items():
        print(f"  {cand:25s} n={r['n']:3d} chi2_p={r['chi2_p_value']:.3f} "
              f"round={r['round_digit_fraction']:.3f} (p={r['p_round_digits']:.3f}) "
              f"-> {r['verdict']}")
    print(f"  {'POOLED':25s} n={res['pooled_all_candidates']['n']:3d} "
          f"chi2_p={res['pooled_all_candidates']['chi2_p_value']:.3f} "
          f"-> {res['pooled_all_candidates']['verdict']}")
    print(f"\nFinding M1: {res['finding']['severity']} - {res['finding']['description']}")
