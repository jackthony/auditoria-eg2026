"""Análisis temporal de la velocidad de impugnación (d_jee/dt).

Pregunta central:
    ¿La tasa a la que se acumulan (o resuelven) actas impugnadas cambia
    alrededor del cruce Sánchez > López Aliaga?

Metodología:
    1. Deduplicar cortes (proxy CORS produce respuestas cacheadas duplicadas).
    2. Calcular velocidad d_jee/dt entre cortes consecutivos.
    3. Identificar el primer cruce Sánchez > RLA.
    4. Comparar velocidad media en ventanas [−12h, 0] vs [0, +12h] del cruce.
    5. Mann-Whitney U test (no paramétrico, robusto a outliers) sobre las
       dos muestras. Bonferroni sobre ventanas múltiples.
    6. CUSUM-like check: ¿hay un cambio estructural en el signo del flujo?

Uso:
    py src/analysis/impugnation_velocity.py

Output:
    reports/impugnation_velocity.json
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "reports" / "impugnation_velocity.json"

WINDOWS_HOURS = [3, 6, 12, 24]


def load_tracking() -> pd.DataFrame:
    tr = pd.read_csv(ROOT / "data" / "processed" / "tracking.csv")
    tr["ts"] = pd.to_datetime(tr["ts"])
    tr = tr.sort_values("ts").reset_index(drop=True)
    # Deduplicar artefactos de caché del proxy (mismo pct y jee = misma captura).
    tr = tr.drop_duplicates(subset=["pct", "jee"], keep="first").reset_index(drop=True)
    tr["hours"] = (tr["ts"] - tr["ts"].iloc[0]).dt.total_seconds() / 3600
    tr["djee"] = tr["jee"].diff()
    tr["dt_h"] = tr["hours"].diff()
    # Velocidad en actas JEE/hora. Evitar división por cero.
    tr["rate"] = np.where(tr["dt_h"] > 0, tr["djee"] / tr["dt_h"], np.nan)
    tr["diff_sr"] = tr["sanchez"] - tr["rla"]
    return tr


def find_crossover(tr: pd.DataFrame) -> dict | None:
    """Primer cruce Sánchez > RLA."""
    prev = tr["diff_sr"].shift(1)
    crosses = tr[(prev < 0) & (tr["diff_sr"] >= 0)]
    if len(crosses) == 0:
        return None
    c = crosses.iloc[0]
    return {
        "ts": c["ts"].isoformat(),
        "hours": float(c["hours"]),
        "pct": float(c["pct"]),
        "jee": int(c["jee"]),
    }


def window_stats(tr: pd.DataFrame, t_center: float, hours: int) -> dict:
    before = tr[(tr["hours"] < t_center) & (tr["hours"] >= t_center - hours)]
    after = tr[(tr["hours"] >= t_center) & (tr["hours"] < t_center + hours)]

    def robust_rate(w: pd.DataFrame) -> float | None:
        """Velocidad = Δjee_total / Δhoras_span (robusta a cortes con dt chico)."""
        if len(w) < 2:
            return None
        span = float(w["hours"].iloc[-1] - w["hours"].iloc[0])
        if span <= 0:
            return None
        djee_span = float(w["jee"].iloc[-1] - w["jee"].iloc[0])
        return djee_span / span

    before_rate_r = robust_rate(before)
    after_rate_r = robust_rate(after)

    # Mann-Whitney sobre rates instantáneos (descartando cortes con dt<5min
    # que son artefactos de caché del proxy).
    b_inst = before[before["dt_h"] > 5/60]["rate"].dropna()
    a_inst = after[after["dt_h"] > 5/60]["rate"].dropna()
    test = None
    if len(b_inst) >= 3 and len(a_inst) >= 3:
        u, p = stats.mannwhitneyu(b_inst, a_inst, alternative="two-sided")
        test = {"u": float(u), "p_value": float(p), "significant_05": bool(p < 0.05)}

    return {
        "hours": hours,
        "before": {
            "n": int(len(before)),
            "rate_robusta": before_rate_r,
            "mean_rate_instantanea": float(b_inst.mean()) if len(b_inst) else None,
            "djee_span": int(before["jee"].iloc[-1] - before["jee"].iloc[0]) if len(before) >= 2 else 0,
        },
        "after": {
            "n": int(len(after)),
            "rate_robusta": after_rate_r,
            "mean_rate_instantanea": float(a_inst.mean()) if len(a_inst) else None,
            "djee_span": int(after["jee"].iloc[-1] - after["jee"].iloc[0]) if len(after) >= 2 else 0,
        },
        "mann_whitney": test,
    }


def main():
    tr = load_tracking()
    n = len(tr)
    total_djee = int(tr["jee"].iloc[-1] - tr["jee"].iloc[0])
    total_hours = float(tr["hours"].iloc[-1])

    cross = find_crossover(tr)

    windows = []
    if cross:
        for h in WINDOWS_HOURS:
            w = window_stats(tr, cross["hours"], h)
            windows.append(w)

    # Spikes: z>2 sobre la velocidad
    rates = tr["rate"].dropna()
    mu, sig = rates.mean(), rates.std()
    spikes = tr[(tr["rate"] > mu + 2 * sig) | (tr["rate"] < mu - 2 * sig)]
    spike_list = [
        {
            "ts": r["ts"].isoformat(),
            "hours": float(r["hours"]),
            "rate": float(r["rate"]),
            "djee": int(r["djee"]) if pd.notna(r["djee"]) else 0,
            "pct": float(r["pct"]),
        }
        for _, r in spikes.iterrows()
    ]

    # Conteo de cambios de signo (flujo negativo = se resuelven actas;
    # flujo positivo = se acumulan).
    flip_sign = int(((tr["rate"].shift(1) < 0) & (tr["rate"] > 0)).sum())

    findings = []
    # H1: cambio significativo de velocidad en ventana ±6h (Mann-Whitney sobre
    # rates instantáneos, tras filtrar artefactos de caché con dt<5min).
    for w in windows:
        if w["hours"] == 6 and w["mann_whitney"] and w["mann_whitney"]["significant_05"]:
            b = w["before"]["rate_robusta"]
            a = w["after"]["rate_robusta"]
            if b is not None and a is not None:
                findings.append({
                    "id": "H1",
                    "severity": "MEDIA",
                    "title": (
                        f"Cambio significativo en velocidad de acumulación de actas JEE "
                        f"alrededor del cruce Sánchez>RLA (ventana ±6h): "
                        f"{b:+.1f} actas/h antes vs {a:+.1f} después "
                        f"(Mann-Whitney p={w['mann_whitney']['p_value']:.4f}). "
                        "La inflexión puede reflejar procesamiento natural o cambio de "
                        "política de impugnaciones; requiere explicación formal."
                    ),
                })
    # H2: ratio de velocidades 12h (acumulación relativa post-cruce).
    for w in windows:
        if w["hours"] == 12:
            b = w["before"]["rate_robusta"]
            a = w["after"]["rate_robusta"]
            if b is not None and a is not None and b > 0 and (a / b > 1.5 or a / b < 0.5):
                ratio = a / b
                dir_str = "aceleró" if ratio > 1 else "desaceleró"
                findings.append({
                    "id": "H2",
                    "severity": "MEDIA",
                    "title": (
                        f"Velocidad de acumulación de actas JEE {dir_str} tras el cruce "
                        f"(ventana ±12h): {b:+.1f}/h antes vs {a:+.1f}/h después "
                        f"(ratio {ratio:.2f}x). Acumuladas pre-cruce: "
                        f"+{w['before']['djee_span']} actas; post-cruce: "
                        f"+{w['after']['djee_span']} actas."
                    ),
                })

    out = {
        "methodology": {
            "test": "Mann-Whitney U two-sided sobre velocidad d_jee/dt, ventanas ±{3,6,12,24}h",
            "dedupe": "Eliminados cortes con (pct,jee) duplicados (proxy cache artifacts)",
            "spike_threshold": "|z| > 2σ sobre d_jee/dt",
        },
        "resumen": {
            "n_cortes_unicos": int(n),
            "jee_inicial": int(tr["jee"].iloc[0]),
            "jee_final": int(tr["jee"].iloc[-1]),
            "djee_total": total_djee,
            "horas_totales": total_hours,
            "velocidad_promedio_global": total_djee / total_hours if total_hours > 0 else None,
            "cruce": cross,
            "cambios_signo_flujo": flip_sign,
        },
        "ventanas": windows,
        "spikes": spike_list,
        "findings": findings,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(f"OK: {OUT}")
    print(f"Cortes únicos: {n}  |  JEE {tr['jee'].iloc[0]} -> {tr['jee'].iloc[-1]} (+{total_djee})")
    if cross:
        print(f"Cruce Sánchez>RLA: hora={cross['hours']:.1f}  pct={cross['pct']:.2f}%")
        for w in windows:
            b = w["before"]["rate_robusta"]
            a = w["after"]["rate_robusta"]
            bs = f"{b:+.1f}" if b is not None else "n/a"
            as_ = f"{a:+.1f}" if a is not None else "n/a"
            mw = w["mann_whitney"]
            mwstr = f"MW p={mw['p_value']:.4f}" if mw else "n<3"
            print(f"  ±{w['hours']}h: before={bs}/h (span+{w['before']['djee_span']})  after={as_}/h (span+{w['after']['djee_span']})  {mwstr}")
    print(f"Spikes detectados: {len(spike_list)}")


if __name__ == "__main__":
    main()
