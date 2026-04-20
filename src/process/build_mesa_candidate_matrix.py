"""Agrega votos mesa x candidato con Pydantic + guardrail de integridad.

Salida:
  {outdir}/mesa_candidato_long.csv
  {outdir}/mesa_totales.csv
  reports/mesa_matrix_integrity.json

Guardrail: si ratio_err > max_err_ratio -> SystemExit(2).

Uso:
  py -m src.process.build_mesa_candidate_matrix --ts 20260419T035056Z [--eleccion 10]
"""
from __future__ import annotations

import argparse
import csv
import glob
import gzip
import json
import logging
import sys
from pathlib import Path
from typing import Iterable

from pydantic import ValidationError

from src.process.models_mesa import Detalle, MesaRecord

logger = logging.getLogger(__name__)

MESA_FIELDS = [
    "codigoMesa", "idUbigeo", "idEleccion", "estadoActa", "codigoEstadoActa",
    "descripcionEstadoActa", "totalElectoresHabiles", "totalVotosEmitidos",
    "totalVotosValidos", "totalAsistentes", "porcentajeParticipacionCiudadana",
    "nombreLocalVotacion", "codigoLocalVotacion",
]
DET_FIELDS = [
    "adAgrupacionPolitica", "adCodigo", "adDescripcion",
    "adVotos", "adTotalVotosValidos",
]


def parse_mesa(row: dict) -> tuple[MesaRecord | None, str | None]:
    try:
        return MesaRecord.model_validate(row), None
    except ValidationError as e:
        first = e.errors()[0] if e.errors() else {}
        msg = first.get("msg", "validation error")
        return None, msg


def iter_raw_rows(capture_dir: Path, eleccion: int | None) -> Iterable[dict]:
    for fp in sorted(glob.glob(str(capture_dir / "*.json.gz"))):
        try:
            payload = json.loads(gzip.open(fp).read())
        except (OSError, json.JSONDecodeError) as e:
            logger.warning("skip %s: %s", fp, e)
            continue
        for row in payload.get("data", []):
            if eleccion is not None and row.get("idEleccion") != eleccion:
                continue
            yield row


def _write_row(w_long, w_tot, mesa: MesaRecord) -> None:
    base = [getattr(mesa, k, None) for k in MESA_FIELDS]
    w_tot.writerow(base)
    for d in mesa.detalle:
        w_long.writerow(base + [getattr(d, k, None) for k in DET_FIELDS])


def build(
    capture_dir: Path,
    eleccion: int | None,
    outdir: Path,
    integrity_path: Path,
    max_err_ratio: float = 0.01,
) -> dict:
    outdir.mkdir(parents=True, exist_ok=True)
    integrity_path.parent.mkdir(parents=True, exist_ok=True)
    long_path = outdir / "mesa_candidato_long.csv"
    tot_path = outdir / "mesa_totales.csv"

    n_ok = 0
    errores: list[dict] = []

    with open(long_path, "w", newline="", encoding="utf-8") as fl, \
         open(tot_path, "w", newline="", encoding="utf-8") as ft:
        wl = csv.writer(fl, delimiter=";")
        wt = csv.writer(ft, delimiter=";")
        wl.writerow(MESA_FIELDS + DET_FIELDS)
        wt.writerow(MESA_FIELDS)

        for row in iter_raw_rows(capture_dir, eleccion):
            mesa, err = parse_mesa(row)
            if mesa is None:
                errores.append({"codigoMesa": row.get("codigoMesa"), "motivo": err})
                continue
            _write_row(wl, wt, mesa)
            n_ok += 1

    total = n_ok + len(errores)
    ratio = len(errores) / total if total else 0.0
    report = {
        "capture_dir": str(capture_dir),
        "eleccion": eleccion,
        "n_ok": n_ok,
        "n_err": len(errores),
        "ratio_err": ratio,
        "max_err_ratio": max_err_ratio,
        "errores": errores[:50],
    }
    integrity_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    if ratio > max_err_ratio:
        logger.error("Guardrail: ratio_err=%.3f > %.3f", ratio, max_err_ratio)
        sys.exit(2)

    return report


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ts", required=True)
    ap.add_argument("--eleccion", type=int, default=10)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--outdir", default="data/processed")
    ap.add_argument("--integrity", default="reports/mesa_matrix_integrity.json")
    ap.add_argument("--max-err-ratio", type=float, default=0.01)
    args = ap.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    report = build(
        capture_dir=Path(f"captures/{args.ts}/mesas"),
        eleccion=None if args.all else args.eleccion,
        outdir=Path(args.outdir),
        integrity_path=Path(args.integrity),
        max_err_ratio=args.max_err_ratio,
    )
    print(f"ok={report['n_ok']} err={report['n_err']} ratio={report['ratio_err']:.4f}")


if __name__ == "__main__":
    main()
