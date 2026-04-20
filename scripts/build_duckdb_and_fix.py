"""
scripts/build_duckdb_and_fix.py — Construye eg2026.duckdb desde parquet HF.

Lee `reports/hf_dataset/onpe_eg2026_mesas_<TS>.parquet` (auto-detecta el más
reciente o usa --ts) y crea/refresca:
  - voto        (3.79M filas, 1 fila = mesa×partido)
  - mesa        (92,766 filas, 1 fila = mesa con depto_real)
  - regiones    (26 filas, ONPE agregado = fuente de verdad)
  - depto_map   (ubigeo_prefix → depto_real, mapping ONPE alfabético+Callao=24)

Mapping prefix→depto validado empíricamente 2026-04-20 (ratios 0.81-1.00 vs
totales oficiales en regiones.csv).

Uso:
    py scripts/build_duckdb_and_fix.py                  # auto-detecta último parquet
    py scripts/build_duckdb_and_fix.py --ts 20260420T074202Z
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import duckdb
import polars as pl

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
HF_DIR = ROOT / "reports" / "hf_dataset"
CSV_REG = ROOT / "data" / "processed" / "regiones.csv"
DB_PATH = ROOT / "reports" / "hallazgos_20260420" / "eg2026.duckdb"

# ONPE prefix → depto_real. Alfabético con Callao=24.
PREFIX_TO_DEPTO: dict[str, str] = {
    "01": "Amazonas", "02": "Áncash", "03": "Apurímac", "04": "Arequipa",
    "05": "Ayacucho", "06": "Cajamarca", "07": "Cusco", "08": "Huancavelica",
    "09": "Huánuco", "10": "Ica", "11": "Junín", "12": "La Libertad",
    "13": "Lambayeque", "14": "Lima", "15": "Loreto", "16": "Madre de Dios",
    "17": "Moquegua", "18": "Pasco", "19": "Piura", "20": "Puno",
    "21": "San Martín", "22": "Tacna", "23": "Tumbes", "24": "Callao",
    "25": "Ucayali",
    "91": "Extranjero", "92": "Extranjero", "93": "Extranjero",
    "94": "Extranjero", "95": "Extranjero",
}


def latest_parquet() -> Path:
    files = list(HF_DIR.glob("onpe_eg2026_mesas_*.parquet"))
    if not files:
        raise SystemExit(f"Sin parquet en {HF_DIR}")
    return max(files, key=lambda p: p.stat().st_mtime)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ts", default=None,
                    help="Timestamp UTC compact (e.g. 20260420T074202Z). Si omites, usa el último.")
    args = ap.parse_args()

    if args.ts:
        pq = HF_DIR / f"onpe_eg2026_mesas_{args.ts}.parquet"
        if not pq.exists():
            raise SystemExit(f"No existe {pq}")
    else:
        pq = latest_parquet()

    print(f"[duckdb] source: {pq.name}")
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect(str(DB_PATH))

    # voto
    con.execute("DROP TABLE IF EXISTS voto")
    con.execute(f"""
        CREATE TABLE voto AS
        SELECT * FROM read_parquet('{pq.as_posix()}');
    """)
    n_voto = con.execute("SELECT COUNT(*) FROM voto").fetchone()[0]
    print(f"[duckdb] voto: {n_voto:,} filas")

    # regiones
    con.execute("DROP TABLE IF EXISTS regiones")
    con.execute(f"""
        CREATE TABLE regiones AS
        SELECT name AS depto_real, totalActas
        FROM read_csv_auto('{CSV_REG.as_posix()}', header=true);
    """)

    # depto_map
    con.execute("DROP TABLE IF EXISTS depto_map")
    rows_map = [{"prefix": p, "depto_real": d} for p, d in PREFIX_TO_DEPTO.items()]
    con.register("mp_df", pl.DataFrame(rows_map))
    con.execute("CREATE TABLE depto_map AS SELECT * FROM mp_df")
    con.unregister("mp_df")

    # Validación captura vs ONPE oficial
    val = con.execute("""
        WITH ds AS (
            SELECT dm.depto_real, COUNT(DISTINCT v.codigo_mesa) AS mesas_cap
            FROM voto v
            JOIN depto_map dm ON dm.prefix = SUBSTR(v.ubigeo,1,2)
            GROUP BY dm.depto_real
        )
        SELECT ds.depto_real, ds.mesas_cap, r.totalActas AS oficial,
               ROUND(ds.mesas_cap*100.0/r.totalActas, 1) AS pct_captura
        FROM ds LEFT JOIN regiones r USING(depto_real)
        ORDER BY ds.mesas_cap DESC;
    """).pl()
    print("\n[duckdb] VALIDACION captura vs ONPE oficial:")
    print(val)

    # mesa con depto_real + flag mesa_especial
    con.execute("DROP TABLE IF EXISTS mesa")
    con.execute("""
        CREATE TABLE mesa AS
        SELECT DISTINCT
            v.codigo_mesa, v.ubigeo,
            SUBSTR(v.ubigeo,1,2) AS prefix,
            dm.depto_real,
            v.estado_acta, v.electores_habiles,
            v.votos_emitidos, v.votos_validos,
            v.pct_participacion, v.local_votacion,
            CAST(v.codigo_mesa AS BIGINT) >= 900000 AS mesa_especial
        FROM voto v
        LEFT JOIN depto_map dm ON dm.prefix = SUBSTR(v.ubigeo,1,2);
    """)
    n_mesa = con.execute("SELECT COUNT(*) FROM mesa").fetchone()[0]
    n_esp = con.execute("SELECT COUNT(*) FROM mesa WHERE mesa_especial").fetchone()[0]
    n_norm = con.execute("SELECT COUNT(*) FROM mesa WHERE NOT mesa_especial").fetchone()[0]
    print(f"\n[duckdb] mesa: {n_mesa:,} filas (normales={n_norm:,}  especiales 900k+={n_esp:,})")

    # Mesas sin depto_real (debug)
    n_sin = con.execute("SELECT COUNT(*) FROM mesa WHERE depto_real IS NULL").fetchone()[0]
    if n_sin > 0:
        print(f"[duckdb] WARN {n_sin} mesas sin depto_real (prefix no mapeado)")
        unk = con.execute("""
            SELECT prefix, COUNT(*) FROM mesa WHERE depto_real IS NULL
            GROUP BY 1 ORDER BY 2 DESC LIMIT 10
        """).fetchall()
        for p, c in unk:
            print(f"   prefix={p}  mesas={c}")

    con.execute("CREATE INDEX IF NOT EXISTS idx_voto_mesa ON voto(codigo_mesa)")
    con.execute("CREATE INDEX IF NOT EXISTS idx_mesa_depto ON mesa(depto_real)")
    con.execute("CREATE INDEX IF NOT EXISTS idx_mesa_estado ON mesa(estado_acta)")
    con.execute("CREATE INDEX IF NOT EXISTS idx_mesa_especial ON mesa(mesa_especial)")

    con.close()
    print(f"\n[duckdb] OK {DB_PATH}  ({DB_PATH.stat().st_size/1e6:.1f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
