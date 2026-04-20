"""
Construye reports/hallazgos_20260420/eg2026.duckdb con:
  - voto        (3.6M filas, 1 fila = mesa×partido)
  - mesa        (88,063 filas, 1 fila = mesa, depto_real fijado)
  - regiones    (26 filas, ONPE agregado = fuente de verdad)
  - depto_map   (ubigeo_prefix → depto_real)

Fix del mapeo INEI-incorrecto del build_hf_dataset.py.
Mapping empírico pareando tamaños dataset vs regiones.csv
(ratios 0.81-1.00 validados).
"""
from __future__ import annotations
import sys
from pathlib import Path

import duckdb
import polars as pl

sys.stdout.reconfigure(encoding="utf-8")

CSV_MESAS = "reports/hf_dataset/onpe_eg2026_mesas_20260419T035056Z.csv"
CSV_REG = "data/processed/regiones.csv"
DB = "reports/hallazgos_20260420/eg2026.duckdb"
Path(DB).parent.mkdir(parents=True, exist_ok=True)

# ONPE prefix → depto_real. Alfabético con Callao movido a 24.
# Validado por muestreo de locales (universidades + IE numbering) 2026-04-20.
PREFIX_TO_DEPTO: dict[str, str] = {
    "01": "Amazonas",
    "02": "Áncash",
    "03": "Apurímac",
    "04": "Arequipa",
    "05": "Ayacucho",
    "06": "Cajamarca",
    "07": "Cusco",
    "08": "Huancavelica",
    "09": "Huánuco",
    "10": "Ica",
    "11": "Junín",
    "12": "La Libertad",
    "13": "Lambayeque",
    "14": "Lima",
    "15": "Loreto",
    "16": "Madre de Dios",
    "17": "Moquegua",
    "18": "Pasco",
    "19": "Piura",
    "20": "Puno",
    "21": "San Martín",
    "22": "Tacna",
    "23": "Tumbes",
    "24": "Callao",
    "25": "Ucayali",
    "91": "Extranjero",  # África + Diplomático
    "92": "Extranjero",  # América
    "93": "Extranjero",  # Asia
    "94": "Extranjero",  # Europa
    "95": "Extranjero",  # Oceanía
}

con = duckdb.connect(DB)

# voto
con.execute("DROP TABLE IF EXISTS voto")
con.execute(f"""
    CREATE TABLE voto AS
    SELECT * FROM read_csv_auto('{CSV_MESAS}', header=true, sample_size=-1);
""")
print(f"voto: {con.execute('SELECT COUNT(*) FROM voto').fetchone()[0]:,} filas")

# regiones
con.execute("DROP TABLE IF EXISTS regiones")
con.execute(f"""
    CREATE TABLE regiones AS
    SELECT name AS depto_real, totalActas
    FROM read_csv_auto('{CSV_REG}', header=true);
""")

# depto_map
con.execute("DROP TABLE IF EXISTS depto_map")
rows_map = [{"prefix": p, "depto_real": d} for p, d in PREFIX_TO_DEPTO.items()]
con.register("mp_df", pl.DataFrame(rows_map))
con.execute("CREATE TABLE depto_map AS SELECT * FROM mp_df")

# Validación: comparar dataset captured vs regiones.csv, por depto_real
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
print()
print("VALIDACION captura vs ONPE oficial:")
print(val)

# mesa con depto_real
con.execute("DROP TABLE IF EXISTS mesa")
con.execute("""
    CREATE TABLE mesa AS
    SELECT DISTINCT
        v.codigo_mesa, v.ubigeo,
        SUBSTR(v.ubigeo,1,2) AS prefix,
        dm.depto_real,
        v.estado_acta, v.electores_habiles,
        v.votos_emitidos, v.votos_validos,
        v.pct_participacion, v.local_votacion
    FROM voto v
    LEFT JOIN depto_map dm ON dm.prefix = SUBSTR(v.ubigeo,1,2);
""")
print(f"\nmesa: {con.execute('SELECT COUNT(*) FROM mesa').fetchone()[0]:,} filas")

con.execute("CREATE INDEX IF NOT EXISTS idx_voto_mesa ON voto(codigo_mesa)")
con.execute("CREATE INDEX IF NOT EXISTS idx_mesa_depto ON mesa(depto_real)")
con.execute("CREATE INDEX IF NOT EXISTS idx_mesa_estado ON mesa(estado_acta)")

con.close()
print(f"\nOK DB: {DB}  ({Path(DB).stat().st_size/1e6:.1f} MB)")
