"""
Tests TDD para reconcile_national_vs_regional.py
"""

import json
from pathlib import Path

import pytest

from src.analysis.reconcile_national_vs_regional import (
    run,
    _load_snapshot,
    _compare_metrics,
)
from src.models.findings import ReconcileResult


@pytest.fixture
def mock_snap_data() -> dict:
    """Mock snapshot con estructura del snap1.json viejo."""
    return {
        "national": {
            "totalActas": 92766,
            "contabilizadas": 86712,
            "enviadasJee": 5763,
            "pendientesJee": 291,
        },
        "regions": [
            {
                "name": "Lima",
                "totalActas": 15000,
                "contabilizadas": 14000,
                "enviadasJee": 900,
            },
            {
                "name": "Arequipa",
                "totalActas": 4215,
                "contabilizadas": 4127,
                "enviadasJee": 88,
            },
        ],
    }


@pytest.fixture
def tmp_capture_dir(tmp_path):
    """Crea directorio de captura temporal con snap1.json."""
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    return tmp_path, raw_dir


def test_load_snapshot_success(tmp_capture_dir, mock_snap_data):
    """Carga correcta de snap*.json"""
    _, raw_dir = tmp_capture_dir
    snap_file = raw_dir / "snap1.json"
    snap_file.write_text(json.dumps(mock_snap_data), encoding="utf-8")

    result = _load_snapshot(raw_dir)
    assert result is not None
    assert result["national"]["totalActas"] == 92766
    assert len(result["regions"]) == 2


def test_load_snapshot_missing():
    """Retorna None si no hay snap*.json"""
    result = _load_snapshot(Path("/nonexistent"))
    assert result is None


def test_compare_metrics_within_threshold(mock_snap_data):
    """Diferencia dentro de threshold → Finding INFO"""
    # Ajustamos para que todas las métricas regionales sumen igual a nacional
    # Total regional: 15000 + 4215 = 19215
    mock_snap_data["national"]["totalActas"] = 19215
    mock_snap_data["national"]["contabilizadas"] = 18127
    mock_snap_data["national"]["enviadasJee"] = 1088
    mock_snap_data["national"]["pendientesJee"] = 0

    mock_snap_data["regions"][0]["totalActas"] = 15000
    mock_snap_data["regions"][0]["contabilizadas"] = 14000
    mock_snap_data["regions"][0]["enviadasJee"] = 1000

    mock_snap_data["regions"][1]["totalActas"] = 4215
    mock_snap_data["regions"][1]["contabilizadas"] = 4127
    mock_snap_data["regions"][1]["enviadasJee"] = 88

    result = _compare_metrics(mock_snap_data)
    assert result["severity"] == "INFO"
    assert "totalActas" in result["metrics"]
    # Verificar que todas las diferencias están dentro de los umbrales
    for m, vals in result["metrics"].items():
        assert not vals["alert"], f"{m} debería estar dentro de threshold"


def test_compare_metrics_exceeds_threshold(mock_snap_data):
    """Diferencia mayor a threshold → Finding CRÍTICO"""
    # Forzamos diferencia grande en totalActas
    mock_snap_data["national"]["totalActas"] = 100000
    # Regiones: 15000 + 4215 = 19215
    # Diferencia: 100000 - 19215 = 80785 (80%+)

    result = _compare_metrics(mock_snap_data)
    assert result["severity"] == "CRÍTICO"


def test_run_reconcile_integration(tmp_capture_dir, mock_snap_data):
    """Test de integración: load, compare, save"""
    tmp_path, raw_dir = tmp_capture_dir
    snap_file = raw_dir / "snap1.json"
    snap_file.write_text(json.dumps(mock_snap_data), encoding="utf-8")

    # Escribir meta.json para que run() pueda encontrar la captura
    data_dir = tmp_path / "data" / "processed"
    data_dir.mkdir(parents=True)
    meta_file = data_dir / "meta.json"
    meta_file.write_text(
        json.dumps({"capture_dir": "."}),
        encoding="utf-8"
    )

    # Pasar root directamente
    result = run(root=tmp_path)

    assert isinstance(result, ReconcileResult)
    assert result.findings is not None
    assert len(result.findings) > 0
    assert result.capture_ts is not None
    assert result.status in ["OK", "WARN", "ERROR"]

    # Verifica que se guardó el JSON
    output_file = tmp_path / "reports" / "reconcile_national_regional.json"
    assert output_file.exists()
    saved = json.loads(output_file.read_text(encoding="utf-8"))
    assert "findings" in saved
    assert saved["status"] == result.status


def test_run_no_snapshot(tmp_capture_dir):
    """Maneja gracefully si no hay snap*.json"""
    tmp_path, _ = tmp_capture_dir

    # Crear meta.json para que run() encuentre la captura
    data_dir = tmp_path / "data" / "processed"
    data_dir.mkdir(parents=True)
    meta_file = data_dir / "meta.json"
    meta_file.write_text(json.dumps({"capture_dir": "raw"}), encoding="utf-8")

    result = run(root=tmp_path)
    assert isinstance(result, ReconcileResult)
    assert result.findings[0].severity in ["INFO", "CRÍTICO"]
    assert result.status in ["OK", "WARN", "ERROR"]


def test_cli_main(tmp_capture_dir, mock_snap_data, capsys):
    """Test CLI invocación con --root"""
    from src.analysis.reconcile_national_vs_regional import main
    import sys

    tmp_path, raw_dir = tmp_capture_dir
    snap_file = raw_dir / "snap1.json"
    snap_file.write_text(json.dumps(mock_snap_data), encoding="utf-8")

    # Escribir meta.json
    data_dir = tmp_path / "data" / "processed"
    data_dir.mkdir(parents=True)
    meta_file = data_dir / "meta.json"
    meta_file.write_text(
        json.dumps({"capture_dir": "."}),
        encoding="utf-8"
    )

    # Simula sys.argv para argparse
    old_argv = sys.argv
    try:
        sys.argv = [
            "reconcile_national_vs_regional.py",
            "--root", str(tmp_path),
        ]
        main()
        captured = capsys.readouterr()
        assert "RECONCILIACIÓN" in captured.out.upper()
    finally:
        sys.argv = old_argv
