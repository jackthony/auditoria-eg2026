"""ML-ANOM — Isolation Forest sobre saltos de la serie temporal.

Detecta saltos atipicos en el % de cada candidato usando features:
  - delta_pct        cambio absoluto vs corte anterior
  - delta_t_minutes  distancia temporal al corte anterior
  - velocity         delta_pct / delta_t_minutes (pp por minuto)
  - delta_actas_jee  cambio en actas impugnadas (integracion JEE)

Supuesto: la gran mayoria de cortes son "normales" (smooth updates).
Las actualizaciones sospechosas (saltos grandes sin tiempo transcurrido,
reversiones no monotonas, integracion masiva de JEE) aparecen como
outliers multivariados.

No afirma fraude. Reporta observaciones con score bajo (IsolationForest)
para revision manual. H0 implicita: todos los saltos provienen de la
misma distribucion generativa.

Salida: reports/ml_anomalies.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

CANDIDATES = ["fujimori", "sanchez", "rla", "nieto", "belmont"]
CONTAMINATION = 0.05  # 5% esperados como outliers
RANDOM_STATE = 42


def _features_for(df: pd.DataFrame, cand: str) -> pd.DataFrame:
    s = df.sort_values("ts").copy()
    s["delta_pct"] = s[cand].diff()
    s["delta_t_minutes"] = s["ts"].diff().dt.total_seconds() / 60.0
    s["delta_jee"] = s["jee"].diff() if "jee" in s.columns else 0.0
    s["velocity"] = s["delta_pct"] / s["delta_t_minutes"].replace(0, np.nan)
    return s.dropna(subset=["delta_pct", "delta_t_minutes", "velocity"])


def run(root: Path | None = None) -> dict:
    ROOT = root or Path(__file__).resolve().parents[2]
    tp = ROOT / "data/processed/tracking.csv"
    if not tp.exists():
        print("[ml_anom] tracking.csv no disponible, saltando")
        return {"findings": [], "anomalies": {}}

    df = pd.read_csv(tp, parse_dates=["ts"])
    if len(df) < 20:
        print(f"[ml_anom] n={len(df)} puntos, insuficiente (min 20)")
        return {"findings": [], "anomalies": {}}

    print(f"── ML-ANOM: IsolationForest sobre {len(df)} cortes, {len(CANDIDATES)} candidatos ──")

    anomalies: dict[str, list[dict]] = {}
    findings: list[dict] = []
    total_anom = 0

    for cand in CANDIDATES:
        if cand not in df.columns:
            continue
        feats = _features_for(df, cand)
        if len(feats) < 10:
            continue
        X = feats[["delta_pct", "delta_t_minutes", "velocity", "delta_jee"]].fillna(0).values
        iso = IsolationForest(
            contamination=CONTAMINATION, random_state=RANDOM_STATE,
            n_estimators=200,
        )
        labels = iso.fit_predict(X)
        scores = iso.score_samples(X)  # mas bajo = mas anomalo
        feats = feats.assign(label=labels, score=scores)

        out = feats[feats["label"] == -1].sort_values("score")
        anomalies[cand] = [
            {
                "ts": r["ts"].isoformat(),
                "delta_pct": round(float(r["delta_pct"]), 4),
                "delta_t_min": round(float(r["delta_t_minutes"]), 2),
                "velocity_pp_per_min": round(float(r["velocity"]), 5),
                "delta_jee": int(r["delta_jee"]) if pd.notna(r["delta_jee"]) else None,
                "score": round(float(r["score"]), 4),
            }
            for _, r in out.iterrows()
        ]
        total_anom += len(out)
        if len(out):
            worst = anomalies[cand][0]
            print(f"  {cand:10s} {len(out)} anomalias · peor: "
                  f"{worst['ts'][:19]} delta={worst['delta_pct']:+.3f}pp "
                  f"vel={worst['velocity_pp_per_min']:+.4f}pp/min")

    sev = "MEDIA" if total_anom > 0 else "INFO"
    findings.append({
        "id": "M3",
        "severity": sev,
        "test": "IsolationForest saltos temporales",
        "title": f"ML-ANOM: {total_anom} saltos atipicos detectados en serie temporal "
                 f"(contamination={CONTAMINATION}, n={len(df)})",
        "h0": "Todos los saltos provienen de la misma distribucion generativa",
        "method": "IsolationForest (n_estimators=200) sobre features "
                  "[delta_pct, delta_t_min, velocity, delta_jee] por candidato",
        "interpretation": "Senal complementaria para revision manual. "
                          "No afirma fraude, identifica cortes con perfil "
                          "estadisticamente inusual.",
        "limitations": "Contamination fija 5%; no-supervisado, no identifica causa. "
                       "Requiere n>=20 cortes.",
    })

    out_path = ROOT / "reports" / "ml_anomalies.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps({
            "n_samples": int(len(df)),
            "contamination": CONTAMINATION,
            "total_anomalies": total_anom,
            "anomalies": anomalies,
            "findings": findings,
        }, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    print(f"  ✓ {out_path}")
    return {"findings": findings, "anomalies": anomalies, "total": total_anom}


if __name__ == "__main__":
    run()
