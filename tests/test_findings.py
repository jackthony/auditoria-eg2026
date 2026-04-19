"""Tests para src.models.findings — Pydantic v2, frozen=True."""

import json
import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.models.findings import Finding, ReconcileResult, load_findings, dump_findings, Severity


class TestFinding:
    """Validación de modelo Finding."""

    def test_finding_creation_minimal(self) -> None:
        """Crea Finding con campos obligatorios."""
        f = Finding(
            id="A0",
            severity="INFO",
            test="reconciliacion_nacional_regional",
            h0="suma_regional == total_nacional",
            interpretation="Diferencia menor a 0.01%, aceptable",
            limitations="No valida cambios en mesas individuales",
            captura_sha256="abc123def456",
            captura_ts="2026-04-19T12:00:00Z",
        )
        assert f.id == "A0"
        assert f.severity == "INFO"
        assert f.statistic is None
        assert f.p_value is None

    def test_finding_with_statistics(self) -> None:
        """Finding con estadísticos completos."""
        f = Finding(
            id="F1",
            severity="MEDIA",
            test="benford_1_digito",
            h0="primer dígito sigue Benford",
            interpretation="χ² = 11.9, p = 0.155 → no rechaza H0",
            limitations="Benford no es test único de fraude",
            captura_sha256="xyz789",
            captura_ts="2026-04-19T00:00:00Z",
            statistic=11.905763860152753,
            p_value=0.15545825418443593,
            threshold=0.05,
            method="χ² Benford-1 (gl=8)",
        )
        assert f.p_value == pytest.approx(0.155458, rel=1e-4)
        assert f.threshold == 0.05
        assert f.method == "χ² Benford-1 (gl=8)"

    def test_finding_frozen_immutable(self) -> None:
        """Finding es frozen → no permite mutación."""
        f = Finding(
            id="E1",
            severity="CRÍTICO",
            test="margen_2vuelta",
            h0="margen > votos_en_disputa",
            interpretation="margen = 13624 votos",
            limitations="Requiere resolución JEE",
            captura_sha256="sha256_e1",
            captura_ts="2026-04-19T10:00:00Z",
        )

        with pytest.raises(Exception):  # FrozenInstanceError
            f.severity = "MEDIA"  # type: ignore

    def test_severity_validation(self) -> None:
        """Solo severidades permitidas."""
        valid_sev: Severity
        for sev in ["CRÍTICO", "MEDIA", "BAJA", "INFO"]:
            Finding(
                id="T1",
                severity=sev,  # type: ignore
                test="test",
                h0="h0",
                interpretation="interp",
                limitations="lim",
                captura_sha256="sha",
                captura_ts="2026-04-19T00:00:00Z",
            )

        # severidad inválida
        with pytest.raises(ValueError):
            Finding(
                id="T1",
                severity="INVALID",  # type: ignore
                test="test",
                h0="h0",
                interpretation="interp",
                limitations="lim",
                captura_sha256="sha",
                captura_ts="2026-04-19T00:00:00Z",
            )

    def test_extra_fields_ignored(self) -> None:
        """ConfigDict(extra='ignore') ignora campos extra."""
        f = Finding(
            id="X1",
            severity="INFO",
            test="test",
            h0="h0",
            interpretation="interp",
            limitations="lim",
            captura_sha256="sha",
            captura_ts="2026-04-19T00:00:00Z",
            extra_field="ignored",  # type: ignore
        )
        assert not hasattr(f, "extra_field")


class TestReconcileResult:
    """Validación de ReconcileResult."""

    def test_reconcile_result_creation(self) -> None:
        """Crea ReconcileResult con findings."""
        findings = [
            Finding(
                id="R1",
                severity="INFO",
                test="sum_check",
                h0="suma == total",
                interpretation="OK",
                limitations="none",
                captura_sha256="sha1",
                captura_ts="2026-04-19T00:00:00Z",
            ),
            Finding(
                id="R2",
                severity="BAJA",
                test="drift_check",
                h0="sin drift significativo",
                interpretation="OK",
                limitations="none",
                captura_sha256="sha2",
                captura_ts="2026-04-19T00:00:00Z",
            ),
        ]

        result = ReconcileResult(
            findings=findings,
            capture_ts="2026-04-19T10:15:00Z",
            status="OK",
        )

        assert len(result.findings) == 2
        assert result.status == "OK"

    def test_reconcile_result_frozen(self) -> None:
        """ReconcileResult es frozen."""
        result = ReconcileResult(
            findings=[],
            capture_ts="2026-04-19T00:00:00Z",
            status="OK",
        )

        with pytest.raises(Exception):  # FrozenInstanceError
            result.status = "ERROR"  # type: ignore


class TestLoadDumpFindings:
    """Funciones load_findings y dump_findings."""

    def test_dump_and_load_roundtrip(self) -> None:
        """dump → load preserva datos."""
        findings = [
            Finding(
                id="F1",
                severity="CRÍTICO",
                test="test1",
                h0="h0_1",
                interpretation="int1",
                limitations="lim1",
                captura_sha256="sha1",
                captura_ts="2026-04-19T00:00:00Z",
                statistic=1.5,
                p_value=0.01,
                threshold=0.05,
                method="method1",
            ),
            Finding(
                id="F2",
                severity="INFO",
                test="test2",
                h0="h0_2",
                interpretation="int2",
                limitations="lim2",
                captura_sha256="sha2",
                captura_ts="2026-04-19T01:00:00Z",
            ),
        ]

        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "findings.json"

            # dump
            dump_findings(findings, path)
            assert path.exists()

            # load
            loaded = load_findings(path)
            assert len(loaded) == 2
            assert loaded[0].id == "F1"
            assert loaded[0].severity == "CRÍTICO"
            assert loaded[0].statistic == 1.5
            assert loaded[0].p_value == 0.01
            assert loaded[1].id == "F2"
            assert loaded[1].p_value is None

    def test_dump_creates_parent_dirs(self) -> None:
        """dump_findings crea directorios padre."""
        findings = [
            Finding(
                id="D1",
                severity="INFO",
                test="test",
                h0="h0",
                interpretation="int",
                limitations="lim",
                captura_sha256="sha",
                captura_ts="2026-04-19T00:00:00Z",
            ),
        ]

        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "a" / "b" / "c" / "findings.json"
            dump_findings(findings, path)
            assert path.exists()
            assert path.parent.exists()

    def test_load_file_not_found(self) -> None:
        """load_findings raise FileNotFoundError si no existe."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "nonexistent.json"
            with pytest.raises(FileNotFoundError):
                load_findings(path)

    def test_load_invalid_json(self) -> None:
        """load_findings raise json.JSONDecodeError si JSON inválido."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "bad.json"
            path.write_text("{ invalid json")

            with pytest.raises(json.JSONDecodeError):
                load_findings(path)

    def test_load_invalid_finding_schema(self) -> None:
        """load_findings raise ValueError si Finding no valida."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "bad_finding.json"
            bad_data = {
                "findings": [
                    {
                        "id": "F1",
                        "severity": "INVALID_SEV",  # inválido
                        "test": "test",
                        "h0": "h0",
                        "interpretation": "int",
                        "limitations": "lim",
                        "captura_sha256": "sha",
                        "captura_ts": "2026-04-19T00:00:00Z",
                    },
                ],
            }
            path.write_text(json.dumps(bad_data))

            with pytest.raises(ValueError):
                load_findings(path)

    def test_dump_json_format(self) -> None:
        """dump_findings genera JSON valido con structure correcta."""
        findings = [
            Finding(
                id="J1",
                severity="MEDIA",
                test="json_test",
                h0="h0",
                interpretation="int",
                limitations="lim",
                captura_sha256="sha",
                captura_ts="2026-04-19T00:00:00Z",
                statistic=42.0,
                p_value=0.001,
            ),
        ]

        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.json"
            dump_findings(findings, path)

            # validar JSON válido
            with open(path) as f:
                data = json.load(f)

            assert "findings" in data
            assert len(data["findings"]) == 1
            assert data["findings"][0]["id"] == "J1"
            assert data["findings"][0]["severity"] == "MEDIA"
            assert data["findings"][0]["statistic"] == 42.0
