"""
src/process/build_dataset.py

Consolida las capturas JSON en CSVs procesables y verifica consistencia.

Uso:
    py src\\process\\build_dataset.py                    # última captura
    py src\\process\\build_dataset.py captures\\...\\     # captura específica
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd


def latest_capture(root: Path) -> Path:
    caps = sorted([p for p in (root / "captures").iterdir()
                   if p.is_dir() and p.name[0].isdigit()])
    if not caps:
        print("ERROR: no hay capturas en captures/", file=sys.stderr)
        sys.exit(1)
    return caps[-1]


def load_snap(capture_dir: Path, name: str) -> dict[str, Any]:
    path = capture_dir / "raw" / f"{name}.json"
    if not path.exists():
        print(f"ERROR: falta {path}", file=sys.stderr)
        sys.exit(1)
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    ROOT = Path(__file__).resolve().parents[2]

    if len(sys.argv) > 1:
        capture_dir = Path(sys.argv[1]).resolve()
    else:
        capture_dir = latest_capture(ROOT)

    print(f"[build] captura: {capture_dir.relative_to(ROOT)}")

    snap1 = load_snap(capture_dir, "snap1")
    snap2 = load_snap(capture_dir, "snap2")
    tracking = load_snap(capture_dir, "tracking")

    # ── Agregados nacionales ─────────────────────────────────────
    nat = snap1["national"]
    print(f"[build] actas: {nat['contabilizadas']:,}/{nat['totalActas']:,} "
          f"({nat['pct']}%)")
    print(f"[build] JEE: {nat['enviadasJee']:,}  pendientes: {nat['pendientesJee']:,}")

    # ── Consolidar regiones (snap1 + snap2) ──────────────────────
    regions_raw = list(snap1.get("regions", [])) + list(snap2.get("regions", []))
    seen = set()
    regions = []
    for r in regions_raw:
        if r["name"] not in seen:
            regions.append(r)
            seen.add(r["name"])

    df = pd.DataFrame(regions)

    # ── Campos derivados ─────────────────────────────────────────
    df["pendientes_calc"] = (df["totalActas"] - df["contabilizadas"] - df["enviadasJee"])
    df["tasa_impugnacion"] = df["enviadasJee"] / df["totalActas"] * 100
    df["tasa_pendientes"] = df["pendientes_calc"] / df["totalActas"] * 100
    df["tasa_avance"] = df["contabilizadas"] / df["totalActas"] * 100

    cols = ["name", "totalActas", "contabilizadas", "enviadasJee", "pendientes_calc",
            "tasa_avance", "tasa_impugnacion", "tasa_pendientes", "vv",
            "fuji", "fuji_v", "rla", "rla_v", "nieto", "nieto_v",
            "belm", "belm_v", "sanch", "sanch_v"]
    df = df[[c for c in cols if c in df.columns]]

    out_dir = ROOT / "data" / "processed"
    out_dir.mkdir(parents=True, exist_ok=True)

    df.to_csv(out_dir / "regiones.csv", index=False, encoding="utf-8")
    print(f"[build] escrito: data/processed/regiones.csv  ({len(df)} regiones)")

    # ── Verificación de consistencia ─────────────────────────────
    print("\n[build] consistency check: Σ regional vs nacional")
    issues = []
    for c in ["fuji", "rla", "nieto", "belm", "sanch"]:
        reg = int(df[f"{c}_v"].sum())
        nac = int(nat["candidates"][f"{c}_v"])
        diff = nac - reg
        pct = 100 * diff / nac if nac else 0
        flag = "⚠" if abs(pct) > 0.5 else "✓"
        print(f"  {flag} {c:6s}  reg={reg:>10,}  nac={nac:>10,}  "
              f"diff={diff:+,}  ({pct:+.3f}%)")
        if abs(pct) > 0.5:
            issues.append(c)

    # ── Serie temporal del tracking ──────────────────────────────
    cuts = tracking.get("cuts", [])
    dfc = pd.DataFrame(cuts)
    if not dfc.empty:
        dfc["ts"] = pd.to_datetime(dfc["ts"])
        dfc = dfc.sort_values("ts").reset_index(drop=True)
        dfc.to_csv(out_dir / "tracking.csv", index=False, encoding="utf-8")
        print(f"\n[build] escrito: data/processed/tracking.csv  ({len(dfc)} cortes)")

    # ── Meta ─────────────────────────────────────────────────────
    meta = {
        "capture_dir": str(capture_dir.relative_to(ROOT)).replace("\\", "/"),
        "capture_ts_utc": capture_dir.name,
        "pct_global": nat["pct"],
        "actas_contabilizadas": nat["contabilizadas"],
        "actas_total": nat["totalActas"],
        "enviadas_jee": nat["enviadasJee"],
        "pendientes_jee": nat["pendientesJee"],
        "votos_emitidos": nat["votosEmitidos"],
        "votos_validos": nat["votosValidos"],
        "margen_sanch_rla_votos": int(nat["candidates"]["sanch_v"] - nat["candidates"]["rla_v"]),
        "margen_sanch_rla_pct": nat["candidates"]["sanch"] - nat["candidates"]["rla"],
        "n_regiones": len(df),
        "consistency_issues": issues,
    }
    (out_dir / "meta.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"[build] escrito: data/processed/meta.json")
    print(f"\n[build] margen Sánchez − RLA: {meta['margen_sanch_rla_votos']:+,} votos "
          f"({meta['margen_sanch_rla_pct']:+.3f} pts)")


if __name__ == "__main__":
    main()
