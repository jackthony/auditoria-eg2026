"""
H1 deep-dive — Extranjero + selva concentran impugnación.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import duckdb

sys.stdout.reconfigure(encoding="utf-8")

DB = "reports/hallazgos_20260420/eg2026.duckdb"
OUT = Path("reports/hallazgos_20260420")
con = duckdb.connect(DB)

# ============================================================
# A. EXTRANJERO desglosado por sub-prefix 91/92/93/94/95
# ============================================================
print("=" * 72)
print("A. Extranjero por sub-prefix (91/92/93/94/95)")
print("=" * 72)
ext = con.execute("""
    SELECT prefix,
           COUNT(*) AS mesas,
           SUM(CASE WHEN estado_acta='I' THEN 1 ELSE 0 END) AS imp,
           ROUND(SUM(CASE WHEN estado_acta='I' THEN 1 ELSE 0 END)*100.0/COUNT(*), 2) AS pct_imp
    FROM mesa
    WHERE depto_real='Extranjero'
    GROUP BY prefix
    ORDER BY pct_imp DESC;
""").pl()
print(ext)
print()

# Top locales del extranjero con mayor impugnación (>= 5 mesas)
print("Top-15 locales Extranjero por pct_imp (>=5 mesas):")
locs = con.execute("""
    SELECT local_votacion,
           COUNT(*) AS mesas,
           SUM(CASE WHEN estado_acta='I' THEN 1 ELSE 0 END) AS imp,
           ROUND(SUM(CASE WHEN estado_acta='I' THEN 1 ELSE 0 END)*100.0/COUNT(*), 2) AS pct_imp
    FROM mesa
    WHERE depto_real='Extranjero'
    GROUP BY local_votacion
    HAVING COUNT(*) >= 5
    ORDER BY pct_imp DESC, mesas DESC
    LIMIT 15;
""").pl()
print(locs)
print()

# Locales con 100% impugnación (catastrófico)
hundred = con.execute("""
    SELECT local_votacion, depto_real, COUNT(*) AS mesas
    FROM mesa
    WHERE estado_acta='I'
    GROUP BY local_votacion, depto_real
    HAVING COUNT(*) >= 3 AND
           COUNT(*) = (SELECT COUNT(*) FROM mesa m2 WHERE m2.local_votacion=mesa.local_votacion)
    ORDER BY mesas DESC
    LIMIT 20;
""").pl()
print("=" * 72)
print("B. Locales con 100% impugnación (>=3 mesas)")
print("=" * 72)
print(f"Total locales 100% impugnados: {len(hundred)}")
print(hundred.head(20))
print()

# Total universo de locales con >=3 mesas
n_locs = con.execute("""
    SELECT COUNT(*) FROM (
        SELECT local_votacion FROM mesa GROUP BY local_votacion HAVING COUNT(*)>=3
    )
""").fetchone()[0]
print(f"Universo locales >=3 mesas: {n_locs:,}")
print()

# ============================================================
# C. SELVA pattern: Loreto, Ucayali, Madre de Dios, San Martín, Amazonas
# ============================================================
print("=" * 72)
print("C. Selva: distribución impugnación por local (>=3 mesas)")
print("=" * 72)
selva = con.execute("""
    SELECT depto_real,
           COUNT(DISTINCT local_votacion) AS locales,
           COUNT(*) AS mesas,
           SUM(CASE WHEN estado_acta='I' THEN 1 ELSE 0 END) AS imp,
           ROUND(SUM(CASE WHEN estado_acta='I' THEN 1 ELSE 0 END)*100.0/COUNT(*), 2) AS pct_imp,
           ROUND(AVG(electores_habiles), 0) AS avg_electores
    FROM mesa
    WHERE depto_real IN ('Loreto','Ucayali','Madre de Dios','San Martín','Amazonas','Extranjero')
    GROUP BY depto_real
    ORDER BY pct_imp DESC;
""").pl()
print(selva)
print()

# ============================================================
# D. Comparar tamaño mesa (electores) en impugnadas vs D
# ============================================================
print("=" * 72)
print("D. Tamaño mesa: impugnadas vs digitalizadas")
print("=" * 72)
size = con.execute("""
    SELECT estado_acta,
           COUNT(*) AS n,
           ROUND(AVG(electores_habiles), 1) AS avg_electores,
           ROUND(AVG(votos_emitidos), 1) AS avg_emitidos,
           ROUND(AVG(pct_participacion), 2) AS avg_pct_part
    FROM mesa
    WHERE estado_acta IN ('D','I') AND electores_habiles > 0
    GROUP BY estado_acta;
""").pl()
print(size)
print()

# Mismo breakdown por depto selva
sz_selva = con.execute("""
    SELECT depto_real, estado_acta,
           COUNT(*) AS n,
           ROUND(AVG(electores_habiles), 0) AS avg_electores,
           ROUND(AVG(pct_participacion), 2) AS avg_pct_part
    FROM mesa
    WHERE depto_real IN ('Loreto','Ucayali','Extranjero','San Martín','Madre de Dios')
      AND estado_acta IN ('D','I') AND electores_habiles > 0
    GROUP BY depto_real, estado_acta
    ORDER BY depto_real, estado_acta;
""").pl()
print("Selva + Extranjero: tamaño mesa y participación por estado:")
print(sz_selva)

# Guardar
findings = {
    "extranjero_por_subprefix": ext.to_dicts(),
    "extranjero_top_locales": locs.to_dicts(),
    "locales_100pct_impugnados": hundred.to_dicts(),
    "universo_locales_3mas": int(n_locs),
    "selva_breakdown": selva.to_dicts(),
    "size_i_vs_d_global": size.to_dicts(),
    "size_i_vs_d_selva": sz_selva.to_dicts(),
}
p = OUT / "h1_deep_dive.json"
p.write_text(json.dumps(findings, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
print(f"\nOK -> {p}")
con.close()
