"""
src/analysis/extract_mesa_votes.py — Extrae CSV compacto mesa×agrupación desde walker.

Input:  captures/{ts}/mesas/*.json.gz
Output: reports/mesas_presidencial.csv
        reports/mesas_summary.json

Filtro: solo idEleccion=10 (presidencial).
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

ID_ELECCION_PRESIDENCIAL = 10


def is_special(nombre: str) -> bool:
    n = (nombre or "").upper()
    return "BLANCO" in n or "NULO" in n


def extract(capture_ts: str, id_eleccion: int = ID_ELECCION_PRESIDENCIAL) -> dict:
    ROOT = Path(__file__).resolve().parents[2]
    mesas_dir = ROOT / "captures" / capture_ts / "mesas"
    if not mesas_dir.exists():
        print(f"ERROR: {mesas_dir} no existe", file=sys.stderr)
        sys.exit(2)

    out_csv = ROOT / "reports" / "mesas_presidencial.csv"
    out_csv.parent.mkdir(exist_ok=True)

    # Nacional
    votos_por_agrup: Counter = Counter()
    blanco_total = 0
    nulo_total = 0
    # Por mesa
    mesas_contabilizadas = 0
    mesas_observadas = 0
    mesas_pendientes = 0
    mesas_otros = 0
    total_validos_sum = 0
    total_emitidos_sum = 0
    total_electores_sum = 0
    mesas_procesadas = 0
    mesas_sin_data = 0
    # Estado por ubigeo (para finding #3 desfase geográfico)
    por_ubigeo = defaultdict(lambda: Counter())

    writer = csv.writer(out_csv.open("w", encoding="utf-8", newline=""))
    writer.writerow([
        "codigoMesa", "idUbigeo", "estado", "totalElectores", "totalEmitidos",
        "totalValidos", "agrupacion", "votos", "pctValidos",
    ])

    files = sorted(mesas_dir.glob("*.json.gz"))
    print(f"[extract] {len(files)} archivos en {mesas_dir}")

    for i, fp in enumerate(files):
        try:
            data = json.loads(gzip.decompress(fp.read_bytes()))
        except Exception as e:
            print(f"  WARN {fp.name}: {e}", file=sys.stderr)
            continue
        if not data.get("success"):
            continue
        items = data.get("data") or []
        presi = next((it for it in items if it.get("idEleccion") == id_eleccion), None)
        if presi is None:
            mesas_sin_data += 1
            continue

        codigo = presi.get("codigoMesa")
        ubigeo = presi.get("idUbigeo")
        estado = presi.get("descripcionEstadoActa") or "?"
        total_electores = presi.get("totalElectoresHabiles") or 0
        total_emitidos = presi.get("totalVotosEmitidos") or 0
        total_validos = presi.get("totalVotosValidos") or 0

        mesas_procesadas += 1
        if estado == "Contabilizada":
            mesas_contabilizadas += 1
        elif estado == "Para envío al JEE":
            mesas_observadas += 1
        elif "Pendiente" in estado:
            mesas_pendientes += 1
        else:
            mesas_otros += 1

        total_validos_sum += total_validos
        total_emitidos_sum += total_emitidos
        total_electores_sum += total_electores

        detalle = presi.get("detalle") or []
        for d in detalle:
            nombre = d.get("adDescripcion") or ""
            votos = d.get("adVotos") or 0
            if not nombre:
                continue
            pct = d.get("adPorcentajeVotosValidos")
            writer.writerow([codigo, ubigeo, estado, total_electores,
                             total_emitidos, total_validos, nombre, votos,
                             pct if pct is not None else ""])
            if is_special(nombre):
                if "BLANCO" in nombre.upper():
                    blanco_total += votos
                else:
                    nulo_total += votos
            else:
                votos_por_agrup[nombre] += votos
                por_ubigeo[ubigeo][nombre] += votos

        if (i + 1) % 10000 == 0:
            print(f"  {i+1}/{len(files)}  procesadas={mesas_procesadas} "
                  f"contab={mesas_contabilizadas} observ={mesas_observadas}")

    # Top 10 nacional
    top10 = votos_por_agrup.most_common(10)
    total_validos_mesa = sum(votos_por_agrup.values())
    total_emitidos_mesa = total_validos_mesa + blanco_total + nulo_total

    summary = {
        "capture_ts": capture_ts,
        "id_eleccion": id_eleccion,
        "archivos_totales": len(files),
        "mesas_procesadas": mesas_procesadas,
        "mesas_sin_data_presidencial": mesas_sin_data,
        "mesas_contabilizadas": mesas_contabilizadas,
        "mesas_observadas_jee": mesas_observadas,
        "mesas_pendientes": mesas_pendientes,
        "mesas_otros_estado": mesas_otros,
        "suma_mesa_total_electores": total_electores_sum,
        "suma_mesa_total_emitidos": total_emitidos_sum,
        "suma_mesa_total_validos": total_validos_sum,
        "suma_detalle_validos": total_validos_mesa,
        "suma_detalle_blancos": blanco_total,
        "suma_detalle_nulos": nulo_total,
        "suma_detalle_emitidos": total_emitidos_mesa,
        "delta_validos_vs_detalle": total_validos_sum - total_validos_mesa,
        "top10_agrupaciones": [
            {"agrupacion": n, "votos": v,
             "pct_validos": round(v / total_validos_mesa * 100, 3) if total_validos_mesa else 0}
            for n, v in top10
        ],
        "ubigeos_con_mesas": len(por_ubigeo),
    }

    out_json = ROOT / "reports" / "mesas_summary.json"
    out_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print()
    print(f"[extract] {mesas_procesadas} mesas procesadas")
    print(f"[extract] contabilizadas: {mesas_contabilizadas}")
    print(f"[extract] observadas JEE: {mesas_observadas}")
    print(f"[extract] suma válidos mesa-a-mesa: {total_validos_mesa:,}")
    print(f"[extract] blancos: {blanco_total:,}  nulos: {nulo_total:,}")
    print()
    print("TOP 10 presidencial (mesa-a-mesa):")
    for n, v in top10:
        pct = v / total_validos_mesa * 100 if total_validos_mesa else 0
        print(f"  {pct:>6.2f}%  {v:>10,}  {n[:60]}")
    print()
    print(f"[extract] CSV: {out_csv}")
    print(f"[extract] JSON: {out_json}")
    return summary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("ts", help="captura ts, ej. 20260419T035056Z")
    ap.add_argument("--eleccion", type=int, default=ID_ELECCION_PRESIDENCIAL)
    args = ap.parse_args()
    extract(args.ts, args.eleccion)
    return 0


if __name__ == "__main__":
    sys.exit(main())
