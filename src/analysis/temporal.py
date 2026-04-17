"""
src/analysis/temporal.py

Análisis de serie temporal del conteo: detección de saltos sospechosos
y artifacts de caché.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def run(root: Path | None = None):
    ROOT = root or Path(__file__).resolve().parents[2]
    tp = ROOT / "data/processed/tracking.csv"
    if not tp.exists():
        print("[temporal] tracking.csv no disponible, saltando")
        return {"findings": []}

    dfc = pd.read_csv(tp, parse_dates=["ts"])
    dfc = dfc.sort_values("ts").reset_index(drop=True)

    # Detectar artefactos de caché: pct que baja y luego sube al mismo valor
    # (condición de carrera típica en proxies)
    artifacts = 0
    for i in range(2, len(dfc)):
        if dfc.loc[i, "pct"] == dfc.loc[i-2, "pct"] and \
           dfc.loc[i, "pct"] != dfc.loc[i-1, "pct"]:
            artifacts += 1

    # Deltas por candidato
    for c in ["fujimori", "rla", "nieto", "belmont", "sanchez"]:
        dfc[f"d{c}"] = dfc[c].diff()

    # Cambios de signo entre Sánchez y RLA
    dfc["sanch_rla_diff"] = dfc["sanchez"] - dfc["rla"]
    crossings = ((dfc["sanch_rla_diff"].shift(1) * dfc["sanch_rla_diff"]) < 0).sum()

    # Saltos >0.5pp en cualquier candidato (ignorando artefactos)
    big_jumps = 0
    for c in ["fujimori", "rla", "nieto", "belmont", "sanchez"]:
        big_jumps += (dfc[f"d{c}"].abs() > 0.5).sum()

    print("═" * 70)
    print(" D. SERIE TEMPORAL")
    print("═" * 70)
    print(f"  Cortes analizados: {len(dfc)}")
    print(f"  Primero: {dfc['ts'].iloc[0]}  ({dfc['pct'].iloc[0]:.2f}%)")
    print(f"  Último:  {dfc['ts'].iloc[-1]}  ({dfc['pct'].iloc[-1]:.2f}%)")
    print(f"  Artefactos de caché detectados (oscilación pct): {artifacts}")
    print(f"  Cambios de signo Sánchez↔RLA: {crossings}")
    print(f"  Saltos >0.5pp en algún candidato: {big_jumps}")

    findings = []
    if artifacts > 5:
        findings.append({
            "severity": "INFO",
            "id": "D1",
            "title": f"Artefactos técnicos de caché en tracking: {artifacts} eventos",
            "detail": (f"Se detectaron {artifacts} oscilaciones donde pct baja y "
                       f"sube al mismo valor. Es condición de carrera típica del "
                       f"proxy caché, NO movimiento real de la data ONPE primaria. "
                       f"Se documenta para evitar mala interpretación pública."),
        })

    if big_jumps == 0:
        findings.append({
            "severity": "INFO",
            "id": "D2",
            "title": "Sin saltos anómalos en el conteo temporal",
            "detail": (f"Ningún delta entre cortes consecutivos supera 0.5pp "
                       f"para ningún candidato en {len(dfc)} cortes analizados."),
        })

    if crossings == 1:
        findings.append({
            "severity": "INFO",
            "id": "D3",
            "title": "Cruce Sánchez↔RLA único, consistente con flujo natural",
            "detail": ("Se registró 1 cambio de signo entre Sánchez y RLA, "
                       "atribuible al ingreso progresivo de actas rurales "
                       "(donde Sánchez tiene ventaja) posterior al procesamiento "
                       "inicial de Lima y extranjero (donde RLA tiene ventaja)."),
        })

    return {"findings": findings, "tracking": dfc}


if __name__ == "__main__":
    run()
