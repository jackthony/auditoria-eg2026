"""Tests forenses MESA-MATRIX-01: schema + invariantes contables + guardrail."""
from __future__ import annotations

import gzip
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from src.process.models_mesa import Detalle, MesaRecord
from src.process.build_mesa_candidate_matrix import build, parse_mesa

FIXT = Path(__file__).parent / "fixtures" / "mesas"


def load_row(idx: int = 0, eleccion: int = 10) -> dict:
    fp = FIXT / "000001.json.gz"
    data = json.loads(gzip.open(fp).read())
    rows = [r for r in data["data"] if r["idEleccion"] == eleccion]
    return rows[idx]


def test_schema_valid_real_mesa() -> None:
    row = load_row()
    mesa = MesaRecord.model_validate(row)
    assert mesa.codigoMesa == "000001"
    assert mesa.idEleccion == 10
    assert len(mesa.detalle) == 41


def test_detalle_acepta_votos_none() -> None:
    d = Detalle(adAgrupacionPolitica=1, adCodigo="X", adDescripcion="Y", adVotos=None, adTotalVotosValidos=0)
    assert d.adVotos is None


def test_rechaza_votos_negativos() -> None:
    with pytest.raises(ValidationError):
        Detalle(adAgrupacionPolitica=1, adCodigo="X", adDescripcion="Y", adVotos=-1, adTotalVotosValidos=0)


def test_rechaza_emitidos_gt_habiles() -> None:
    row = load_row()
    row["totalVotosEmitidos"] = (row["totalElectoresHabiles"] or 0) + 1
    with pytest.raises(ValidationError):
        MesaRecord.model_validate(row)


def test_rechaza_validos_gt_emitidos() -> None:
    row = load_row()
    row["totalVotosValidos"] = (row["totalVotosEmitidos"] or 0) + 1
    with pytest.raises(ValidationError):
        MesaRecord.model_validate(row)


def test_acepta_mesa_sin_escrutar() -> None:
    row = load_row()
    row["totalVotosEmitidos"] = None
    row["totalVotosValidos"] = None
    mesa = MesaRecord.model_validate(row)
    assert mesa.totalVotosEmitidos is None


def test_invariante_suma_detalle_igual_emitidos() -> None:
    row = load_row()
    mesa = MesaRecord.model_validate(row)
    suma = sum(d.adVotos or 0 for d in mesa.detalle)
    assert abs(suma - mesa.totalVotosEmitidos) <= 2


def test_rechaza_suma_inconsistente() -> None:
    row = load_row()
    row["detalle"][0]["adVotos"] = (row["detalle"][0]["adVotos"] or 0) + 100
    with pytest.raises(ValidationError):
        MesaRecord.model_validate(row)


def test_parse_mesa_ok() -> None:
    row = load_row()
    mesa, err = parse_mesa(row)
    assert err is None
    assert mesa is not None and mesa.codigoMesa == "000001"


def test_parse_mesa_err() -> None:
    row = load_row()
    row["totalVotosEmitidos"] = 999_999
    mesa, err = parse_mesa(row)
    assert mesa is None
    assert err and "emitidos" in err.lower() or "validos" in err.lower() or "habiles" in err.lower()


def test_build_produce_csv_y_integrity(tmp_path: Path) -> None:
    out = tmp_path / "out"
    report = build(capture_dir=FIXT, eleccion=10, outdir=out,
                   integrity_path=tmp_path / "integrity.json", max_err_ratio=0.01)
    assert (out / "mesa_candidato_long.csv").exists()
    assert (out / "mesa_totales.csv").exists()
    assert report["n_ok"] >= 1
    assert report["ratio_err"] == 0.0


def test_build_guardrail_aborta_si_err_gt_umbral(tmp_path: Path) -> None:
    bad_dir = tmp_path / "mesas"
    bad_dir.mkdir()
    good = gzip.open(FIXT / "000001.json.gz").read()
    (bad_dir / "000001.json.gz").write_bytes(good)
    payload = json.loads(good)
    for r in payload["data"]:
        r["totalVotosEmitidos"] = 999_999
    import io
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb") as gz:
        gz.write(json.dumps(payload).encode())
    (bad_dir / "000002.json.gz").write_bytes(buf.getvalue())

    with pytest.raises(SystemExit):
        build(capture_dir=bad_dir, eleccion=10, outdir=tmp_path / "out",
              integrity_path=tmp_path / "integrity.json", max_err_ratio=0.01)
