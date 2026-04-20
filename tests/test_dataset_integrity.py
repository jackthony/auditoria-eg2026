"""
tests/test_dataset_integrity.py — Tests sobre el parquet HF (Polars + DuckDB).

Valida sobre 3.79M filas / 92,766 mesas en milisegundos.

Datos: reports/hf_dataset/onpe_eg2026_mesas_<TS>.parquet (último por mtime).
Marcado @pytest.mark.integration porque toca dataset real.
"""
from __future__ import annotations

from pathlib import Path

import duckdb
import polars as pl
import pytest

ROOT = Path(__file__).resolve().parents[1]
HF_DIR = ROOT / "reports" / "hf_dataset"

EXPECTED_NORMALES = 88063  # 88064 - gap 087704
EXPECTED_ESPECIALES = 4703
EXPECTED_TOTAL = EXPECTED_NORMALES + EXPECTED_ESPECIALES  # 92,766
GAP_MESA = "087704"


def _latest_parquet() -> Path:
    files = list(HF_DIR.glob("onpe_eg2026_mesas_*.parquet"))
    if not files:
        pytest.skip("Sin parquet HF disponible")
    return max(files, key=lambda p: p.stat().st_mtime)


@pytest.fixture(scope="module")
def parquet_path() -> Path:
    return _latest_parquet()


@pytest.fixture(scope="module")
def lf(parquet_path: Path) -> pl.LazyFrame:
    return pl.scan_parquet(parquet_path)


@pytest.fixture(scope="module")
def mesas(lf: pl.LazyFrame) -> pl.DataFrame:
    return (
        lf.select("codigo_mesa", "ubigeo", "departamento")
        .unique(subset=["codigo_mesa"])
        .with_columns(
            pl.col("codigo_mesa").cast(pl.Int64).alias("mesa_int"),
        )
        .with_columns(
            (pl.col("mesa_int") >= 900000).alias("mesa_especial"),
        )
        .collect()
    )


@pytest.mark.integration
def test_universe_total_count(mesas: pl.DataFrame) -> None:
    assert mesas.height == EXPECTED_TOTAL, (
        f"Esperado {EXPECTED_TOTAL} mesas, encontrado {mesas.height}"
    )


@pytest.mark.integration
def test_normales_count(mesas: pl.DataFrame) -> None:
    n = mesas.filter(~pl.col("mesa_especial")).height
    assert n == EXPECTED_NORMALES, f"Normales: esperado {EXPECTED_NORMALES}, got {n}"


@pytest.mark.integration
def test_especiales_count(mesas: pl.DataFrame) -> None:
    e = mesas.filter(pl.col("mesa_especial")).height
    assert e == EXPECTED_ESPECIALES, f"Especiales: esperado {EXPECTED_ESPECIALES}, got {e}"


@pytest.mark.integration
def test_no_duplicate_mesa_partido(parquet_path: Path) -> None:
    # DuckDB groupby SQL — instantáneo sobre parquet directo
    res = duckdb.sql(
        f"""
        SELECT COUNT(*) AS dupes FROM (
            SELECT codigo_mesa, partido_codigo, COUNT(*) AS c
            FROM read_parquet('{parquet_path.as_posix()}')
            GROUP BY 1, 2
            HAVING c > 1
        )
        """
    ).fetchone()
    assert res[0] == 0, f"{res[0]} pares (mesa, partido) duplicados"


@pytest.mark.integration
def test_gap_087704_absent(mesas: pl.DataFrame) -> None:
    found = mesas.filter(pl.col("codigo_mesa") == GAP_MESA).height
    assert found == 0, f"Gap {GAP_MESA} debería no existir, halladas {found}"


@pytest.mark.integration
def test_normales_range(mesas: pl.DataFrame) -> None:
    norm = mesas.filter(~pl.col("mesa_especial"))["mesa_int"]
    assert norm.min() == 1 and norm.max() == 88064, (
        f"Rango normales fuera de [1, 88064]: min={norm.min()} max={norm.max()}"
    )


@pytest.mark.integration
def test_especiales_range(mesas: pl.DataFrame) -> None:
    esp = mesas.filter(pl.col("mesa_especial"))["mesa_int"]
    assert esp.min() == 900001 and esp.max() == 904703, (
        f"Rango especiales fuera de [900001, 904703]: min={esp.min()} max={esp.max()}"
    )


@pytest.mark.integration
def test_special_party_codes_present(lf: pl.LazyFrame) -> None:
    codes = set(
        lf.select(pl.col("partido_codigo").drop_nulls().cast(pl.Utf8))
        .unique()
        .collect()["partido_codigo"]
        .to_list()
    )
    for sp in ("80", "81", "82"):
        assert sp in codes, f"Falta código especial {sp} (BLANCOS/NULOS/IMPUGNADOS)"


@pytest.mark.integration
def test_departamentos_catalogo(mesas: pl.DataFrame) -> None:
    deptos = set(mesas["departamento"].drop_nulls().unique().to_list())
    assert len(deptos) >= 24, f"Solo {len(deptos)} deptos: {deptos}"


@pytest.mark.integration
def test_ubigeo_format(mesas: pl.DataFrame) -> None:
    bad = mesas.filter(pl.col("ubigeo").str.len_chars() != 6).height
    assert bad == 0, f"{bad} ubigeos con longitud != 6"


@pytest.mark.integration
def test_votos_no_negativos(parquet_path: Path) -> None:
    res = duckdb.sql(
        f"""
        SELECT COUNT(*) FROM read_parquet('{parquet_path.as_posix()}')
        WHERE votos < 0
        """
    ).fetchone()
    assert res[0] == 0, f"{res[0]} filas con votos negativos"


@pytest.mark.integration
def test_partidos_count_minimo(lf: pl.LazyFrame) -> None:
    n = lf.select(pl.col("partido_codigo").n_unique()).collect().item()
    assert n >= 30, f"Solo {n} partidos únicos (esperado >=30)"
