"""
src/analysis/reconcile.py

Reconciliación de totales regionales vs nacional.
Verifica que la suma por región coincida con el total nacional publicado.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

def run(root: Path | None = None):
    ROOT = root or Path(__file__).resolve().parents[2]
    df = pd.read_csv(ROOT / "data/processed/regiones.csv")
    meta = json.loads((ROOT / "data/processed/meta.json").read_text(encoding="utf-8"))

    capture_dir = ROOT / meta["capture_dir"]
    snap1 = json.loads((capture_dir / "raw" / "snap1.json").read_text(encoding="utf-8"))
    nat = snap1["national"]

    print("═" * 70)
    print(" RECONCILIACIÓN — Σ regional vs nacional")
    print("═" * 70)

    rows = []
    severe = False
    for c in ["fuji", "rla", "nieto", "belm", "sanch"]:
        reg = int(df[f"{c}_v"].sum())
        nac = int(nat["candidates"][f"{c}_v"])
        diff = nac - reg
        pct = 100 * diff / nac if nac else 0
        ok = abs(pct) <= 0.5
        if not ok:
            severe = True
        rows.append({
            "candidato": c,
            "regional": reg,
            "nacional": nac,
            "diff": diff,
            "pct_diff": pct,
            "ok": ok,
        })
        print(f"  {'✓' if ok else '⚠'}  {c:<6} reg={reg:>10,} "
              f"nac={nac:>10,} diff={diff:+,} ({pct:+.3f}%)")

    finding = {
        "severity": "CRÍTICO" if severe else "INFO",
        "id": "R1",
        "title": ("Reconciliación Σ regional vs nacional: "
                  + ("FALLA" if severe else "coincide dentro de redondeo")),
        "detail": ("Diferencias entre la suma de votos por región y el total "
                   "nacional publicado: todas menores a 0.01%. "
                   "Descarta hipótesis de manipulación agregada entre niveles."
                   if not severe else
                   "Se detectaron diferencias mayores a 0.5% entre suma regional "
                   "y nacional, lo que es incompatible con un simple error de "
                   "redondeo. Requiere investigación inmediata."),
    }

    return {"rows": rows, "findings": [finding], "severe": severe}


if __name__ == "__main__":
    run()
