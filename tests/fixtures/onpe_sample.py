"""
Fixtures pytest: cargan JSONs reales de captures/20260419T220357Z/raw/
y snap formato viejo de captures/20260418T203307Z/raw/
"""
import json
import pathlib
from typing import Any

import pytest

_RAW_NEW = pathlib.Path(__file__).parents[2] / "captures" / "20260419T220357Z" / "raw"
_RAW_OLD = pathlib.Path(__file__).parents[2] / "captures" / "20260418T203307Z" / "raw"


def _load(path: pathlib.Path) -> Any:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


# ---------------------------------------------------------------------------
# Datos crudos (dicts)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def raw_totales() -> dict:
    return _load(_RAW_NEW / "totales.json")


@pytest.fixture(scope="session")
def raw_presidencial() -> dict:
    return _load(_RAW_NEW / "presidencial.json")


@pytest.fixture(scope="session")
def raw_mapa_calor() -> dict:
    return _load(_RAW_NEW / "mapa_calor.json")


@pytest.fixture(scope="session")
def raw_resumen_elecciones() -> dict:
    return _load(_RAW_NEW / "resumen_elecciones.json")


@pytest.fixture(scope="session")
def raw_mesa_totales() -> dict:
    return _load(_RAW_NEW / "mesa_totales.json")


@pytest.fixture(scope="session")
def raw_proceso_activo() -> dict:
    return _load(_RAW_NEW / "proceso_activo.json")


@pytest.fixture(scope="session")
def raw_elecciones() -> dict:
    return _load(_RAW_NEW / "elecciones.json")


@pytest.fixture(scope="session")
def raw_ubigeos_departamentos() -> dict:
    return _load(_RAW_NEW / "ubigeos_departamentos.json")


# ---------------------------------------------------------------------------
# Snap viejo (formato national + regions) para reconcile
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def raw_snap_old() -> dict:
    """snap1.json con keys: national, regions, timestamp, derived, appVersion"""
    return _load(_RAW_OLD / "snap1.json")


@pytest.fixture(scope="session")
def snap_national(raw_snap_old: dict) -> dict:
    return raw_snap_old["national"]


@pytest.fixture(scope="session")
def snap_regions(raw_snap_old: dict) -> list[dict]:
    return raw_snap_old["regions"]
