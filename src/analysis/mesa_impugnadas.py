"""
src/analysis/mesa_impugnadas.py — MESA-01

Analiza mesas con estadoActa=I (impugnadas) desde capturas mesa-a-mesa.
Calcula electores hábiles en juego y distribución geográfica.

Uso:
    py -m src.analysis.mesa_impugnadas [ts]
    py -m src.analysis.mesa_impugnadas 20260419T035056Z
"""
from __future__ import annotations

import gzip
import json
import sys
from collections import Counter, defaultdict
from multiprocessing import Pool, cpu_count
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[2]
ID_ELECCION = 10  # presidencial


def _process_file(path_str: str) -> dict:
    try:
        with gzip.open(path_str, "rb") as fh:
            d = json.loads(fh.read())
    except Exception:
        return {}

    data = d.get("data") or []
    result: dict = {}
    for acta in data:
        if acta.get("idEleccion") != ID_ELECCION:
            continue
        estado = acta.get("estadoActa", "?")
        ubigeo = acta.get("idUbigeo", 0)
        electores = acta.get("totalElectoresHabiles") or 0
        result = {
            "estado": estado,
            "ubigeo": ubigeo,
            "electores": electores,
            "codigo": acta.get("codigoMesa", ""),
        }
        break  # una acta presidencial por mesa

    return result


def _find_latest_ts() -> str | None:
    caps = sorted(ROOT.glob("captures/*/mesas"), key=lambda p: p.parent.name, reverse=True)
    for cap in caps:
        files = list(cap.glob("*.json.gz"))
        if len(files) > 1000:
            return cap.parent.name
    return None


def run(ts: str | None = None) -> dict:
    if ts is None:
        ts = _find_latest_ts()
        if ts is None:
            print("ERROR: no captura mesa-a-mesa con >1k archivos", file=sys.stderr)
            sys.exit(1)

    mesas_dir = ROOT / "captures" / ts / "mesas"
    files = sorted(str(p) for p in mesas_dir.glob("*.json.gz"))
    n_files = len(files)
    print(f"[MESA-01] ts={ts}  archivos={n_files:,}")

    workers = min(cpu_count(), 8)
    estado_count: Counter = Counter()
    ubigeo_imp: Counter = Counter()       # ubigeo → n mesas impugnadas
    electores_imp: Counter = Counter()    # ubigeo → electores impugnadas
    electores_total: int = 0
    electores_imp_total: int = 0

    with Pool(processes=workers) as pool:
        for i, r in enumerate(pool.imap_unordered(_process_file, files, chunksize=500)):
            if not r:
                continue
            estado = r["estado"]
            estado_count[estado] += 1
            electores_total += r["electores"]
            if estado == "I":
                ubigeo_imp[r["ubigeo"]] += 1
                electores_imp[r["ubigeo"]] += r["electores"]
                electores_imp_total += r["electores"]
            if i % 10000 == 0 and i:
                print(f"  {i:>6}/{n_files}  imp={estado_count['I']}", flush=True)

    n_imp = estado_count["I"]
    n_total = sum(estado_count.values())
    pct_imp = round(100 * n_imp / n_total, 2) if n_total else 0

    # Top ubigeos por mesas impugnadas
    top_ubigeo = [
        {"ubigeo": u, "mesas_imp": c, "electores_imp": electores_imp[u]}
        for u, c in ubigeo_imp.most_common(20)
    ]

    # Electores en mesas impugnadas como múltiplo del margen
    meta_path = ROOT / "data" / "processed" / "meta.json"
    margen = None
    margen_pct = None
    ratio_electores_vs_margen = None
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        margen = meta.get("margen_sanch_rla_votos")
        margen_pct = meta.get("margen_sanch_rla_pct")
        if margen and electores_imp_total:
            ratio_electores_vs_margen = round(electores_imp_total / margen, 1)

    findings = []

    sev = "CRÍTICO" if pct_imp > 5 else "MEDIA" if pct_imp > 2 else "INFO"
    findings.append({
        "id": "MESA-IMP-1",
        "severity": sev,
        "test": "Mesas impugnadas (estadoActa=I) universo walker",
        "h0": "Proporción impugnadas no excede umbral procesal 5%",
        "statistic": pct_imp,
        "p_value": None,
        "threshold": 5.0,
        "interpretation": (
            f"{n_imp:,} mesas impugnadas de {n_total:,} ({pct_imp}%). "
            f"Electores hábiles en mesas impugnadas: {electores_imp_total:,}."
        ),
        "limitations": "adVotos=null en impugnadas — desglose candidato no disponible hasta resolución JEE.",
    })

    if ratio_electores_vs_margen:
        sev2 = "CRÍTICO" if ratio_electores_vs_margen > 2 else "MEDIA"
        findings.append({
            "id": "MESA-IMP-2",
            "severity": sev2,
            "test": "Electores impugnados vs margen vigente",
            "h0": "Electores en mesas impugnadas < margen vigente",
            "statistic": ratio_electores_vs_margen,
            "p_value": None,
            "threshold": 1.0,
            "interpretation": (
                f"Electores hábiles en {n_imp:,} mesas impugnadas: {electores_imp_total:,}. "
                f"Margen Sánchez−RLA: {margen:,} votos. "
                f"Ratio: {ratio_electores_vs_margen}× — si el resultado de mesas impugnadas "
                "difiriese del promedio nacional, podría alterar el margen."
            ),
            "limitations": (
                "Electores hábiles ≠ votos efectivos (participación ~73%). "
                "Impugnación es recurso procesal estándar. ONPE debe explicar concentración."
            ),
        })

    out = {
        "method": "Análisis mesas estadoActa=I desde walker 88k (MESA-01)",
        "capture_ts_utc": ts,
        "n_archivos_walker": n_files,
        "estado_distribution": dict(estado_count),
        "n_impugnadas": n_imp,
        "n_total_mesas": n_total,
        "pct_impugnadas": pct_imp,
        "electores_habiles_impugnadas": electores_imp_total,
        "electores_habiles_total": electores_total,
        "margen_sanchez_rla_votos": margen,
        "margen_sanchez_rla_pct": margen_pct,
        "ratio_electores_imp_vs_margen": ratio_electores_vs_margen,
        "top20_ubigeo_impugnadas": top_ubigeo,
        "hallazgos": findings,
        "caveat": (
            "estadoActa=I = acta enviada al JEE para resolución. "
            "Puede resolverse a favor o en contra de cualquier candidato. ONPE debe explicar."
        ),
    }

    out_path = ROOT / "reports" / "mesa_impugnadas.json"
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nOK → {out_path.relative_to(ROOT)}")
    print(f"   {n_imp:,} impugnadas / {n_total:,} mesas ({pct_imp}%)")
    print(f"   electores en juego: {electores_imp_total:,}")
    if ratio_electores_vs_margen:
        print(f"   ratio vs margen: {ratio_electores_vs_margen}×")

    return out


def main() -> None:
    ts = sys.argv[1] if len(sys.argv) > 1 else None
    run(ts)


if __name__ == "__main__":
    main()
