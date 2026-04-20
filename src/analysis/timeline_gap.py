"""TIMELINE-01: analiza gap temporal lineaTiempo por mesa.

Evalua si el tiempo entre Transmision (T) y Contabilizacion (C)
esta correlacionado con el resultado electoral por candidato/region.

Output:
  reports/timeline_gap.json
  reports/timeline_outliers.csv (mesas gap > p95)
"""
from __future__ import annotations

import csv
import glob
import gzip
import json
import logging
from collections import defaultdict
from pathlib import Path
from statistics import median
from typing import Any

from scipy import stats

from src.process.models_mesa import MesaRecord

logger = logging.getLogger(__name__)

CAND_JPP = "JUNTOS POR EL PERU"
CAND_RLA = "PARTIDO CIVICO OBRAS"


def dep_code(ubigeo: int | str | None) -> str:
    if not ubigeo:
        return "??"
    return str(ubigeo).zfill(6)[:2]


def extract_gaps(mesa: dict) -> dict[str, Any] | None:
    """Retorna {codigoMesa, dep, gap_t_c_s, jpp_votos, rla_votos, total, ganador}."""
    lt = mesa.get("lineaTiempo") or []
    by_state = {e["codigoEstadoActa"]: e["fechaRegistro"] for e in lt if e.get("fechaRegistro")}
    if "T" not in by_state or "C" not in by_state:
        return None

    gap_ms = by_state["C"] - by_state["T"]
    if gap_ms < 0:
        return None

    detalle = mesa.get("detalle") or []
    votos = {d.get("adDescripcion", ""): (d.get("adVotos") or 0) for d in detalle}
    jpp = next((v for k, v in votos.items() if k and k.startswith("JUNTOS")), 0)
    rla = next((v for k, v in votos.items() if k and "OBRAS" in k), 0)
    total_valid = sum(v for k, v in votos.items()
                      if not any(t in (k or "").upper() for t in ("BLANCO", "NULO", "IMPUG")))

    ganador = max(votos.items(), key=lambda x: x[1] or 0)[0] if votos else None

    return {
        "codigoMesa": mesa.get("codigoMesa"),
        "idUbigeo": mesa.get("idUbigeo"),
        "dep": dep_code(mesa.get("idUbigeo")),
        "gap_t_c_s": round(gap_ms / 1000, 1),
        "t_ms": by_state["T"],
        "c_ms": by_state["C"],
        "jpp_votos": jpp,
        "rla_votos": rla,
        "total_valid": total_valid,
        "jpp_pct": round(jpp / total_valid * 100, 3) if total_valid else 0,
        "ganador": ganador,
    }


def iter_mesas(capture_dir: Path, eleccion: int):
    for fp in sorted(glob.glob(str(capture_dir / "*.json.gz"))):
        try:
            payload = json.loads(gzip.open(fp).read())
        except Exception as e:
            logger.warning("skip %s: %s", fp, e)
            continue
        for row in payload.get("data", []):
            if row.get("idEleccion") != eleccion:
                continue
            yield row


def analyze(capture_ts: str, eleccion: int = 10) -> dict:
    capture_dir = Path(f"captures/{capture_ts}/mesas")
    records = []
    for mesa in iter_mesas(capture_dir, eleccion):
        r = extract_gaps(mesa)
        if r is not None:
            records.append(r)

    gaps = [r["gap_t_c_s"] for r in records]
    if not gaps:
        raise RuntimeError("no timeline data")

    p50 = float(median(gaps))
    p95 = float(stats.scoreatpercentile(gaps, 95))
    p99 = float(stats.scoreatpercentile(gaps, 99))

    # split: gap <=p50 vs gap >p95
    low = [r for r in records if r["gap_t_c_s"] <= p50]
    high = [r for r in records if r["gap_t_c_s"] > p95]

    def pct_jpp(rs):
        tot = sum(r["total_valid"] for r in rs)
        jpp = sum(r["jpp_votos"] for r in rs)
        return jpp / tot * 100 if tot else 0

    jpp_low = pct_jpp(low)
    jpp_high = pct_jpp(high)

    # Mann-Whitney on jpp_pct between low vs high
    u_stat, u_pval = stats.mannwhitneyu(
        [r["jpp_pct"] for r in low],
        [r["jpp_pct"] for r in high],
        alternative="two-sided",
    )

    # por departamento
    by_dep: dict[str, dict[str, float]] = defaultdict(lambda: {"n": 0, "gap_med": 0, "jpp_pct": 0, "_gaps": [], "_jpp": 0, "_tot": 0})
    for r in records:
        d = by_dep[r["dep"]]
        d["n"] += 1
        d["_gaps"].append(r["gap_t_c_s"])
        d["_jpp"] += r["jpp_votos"]
        d["_tot"] += r["total_valid"]
    for d in by_dep.values():
        d["gap_med"] = float(median(d["_gaps"])) if d["_gaps"] else 0
        d["jpp_pct"] = d["_jpp"] / d["_tot"] * 100 if d["_tot"] else 0
        for k in ("_gaps", "_jpp", "_tot"):
            d.pop(k)

    # outliers CSV
    out_csv = Path("reports/timeline_outliers.csv")
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["codigoMesa", "idUbigeo", "dep", "gap_t_c_s",
                                          "jpp_votos", "rla_votos", "total_valid",
                                          "jpp_pct", "ganador"],
                           extrasaction="ignore", delimiter=";")
        w.writeheader()
        for r in sorted(high, key=lambda x: -x["gap_t_c_s"]):
            w.writerow(r)

    report = {
        "capture_ts": capture_ts,
        "eleccion": eleccion,
        "n_mesas_con_timeline": len(records),
        "gap_t_c_s": {
            "p50": p50, "p95": p95, "p99": p99,
            "max": float(max(gaps)), "min": float(min(gaps)),
            "mean": float(sum(gaps) / len(gaps)),
        },
        "jpp_pct_por_grupo": {
            "low_gap_lte_p50": round(jpp_low, 3),
            "high_gap_gt_p95": round(jpp_high, 3),
            "delta_pp": round(jpp_high - jpp_low, 3),
        },
        "mannwhitney_jpp_pct_low_vs_high": {
            "u_statistic": float(u_stat),
            "p_value": float(u_pval),
            "n_low": len(low),
            "n_high": len(high),
            "interpretacion": "H0: misma distribucion JPP%; p<0.001 rechaza H0",
        },
        "por_departamento": dict(by_dep),
    }

    out_json = Path("reports/timeline_gap.json")
    out_json.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--ts", required=True)
    ap.add_argument("--eleccion", type=int, default=10)
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    r = analyze(args.ts, args.eleccion)
    print(f"mesas con timeline: {r['n_mesas_con_timeline']:,}")
    print(f"gap T->C p50={r['gap_t_c_s']['p50']:.0f}s  p95={r['gap_t_c_s']['p95']:.0f}s  p99={r['gap_t_c_s']['p99']:.0f}s")
    print(f"JPP% low_gap={r['jpp_pct_por_grupo']['low_gap_lte_p50']}  high_gap={r['jpp_pct_por_grupo']['high_gap_gt_p95']}  delta={r['jpp_pct_por_grupo']['delta_pp']:+.3f}pp")
    print(f"Mann-Whitney U p={r['mannwhitney_jpp_pct_low_vs_high']['p_value']:.3e}")


if __name__ == "__main__":
    main()
