"""Genera web/data.json para el dashboard público.

Lee regiones.csv + tracking.csv + findings.json y produce un JSON
auto-contenido para GitHub Pages.

Uso:
    py scripts/build_dashboard_json.py
"""
from __future__ import annotations

import json
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "web" / "data.json"


def norm_dep(s: str) -> str:
    """Normaliza nombre de región/departamento al formato del GeoJSON
    (UPPERCASE, sin diacríticos, sin espacios extras)."""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.upper().strip()


def main():
    tr = pd.read_csv(ROOT / "data" / "processed" / "tracking.csv")
    tr["ts"] = pd.to_datetime(tr["ts"])
    tr = tr.sort_values("ts").reset_index(drop=True)
    last = tr.iloc[-1]
    prev = tr.iloc[-2] if len(tr) > 1 else None

    reg = pd.read_csv(ROOT / "data" / "processed" / "regiones.csv")
    # Guard div/0 y NaN → se propagan como Infinity/NaN a JSON y rompen el JS.
    reg["vv_acta"] = reg["vv"] / reg["contabilizadas"].replace(0, np.nan)
    reg["vv_acta"] = reg["vv_acta"].fillna(0.0).replace([np.inf, -np.inf], 0.0)
    reg["actas_fuera"] = reg["enviadasJee"] + reg["pendientes_calc"]
    reg["votos_fuera"] = (reg["actas_fuera"] * reg["vv_acta"]).fillna(0.0)
    reg["delta"] = reg["votos_fuera"] * (reg["rla"] - reg["sanch"]) / 100
    reg = reg.sort_values("delta", ascending=False)

    findings = json.loads((ROOT / "reports" / "findings.json").read_text(encoding="utf-8"))["findings"]

    # Findings mesa-a-mesa GAP (F1..F4).
    gap_path = ROOT / "reports" / "findings_gap.json"
    findings_gap = None
    if gap_path.exists():
        findings_gap = json.loads(gap_path.read_text(encoding="utf-8"))

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
    # Alertas GAP (mesa-a-mesa) — prepend CRITICOS arriba.
    if findings_gap:
        for f in findings_gap.get("findings", []):
            if f["severity"] == "CRITICO":
                alerts.insert(0, {
                    "level": "critical",
                    "msg": f"[{f['id']}] {f.get('interpretacion', f['pregunta'])}"
                })
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

    # Regiones con margen absoluto (Sánchez − RLA) para mapa choropleth.
    # `name_norm` = NOMBDEP del GeoJSON oficial (UPPERCASE, sin diacríticos).
    regions = []
    for _, r in reg.iterrows():
        pct_actas = float(r["contabilizadas"]) / float(r["totalActas"]) * 100 if r["totalActas"] else 0.0
        regions.append({
            "name": r["name"],
            "name_norm": norm_dep(str(r["name"])),
            "rla_v": int(r["rla_v"]),
            "sanch_v": int(r["sanch_v"]),
            "rla_pct": float(r["rla"]),
            "sanch_pct": float(r["sanch"]),
            "margin": int(r["sanch_v"] - r["rla_v"]),
            "vv": int(r["vv"]),
            "pct_actas": round(pct_actas, 2),
            "actas_fuera": int(r["actas_fuera"]),
        })

    # Proyeccion lineal tipo Renzo — regresion por candidato vs pct escrutado
    # usando los ultimos N puntos (donde el conteo empieza a estabilizarse).
    # No reemplaza el forecast bayesiano; es una lectura rapida, asume integracion lineal.
    projection = None
    if len(tr) >= 10:
        tr_sorted = tr.sort_values("ts").copy()
        pct_now = float(tr_sorted["pct"].iloc[-1])
        tail = tr_sorted.tail(30)  # ultimos 30 cortes: fase estable
        xs = tail["pct"].astype(float).values
        proj: dict = {"pct_now": pct_now, "target_pct": 100.0, "window_points": int(len(tail))}
        xs_var = float(np.var(xs))
        for cand in ("fujimori", "sanchez", "rla", "nieto", "belmont"):
            ys = tail[cand].astype(float).values
            # Guard: xs casi constante o NaN → usar último valor observado.
            if xs_var < 1e-6 or np.any(np.isnan(ys)) or np.any(np.isnan(xs)):
                proj[cand] = round(float(ys[-1]), 3)
                proj[f"{cand}_slope"] = 0.0
                continue
            m, b = np.polyfit(xs, ys, 1)
            y100 = m * 100.0 + b
            if not np.isfinite(y100):
                proj[cand] = round(float(ys[-1]), 3)
                proj[f"{cand}_slope"] = 0.0
                continue
            proj[cand] = round(float(y100), 3)
            proj[f"{cand}_slope"] = round(float(m), 5)
        proj["margin_sanchez_rla_100"] = round(proj["sanchez"] - proj["rla"], 3)
        proj["method"] = "linear_regression_tail30"
        projection = proj

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
        "findings_gap": findings_gap,
        "series": series,
        "contrafactual": contrafactual,
        "regions": regions,
        "projection": projection,
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

    # API-01: endpoints publicos consumibles por terceros desde gh-pages.
    api_dir = ROOT / "web" / "api"
    api_dir.mkdir(parents=True, exist_ok=True)
    meta = out["meta"]
    endpoints = {
        "findings.json": {"findings": findings, "meta": meta},
        "findings_gap.json": {"findings_gap": findings_gap, "meta": meta},
        "forecast.json": {"forecast": forecast, "meta": meta},
        "state.json": {"state": state, "delta": delta, "meta": meta},
        "regions.json": {"regions": regions, "meta": meta},
        "series.json": {"series": series, "meta": meta},
        "projection.json": {"projection": projection, "meta": meta},
    }
    for name, payload in endpoints.items():
        (api_dir / name).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )
    print(f"OK: {api_dir} ({len(endpoints)} endpoints)")


if __name__ == "__main__":
    main()
