"""
RED tests — PYDANTIC-01
Fallarán con ImportError hasta que existan src/models/onpe.py + src/models/findings.py
"""
import pytest
from pydantic import ValidationError

# Estas importaciones deben fallar (RED) hasta que se implementen los modelos
from src.models.onpe import (  # noqa: E402
    TotalesData,
    PresidencialItem,
    MapaCalorItem,
    ResumenEleccionItem,
    MesaTotales,
    ProcesoActivo,
    EleccionItem,
    UbigeoItem,
    OnpeResponse,
)
from src.models.findings import Finding, Severity  # noqa: E402

from tests.fixtures.onpe_sample import *  # noqa: F401,F403  (registra fixtures)


# ===========================================================================
# TotalesData
# ===========================================================================

class TestTotalesData:
    def test_parse_real_fixture(self, raw_totales: dict) -> None:
        payload = raw_totales["data"]
        model = TotalesData(**payload)
        assert model.contabilizadas == 86748
        assert model.totalActas == 92766
        assert isinstance(model.actasContabilizadas, float)

    def test_frozen_raises_on_mutation(self, raw_totales: dict) -> None:
        model = TotalesData(**raw_totales["data"])
        with pytest.raises((TypeError, AttributeError)):
            model.contabilizadas = 0  # type: ignore[misc]

    def test_extra_field_ignored(self, raw_totales: dict) -> None:
        payload = {**raw_totales["data"], "campo_fantasma": "x"}
        model = TotalesData(**payload)
        assert not hasattr(model, "campo_fantasma")

    def test_wrong_type_raises_validation_error(self) -> None:
        with pytest.raises(ValidationError):
            TotalesData(contabilizadas="no_es_int", totalActas="mal")  # type: ignore[arg-type]


# ===========================================================================
# PresidencialItem
# ===========================================================================

class TestPresidencialItem:
    def test_parse_real_fixture(self, raw_presidencial: dict) -> None:
        item = raw_presidencial["data"][0]
        model = PresidencialItem(**item)
        assert isinstance(model.nombreAgrupacionPolitica, str)
        assert isinstance(model.totalVotosValidos, int)
        assert 0.0 <= model.porcentajeVotosValidos <= 100.0

    def test_parse_all_38_items(self, raw_presidencial: dict) -> None:
        items = [PresidencialItem(**d) for d in raw_presidencial["data"]]
        assert len(items) == 38

    def test_frozen(self, raw_presidencial: dict) -> None:
        model = PresidencialItem(**raw_presidencial["data"][0])
        with pytest.raises((TypeError, AttributeError)):
            model.totalVotosValidos = 0  # type: ignore[misc]

    def test_extra_ignored(self, raw_presidencial: dict) -> None:
        payload = {**raw_presidencial["data"][0], "extra": True}
        PresidencialItem(**payload)  # no debe lanzar

    def test_wrong_type_raises(self) -> None:
        with pytest.raises(ValidationError):
            PresidencialItem(
                nombreAgrupacionPolitica=123,  # type: ignore[arg-type]
                codigoAgrupacionPolitica=None,  # type: ignore[arg-type]
                nombreCandidato=None,  # type: ignore[arg-type]
                dniCandidato=None,  # type: ignore[arg-type]
                totalVotosValidos="mal",  # type: ignore[arg-type]
                porcentajeVotosValidos="mal",  # type: ignore[arg-type]
                porcentajeVotosEmitidos="mal",  # type: ignore[arg-type]
            )


# ===========================================================================
# MapaCalorItem
# ===========================================================================

class TestMapaCalorItem:
    def test_parse_real_fixture(self, raw_mapa_calor: dict) -> None:
        item = raw_mapa_calor["data"][0]
        model = MapaCalorItem(**item)
        assert model.porcentajeActasContabilizadas == pytest.approx(93.513, rel=1e-3)
        assert model.actasContabilizadas == 86748
        # campos nullables deben ser None
        assert model.ambitoGeografico is None
        assert model.ubigeoNivel01 is None

    def test_frozen(self, raw_mapa_calor: dict) -> None:
        model = MapaCalorItem(**raw_mapa_calor["data"][0])
        with pytest.raises((TypeError, AttributeError)):
            model.actasContabilizadas = 0  # type: ignore[misc]

    def test_extra_ignored(self, raw_mapa_calor: dict) -> None:
        payload = {**raw_mapa_calor["data"][0], "raro": "z"}
        MapaCalorItem(**payload)


# ===========================================================================
# ResumenEleccionItem
# ===========================================================================

class TestResumenEleccionItem:
    def test_parse_real_fixture(self, raw_resumen_elecciones: dict) -> None:
        item = raw_resumen_elecciones["data"][0]
        model = ResumenEleccionItem(**item)
        assert model.id == 10
        assert model.nombre == "Presidencial"
        assert model.totalActas is None          # dato real: null
        assert isinstance(model.actasContabilizadas, int)

    def test_parse_all_5_items(self, raw_resumen_elecciones: dict) -> None:
        items = [ResumenEleccionItem(**d) for d in raw_resumen_elecciones["data"]]
        assert len(items) == 5

    def test_frozen(self, raw_resumen_elecciones: dict) -> None:
        model = ResumenEleccionItem(**raw_resumen_elecciones["data"][0])
        with pytest.raises((TypeError, AttributeError)):
            model.id = 99  # type: ignore[misc]

    def test_extra_ignored(self, raw_resumen_elecciones: dict) -> None:
        payload = {**raw_resumen_elecciones["data"][0], "extra_field": "ok"}
        ResumenEleccionItem(**payload)


# ===========================================================================
# MesaTotales
# ===========================================================================

class TestMesaTotales:
    def test_parse_real_fixture(self, raw_mesa_totales: dict) -> None:
        model = MesaTotales(**raw_mesa_totales["data"])
        assert model.mesasInstaladas == 92532
        assert model.mesasNoInstaladas == 48
        assert model.mesasPendientes == 186

    def test_frozen(self, raw_mesa_totales: dict) -> None:
        model = MesaTotales(**raw_mesa_totales["data"])
        with pytest.raises((TypeError, AttributeError)):
            model.mesasInstaladas = 0  # type: ignore[misc]

    def test_wrong_type_raises(self) -> None:
        with pytest.raises(ValidationError):
            MesaTotales(mesasInstaladas="x", mesasNoInstaladas="y", mesasPendientes="z")  # type: ignore[arg-type]


# ===========================================================================
# ProcesoActivo
# ===========================================================================

class TestProcesoActivo:
    def test_parse_real_fixture(self, raw_proceso_activo: dict) -> None:
        model = ProcesoActivo(**raw_proceso_activo["data"])
        assert model.acronimo == "EG2026"
        assert model.activoFechaProceso is True
        assert model.idEleccionPrincipal == 10
        # fechaProceso puede ser int (ms epoch) o str — ambos válidos
        assert model.fechaProceso is not None

    def test_frozen(self, raw_proceso_activo: dict) -> None:
        model = ProcesoActivo(**raw_proceso_activo["data"])
        with pytest.raises((TypeError, AttributeError)):
            model.acronimo = "XX"  # type: ignore[misc]

    def test_extra_ignored(self, raw_proceso_activo: dict) -> None:
        payload = {**raw_proceso_activo["data"], "campo_extra": 999}
        ProcesoActivo(**payload)


# ===========================================================================
# EleccionItem
# ===========================================================================

class TestEleccionItem:
    def test_parse_real_fixture(self, raw_elecciones: dict) -> None:
        item = raw_elecciones["data"][0]
        model = EleccionItem(**item)
        assert isinstance(model.id, int)
        assert isinstance(model.nombre, str)

    def test_parse_all_items(self, raw_elecciones: dict) -> None:
        items = [EleccionItem(**d) for d in raw_elecciones["data"]]
        assert len(items) == 9

    def test_frozen(self, raw_elecciones: dict) -> None:
        model = EleccionItem(**raw_elecciones["data"][0])
        with pytest.raises((TypeError, AttributeError)):
            model.nombre = "hack"  # type: ignore[misc]

    def test_extra_ignored(self, raw_elecciones: dict) -> None:
        payload = {**raw_elecciones["data"][0], "xxx": 1}
        EleccionItem(**payload)


# ===========================================================================
# UbigeoItem
# ===========================================================================

class TestUbigeoItem:
    def test_parse_real_fixture(self, raw_ubigeos_departamentos: dict) -> None:
        item = raw_ubigeos_departamentos["data"][0]
        model = UbigeoItem(**item)
        assert model.ubigeo == "010000"
        assert model.nombre == "AMAZONAS"

    def test_parse_all_25_items(self, raw_ubigeos_departamentos: dict) -> None:
        items = [UbigeoItem(**d) for d in raw_ubigeos_departamentos["data"]]
        assert len(items) == 25

    def test_frozen(self, raw_ubigeos_departamentos: dict) -> None:
        model = UbigeoItem(**raw_ubigeos_departamentos["data"][0])
        with pytest.raises((TypeError, AttributeError)):
            model.ubigeo = "999999"  # type: ignore[misc]

    def test_wrong_type_raises(self) -> None:
        with pytest.raises(ValidationError):
            UbigeoItem(ubigeo=123, nombre=456)  # type: ignore[arg-type]


# ===========================================================================
# OnpeResponse (envelope genérico)
# ===========================================================================

class TestOnpeResponse:
    def test_parse_success_true(self, raw_totales: dict) -> None:
        model = OnpeResponse(**raw_totales)
        assert model.success is True

    def test_parse_success_false_allowed(self) -> None:
        model = OnpeResponse(success=False, message="error", data=None)
        assert model.success is False

    def test_data_present(self, raw_totales: dict) -> None:
        model = OnpeResponse(**raw_totales)
        assert model.data is not None

    def test_extra_ignored(self, raw_totales: dict) -> None:
        payload = {**raw_totales, "campo_raro": "ok"}
        OnpeResponse(**payload)


# ===========================================================================
# Finding + Severity
# ===========================================================================

class TestFinding:
    def _make_finding(self, **overrides) -> dict:
        base = {
            "id": "F001",
            "severity": "CRÍTICO",
            "test": "reconcile_national_vs_regional",
            "h0": "national == sum(regions)",
            "statistic": 4.703,
            "threshold": 0.1,
            "interpretation": "Diff > umbral",
            "limitations": "Solo datos regionales disponibles",
            "captura_sha256": "abc123def456",
        }
        return {**base, **overrides}

    def test_parse_valid_finding(self) -> None:
        model = Finding(**self._make_finding())
        assert model.id == "F001"
        assert model.severity == "CRÍTICO"
        assert model.captura_sha256 == "abc123def456"

    def test_p_value_optional_defaults_none(self) -> None:
        model = Finding(**self._make_finding())
        assert model.p_value is None

    def test_p_value_can_be_set(self) -> None:
        model = Finding(**self._make_finding(p_value=0.032))
        assert model.p_value == pytest.approx(0.032)

    def test_severity_literal_critico(self) -> None:
        model = Finding(**self._make_finding(severity="CRÍTICO"))
        assert model.severity == "CRÍTICO"

    def test_severity_literal_media(self) -> None:
        model = Finding(**self._make_finding(severity="MEDIA"))
        assert model.severity == "MEDIA"

    def test_severity_literal_baja(self) -> None:
        model = Finding(**self._make_finding(severity="BAJA"))
        assert model.severity == "BAJA"

    def test_severity_literal_info(self) -> None:
        model = Finding(**self._make_finding(severity="INFO"))
        assert model.severity == "INFO"

    def test_severity_invalid_raises(self) -> None:
        with pytest.raises(ValidationError):
            Finding(**self._make_finding(severity="ALTO"))  # type: ignore[arg-type]

    def test_captura_sha256_required_str(self) -> None:
        payload = self._make_finding()
        del payload["captura_sha256"]
        with pytest.raises(ValidationError):
            Finding(**payload)

    def test_captura_sha256_must_be_str(self) -> None:
        with pytest.raises(ValidationError):
            Finding(**self._make_finding(captura_sha256=12345))  # type: ignore[arg-type]

    def test_frozen(self) -> None:
        model = Finding(**self._make_finding())
        with pytest.raises((TypeError, AttributeError)):
            model.severity = "INFO"  # type: ignore[misc]


class TestSeverity:
    def test_all_values_defined(self) -> None:
        assert set(Severity.__args__) == {"CRÍTICO", "MEDIA", "BAJA", "INFO"}  # type: ignore[attr-defined]
