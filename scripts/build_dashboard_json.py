"""Genera web/data.json para el dashboard público.

Lee regiones.csv + tracking.csv + findings.json y produce un JSON
auto-contenido para GitHub Pages.

Uso:
    py scripts/build_dashboard_json.py
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "web" / "data.json"


def main():
    tr = pd.read_csv(ROOT / "data" / "processed" / "tracking.csv")
    tr["ts"] = pd.to_datetime(tr["ts"])
    tr = tr.sort_values("ts").reset_index(drop=True)
    last = tr.iloc[-1]
    prev = tr.iloc[-2] if len(tr) > 1 else None

    reg = pd.read_csv(ROOT / "data" / "processed" / "regiones.csv")
    reg["vv_acta"] = reg["vv"] / reg["contabilizadas"]
    reg["actas_fuera"] = reg["enviadasJee"] + reg["pendientes_calc"]
    reg["votos_fuera"] = reg["actas_fuera"] * reg["vv_acta"]
    reg["delta"] = reg["votos_fuera"] * (reg["rla"] - reg["sanch"]) / 100
    reg = reg.sort_values("delta", ascending=False)

    findings = json.loads((ROOT / "reports" / "findings.json").read_text(encoding="utf-8"))["findings"]

    # Margen Sánchez - RLA en votos absolutos (desde regiones.csv sanch_v/rla_v).
    # Los porcentajes de tracking.csv están redondeados a 3 dec y producen error de +5-6k votos.
    vv_total = int(reg["vv"].sum())
    votos_sanch = int(reg["sanch_v"].sum())
    votos_rla = int(reg["rla_v"].sum())
    margen = votos_sanch - votos_rla

    state = {
        "ts": last["ts"].isoformat(),
        "ts_human": last["ts"].strftime("%Y-%m-%d %H:%M UTC"),
        "pct": float(last["pct"]),
        "fujimori": float(last["fujimori"]),
        "sanchez": float(last["sanchez"]),
        "rla": float(last["rla"]),
        "nieto": float(last["nieto"]),
        "belmont": float(last["belmont"]),
        "margen_sanch_rla": margen,
        "votos_sanchez": votos_sanch,
        "votos_rla": votos_rla,
        "actas_jee": int(last["jee"]),
        "contabilizadas": int(last["contabilizadas"]),
    }

    delta = None
    if prev is not None:
        # Delta de margen aproximado usando porcentajes del corte anterior × vv_total actual.
        # Es una aproximación (±3-5k votos) porque no guardamos snapshots de sanch_v/rla_v por corte.
        delta_margen = int(round((last["sanchez"] - last["rla"] - prev["sanchez"] + prev["rla"])/100 * vv_total))
        delta = {
            "fujimori": float(last["fujimori"] - prev["fujimori"]),
            "sanchez": float(last["sanchez"] - prev["sanchez"]),
            "rla": float(last["rla"] - prev["rla"]),
            "margen_sanch_rla": delta_margen,
        }

    # Alertas automáticas
    alerts = []
    if last["pct"] < 100.0 and state["actas_jee"] > 5000:
        alerts.append({"level": "critical",
            "msg": f"Universo en disputa ~{reg['votos_fuera'].sum():,.0f} votos "
                   f"(≈{int(reg['votos_fuera'].sum()/max(abs(margen),1))}× el margen). "
                   "Definición del 2° lugar depende de resolución JEE."})
    if abs(margen) < 10000:
        alerts.append({"level": "warning",
            "msg": f"Margen estrecho: |Sánchez−RLA| = {abs(margen):,} votos. "
                   "Cualquier movimiento material de actas puede voltear el 2° lugar."})
    if delta and abs(delta["margen_sanch_rla"]) > 5000:
        dire = "aumentó" if delta["margen_sanch_rla"] > 0 else "redujo"
        alerts.append({"level": "warning",
            "msg": f"Variación relevante vs corte anterior: el margen {dire} en "
                   f"{abs(delta['margen_sanch_rla']):,} votos."})
    if state["pct"] < 95.0:
        alerts.append({"level": "info",
            "msg": f"Escrutinio aún incompleto ({state['pct']:.2f}%). Faltan cortes."})
    if not alerts:
        alerts.append({"level": "info", "msg": "Sin alertas nuevas en este corte."})

    # Serie temporal (reducir a ~60 puntos máx para el chart)
    step = max(1, len(tr) // 60)
    series = []
    for _, row in tr.iloc[::step].iterrows():
        series.append({
            "ts": row["ts"].isoformat(),
            "fujimori": float(row["fujimori"]),
            "sanchez": float(row["sanchez"]),
            "rla": float(row["rla"]),
            "nieto": float(row["nieto"]),
            "belmont": float(row["belmont"]),
        })

    # Contrafactual por región (top+bottom)
    contrafactual = []
    for _, r in reg.iterrows():
        contrafactual.append({
            "name": r["name"],
            "actas_fuera": int(r["actas_fuera"]),
            "rla": float(r["rla"]),
            "sanch": float(r["sanch"]),
            "delta": float(r["delta"]),
        })

    # Forecast bayesiano (opcional — si fue corrido).
    forecast_path = ROOT / "reports" / "forecast.json"
    forecast = None
    if forecast_path.exists():
        forecast = json.loads(forecast_path.read_text(encoding="utf-8"))
        # Alerta critical si P(cruce) > 30% en escenario central.
        p_cruce = forecast["escenarios"]["central"]["p_rla_supera_sanchez"]
        if p_cruce > 0.30:
            alerts.insert(0, {
                "level": "critical",
                "msg": f"Modelo bayesiano: P(RLA supera Sánchez) = {p_cruce:.0%} "
                       f"en escenario central. Empate técnico estadístico."
            })

    out = {
        "state": state,
        "delta": delta,
        "alerts": alerts,
        "findings": findings,
        "series": series,
        "contrafactual": contrafactual,
        "forecast": forecast,
        "meta": {
            "generated_at": pd.Timestamp.utcnow().isoformat(),
            "source": "ONPE vía proxy CORS + captura atómica con SHA-256",
            "repo": "https://github.com/neuracode/auditoria-eg2026",
        },
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2, default=str),
                   encoding="utf-8")
    print(f"OK: {OUT} ({OUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
