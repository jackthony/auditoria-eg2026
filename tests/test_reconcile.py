"""
RED tests — PYDANTIC-01 / reconcile
Fallarán con ImportError hasta que existan:
  src/models/findings.py
  src/analysis/reconcile_national_vs_regional.py
"""
import json
import pathlib

import pytest

from src.analysis.reconcile_national_vs_regional import (  # noqa: E402
    run_reconcile,
    ReconcileResult,
)
from src.models.findings import Finding  # noqa: E402

from tests.fixtures.onpe_sample import *  # noqa: F401,F403


_REPORT_PATH = pathlib.Path(__file__).parents[1] / "reports" / "reconcile_national_regional.json"


# ===========================================================================
# Helpers
# ===========================================================================

def _build_national(pct: float, votes: int) -> dict:
    """Crea un national dict mínimo compatible con snap viejo."""
    return {
        "pct": pct,
        "totalActas": 92766,
        "contabilizadas": 86748,
        "candidates": {
            "rla": pct,
            "rla_v": votes,
        },
        "candidateVotes": {"rla": votes},
    }


def _build_regions(pcts_votes: list[tuple[float, int]]) -> list[dict]:
    """Crea lista de regiones mínimas con porcentaje RLA y votos."""
    return [
        {
            "name": f"Region{i}",
            "pct": 93.0,
            "vv": v,
            "totalActas": 100,
            "contabilizadas": 93,
            "rla": p,
            "rla_v": v,
        }
        for i, (p, v) in enumerate(pcts_votes)
    ]


# ===========================================================================
# run_reconcile — caso OK (national == sum regions)
# ===========================================================================

class TestRunReconcileOk:
    def test_returns_reconcile_result(self, snap_national: dict, snap_regions: list[dict]) -> None:
        result = run_reconcile(snap_national, snap_regions)
        assert isinstance(result, ReconcileResult)

    def test_findings_is_list_of_finding(self, snap_national: dict, snap_regions: list[dict]) -> None:
        result = run_reconcile(snap_national, snap_regions)
        assert isinstance(result.findings, list)
        for f in result.findings:
            assert isinstance(f, Finding)

    def test_balanced_data_produces_info_severity(self) -> None:
        """national == sum(regions) en votos RLA → Finding INFO."""
        total_votes = 100_000
        national = _build_national(pct=12.0, votes=total_votes)
        regions = _build_regions([(12.0, 60_000), (12.0, 40_000)])
        result = run_reconcile(national, regions)
        severities = {f.severity for f in result.findings}
        assert "INFO" in severities
        assert "CRÍTICO" not in severities

    def test_no_mutation_of_inputs(self, snap_national: dict, snap_regions: list[dict]) -> None:
        """run_reconcile no muta los dicts de entrada."""
        import copy
        national_copy = copy.deepcopy(snap_national)
        regions_copy = copy.deepcopy(snap_regions)
        run_reconcile(snap_national, snap_regions)
        assert snap_national == national_copy
        assert snap_regions == regions_copy


# ===========================================================================
# run_reconcile — descuadre > 0.1pp → CRÍTICO
# ===========================================================================

class TestRunReconcileDescuadre:
    def test_diff_greater_than_threshold_raises_critico(self) -> None:
        """Diferencia de 2pp entre national y sum(regions) → Finding CRÍTICO."""
        national = _build_national(pct=12.0, votes=120_000)
        # regions suman 100_000 votos pero national dice 120_000 → diff 20%
        regions = _build_regions([(10.0, 50_000), (10.0, 50_000)])
        result = run_reconcile(national, regions)
        severities = {f.severity for f in result.findings}
        assert "CRÍTICO" in severities

    def test_finding_contains_statistic(self) -> None:
        national = _build_national(pct=12.0, votes=120_000)
        regions = _build_regions([(10.0, 50_000), (10.0, 50_000)])
        result = run_reconcile(national, regions)
        criticos = [f for f in result.findings if f.severity == "CRÍTICO"]
        assert len(criticos) >= 1
        assert criticos[0].statistic is not None

    def test_finding_has_sha256(self, snap_national: dict, snap_regions: list[dict]) -> None:
        result = run_reconcile(snap_national, snap_regions)
        for f in result.findings:
            assert isinstance(f.captura_sha256, str)
            assert len(f.captura_sha256) > 0

    def test_diff_below_threshold_not_critico(self) -> None:
        """Diff < 0.1pp → NO CRÍTICO."""
        # Mismo valor exacto → diff 0
        national = _build_national(pct=12.0, votes=100_000)
        regions = _build_regions([(12.0, 60_000), (12.0, 40_000)])
        result = run_reconcile(national, regions)
        severities = {f.severity for f in result.findings}
        assert "CRÍTICO" not in severities


# ===========================================================================
# Output JSON en reports/
# ===========================================================================

class TestReconcileOutputJson:
    def test_output_file_is_valid_json(self, snap_national: dict, snap_regions: list[dict], tmp_path: pathlib.Path) -> None:
        """run_reconcile escribe JSON válido a reports/reconcile_national_regional.json."""
        out_path = tmp_path / "reconcile_national_regional.json"
        run_reconcile(snap_national, snap_regions, output_path=out_path)
        assert out_path.exists()
        data = json.loads(out_path.read_text(encoding="utf-8"))
        assert isinstance(data, list)

    def test_output_json_items_match_finding_schema(
        self, snap_national: dict, snap_regions: list[dict], tmp_path: pathlib.Path
    ) -> None:
        out_path = tmp_path / "reconcile_national_regional.json"
        run_reconcile(snap_national, snap_regions, output_path=out_path)
        items = json.loads(out_path.read_text(encoding="utf-8"))
        for item in items:
            # Debe poder parsearse como Finding sin error
            f = Finding(**item)
            assert f.captura_sha256 is not None

    def test_output_json_required_keys_present(
        self, snap_national: dict, snap_regions: list[dict], tmp_path: pathlib.Path
    ) -> None:
        out_path = tmp_path / "reconcile_national_regional.json"
        run_reconcile(snap_national, snap_regions, output_path=out_path)
        items = json.loads(out_path.read_text(encoding="utf-8"))
        required_keys = {"id", "severity", "test", "h0", "statistic", "threshold",
                         "interpretation", "limitations", "captura_sha256"}
        for item in items:
            assert required_keys.issubset(item.keys()), f"Faltan keys en {item}"


# ===========================================================================
# ReconcileResult — contrato del tipo
# ===========================================================================

class TestReconcileResult:
    def test_reconcile_result_has_findings_attr(self, snap_national: dict, snap_regions: list[dict]) -> None:
        result = run_reconcile(snap_national, snap_regions)
        assert hasattr(result, "findings")

    def test_reconcile_result_findings_all_valid_findings(
        self, snap_national: dict, snap_regions: list[dict]
    ) -> None:
        result = run_reconcile(snap_national, snap_regions)
        for f in result.findings:
            assert f.severity in {"CRÍTICO", "MEDIA", "BAJA", "INFO"}
            assert isinstance(f.id, str)
            assert isinstance(f.test, str)
