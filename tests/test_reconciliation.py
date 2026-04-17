"""
tests/test_reconciliation.py

Verifica que la reconciliación regional↔nacional funcione sobre la captura inicial.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


def test_build_dataset_runs():
    """El pipeline de build_dataset debe ejecutarse sin errores."""
    result = subprocess.run(
        [sys.executable, str(ROOT / "src/process/build_dataset.py")],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert result.returncode == 0, f"build_dataset falló:\n{result.stderr}"
    assert (ROOT / "data/processed/regiones.csv").exists()
    assert (ROOT / "data/processed/meta.json").exists()


def test_reconciliation_within_rounding():
    """La diferencia regional↔nacional debe ser < 0.5%."""
    meta_path = ROOT / "data/processed/meta.json"
    if not meta_path.exists():
        pytest.skip("meta.json no existe; ejecutar build_dataset primero")

    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    # consistency_issues debe estar vacío
    assert meta.get("consistency_issues") == [], (
        f"Hay inconsistencias: {meta['consistency_issues']}"
    )


def test_meta_has_required_fields():
    meta_path = ROOT / "data/processed/meta.json"
    if not meta_path.exists():
        pytest.skip("meta.json no existe; ejecutar build_dataset primero")

    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    required = ["pct_global", "actas_total", "enviadas_jee",
                "margen_sanch_rla_votos", "n_regiones"]
    for k in required:
        assert k in meta, f"falta clave: {k}"
