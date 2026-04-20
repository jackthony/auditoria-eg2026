"""
Samplear 5 locales por cada prefix (01-25).
Imprimir nombres crudos para validación manual.
"""
from __future__ import annotations
import sys
import duckdb

sys.stdout.reconfigure(encoding="utf-8")

DB = "reports/hallazgos_20260420/eg2026.duckdb"
con = duckdb.connect(DB, read_only=True)

# Para cada prefix real (01-25), 5 locales distintos con más mesas
prefixes = con.execute("""
    SELECT DISTINCT SUBSTR(ubigeo,1,2) AS p
    FROM voto
    WHERE SUBSTR(ubigeo,1,2) NOT LIKE '9%'
    ORDER BY p;
""").pl()

for p in prefixes["p"].to_list():
    print(f"\n=== PREFIX {p} ===")
    r = con.execute(f"""
        SELECT local_votacion, COUNT(DISTINCT codigo_mesa) AS mesas
        FROM voto
        WHERE SUBSTR(ubigeo,1,2)='{p}'
          AND local_votacion IS NOT NULL
        GROUP BY local_votacion
        ORDER BY mesas DESC
        LIMIT 5;
    """).pl()
    for name, n in zip(r["local_votacion"].to_list(), r["mesas"].to_list()):
        print(f"  [{n:>4}]  {name}")

# También para 91-95
print("\n=== PREFIX 91-95 (Extranjero) ===")
for p in ("91","92","93","94","95"):
    print(f"\n-- {p} --")
    r = con.execute(f"""
        SELECT local_votacion, COUNT(DISTINCT codigo_mesa) AS mesas
        FROM voto
        WHERE SUBSTR(ubigeo,1,2)='{p}'
          AND local_votacion IS NOT NULL
        GROUP BY local_votacion
        ORDER BY mesas DESC
        LIMIT 5;
    """).pl()
    for name, n in zip(r["local_votacion"].to_list(), r["mesas"].to_list()):
        print(f"  [{n:>4}]  {name}")
con.close()
