"""
Análisis v2 — sobre eg2026.duckdb con depto_real fijado.

3 hallazgos:
  1. Sesgo geográfico en impugnadas (depto real)
  2. Partidos vs tasa impugnación de su local de votación (solo mesas D)
  3. Anomalías nulos/blancos (outliers por mesa)
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import duckdb
import polars as pl

sys.stdout.reconfigure(encoding="utf-8")

DB = "reports/hallazgos_20260420/eg2026.duckdb"
OUT = Path("reports/hallazgos_20260420")
con = duckdb.connect(DB)

# Marcar caveat: 3 prefijos con ratio>1.05 = Tumbes/Moquegua/Madre de Dios
# + 4 prefijos NO_IDENTIFICADO (prefix 16, 91, 93, 95)
SOSPECHOSOS = ("Tumbes", "Moquegua", "Madre de Dios")

total_mesas = con.execute("SELECT COUNT(*) FROM mesa").fetchone()[0]
global_imp_pct = con.execute(
    "SELECT AVG(CASE WHEN estado_acta='I' THEN 1.0 ELSE 0.0 END)*100 FROM mesa"
).fetchone()[0]

print(f"Mesas: {total_mesas:,}")
print(f"Tasa global impugnadas: {global_imp_pct:.3f}%")
print()

# ============================================================
# 1. SESGO GEOGRÁFICO (depto real)
# ============================================================
print("=" * 72)
print("1. SESGO GEOGRÁFICO por depto_real (ONPE)")
print("=" * 72)
geo = con.execute("""
    WITH t AS (
        SELECT depto_real,
               COUNT(*) AS total,
               SUM(CASE WHEN estado_acta='I' THEN 1 ELSE 0 END) AS imp
        FROM mesa
        WHERE depto_real IS NOT NULL AND depto_real <> 'NO_IDENTIFICADO'
        GROUP BY depto_real
    ),
    g AS (SELECT SUM(imp)*1.0/SUM(total) AS p FROM t)
    SELECT t.depto_real, t.total, t.imp,
           ROUND(t.imp*100.0/t.total, 2) AS pct_imp,
           ROUND(((t.imp*1.0/t.total) - g.p) / sqrt(g.p*(1-g.p)/t.total), 2) AS z_score
    FROM t, g
    ORDER BY pct_imp DESC;
""").pl()
print(geo)
print()

# ============================================================
# 2. PARTIDOS vs TASA IMPUGNACIÓN del local (mesas D)
# ============================================================
print("=" * 72)
print("2. PARTIDO vs TASA IMPUGNACIÓN del local")
print("=" * 72)

# Preparar tabla local_stats
con_rw = con
con_rw.execute("""
    CREATE OR REPLACE TEMP VIEW local_stats AS
    SELECT local_votacion, depto_real,
           COUNT(*) AS mesas_total,
           SUM(CASE WHEN estado_acta='I' THEN 1 ELSE 0 END) AS mesas_imp,
           SUM(CASE WHEN estado_acta='I' THEN 1 ELSE 0 END)*1.0/COUNT(*) AS tasa_imp
    FROM mesa
    WHERE depto_real IS NOT NULL AND depto_real <> 'NO_IDENTIFICADO'
    GROUP BY local_votacion, depto_real
    HAVING COUNT(*) >= 3;
""")

q80 = con_rw.execute("SELECT quantile_cont(tasa_imp, 0.80) FROM local_stats").fetchone()[0]
q20 = con_rw.execute("SELECT quantile_cont(tasa_imp, 0.20) FROM local_stats").fetchone()[0]
print(f"Quintil 20 tasa_imp ≤ {q20:.3f}")
print(f"Quintil 80 tasa_imp ≥ {q80:.3f}")
print()

# Share por partido en ALTO vs BAJO
res = con_rw.execute(f"""
    WITH partido_d AS (
        SELECT v.local_votacion, v.partido, SUM(v.votos) AS votos
        FROM voto v
        WHERE TRY_CAST(v.partido_codigo AS INTEGER) BETWEEN 1 AND 38
          AND v.estado_acta = 'D'
        GROUP BY v.local_votacion, v.partido
    ),
    pl AS (
        SELECT ls.local_votacion, ls.tasa_imp,
               CASE WHEN ls.tasa_imp >= {q80} THEN 'ALTO'
                    WHEN ls.tasa_imp <= {q20} THEN 'BAJO' ELSE 'MEDIO' END AS bucket,
               p.partido, p.votos
        FROM local_stats ls
        JOIN partido_d p USING(local_votacion)
    ),
    agg AS (
        SELECT bucket, partido, SUM(votos) AS votos
        FROM pl GROUP BY bucket, partido
    ),
    tot AS (SELECT bucket, SUM(votos) AS total FROM agg GROUP BY bucket)
    SELECT a.bucket, a.partido,
           ROUND(a.votos*100.0/t.total, 3) AS pct
    FROM agg a JOIN tot t USING(bucket)
    WHERE a.bucket IN ('ALTO','BAJO')
    ORDER BY a.bucket, pct DESC;
""").pl()

# Pivot
pivot = (res.pivot(values="pct", index="partido", on="bucket")
         .with_columns((pl.col("ALTO") - pl.col("BAJO")).round(3).alias("delta_pp"))
         .sort("delta_pp", descending=True))
print("Top-8 partidos que SUBEN share en locales ALTA impugnación:")
print(pivot.head(8))
print()
print("Top-8 partidos que BAJAN share en locales ALTA impugnación:")
print(pivot.tail(8))
print()

# ============================================================
# 3. NULOS/BLANCOS (solo mesas D)
# ============================================================
print("=" * 72)
print("3. NULOS / BLANCOS (mesas D)")
print("=" * 72)

nb_global = con.execute("""
    WITH e AS (
        SELECT SUM(CASE WHEN TRY_CAST(partido_codigo AS INT)=80 THEN votos ELSE 0 END) AS bl,
               SUM(CASE WHEN TRY_CAST(partido_codigo AS INT)=81 THEN votos ELSE 0 END) AS nu,
               SUM(votos) AS tot
        FROM voto WHERE estado_acta='D'
    )
    SELECT ROUND(bl*100.0/tot,2) AS pct_bl,
           ROUND(nu*100.0/tot,2) AS pct_nu
    FROM e;
""").pl()
print("Global mesas D:")
print(nb_global)
print()

nb_dept = con.execute("""
    WITH mesa_esp AS (
        SELECT m.depto_real, v.codigo_mesa, v.votos_emitidos,
               SUM(CASE WHEN TRY_CAST(v.partido_codigo AS INT)=80 THEN v.votos ELSE 0 END) AS bl,
               SUM(CASE WHEN TRY_CAST(v.partido_codigo AS INT)=81 THEN v.votos ELSE 0 END) AS nu
        FROM voto v
        JOIN mesa m ON m.codigo_mesa = v.codigo_mesa
        WHERE v.estado_acta='D' AND m.depto_real IS NOT NULL AND m.depto_real <> 'NO_IDENTIFICADO'
        GROUP BY m.depto_real, v.codigo_mesa, v.votos_emitidos
    )
    SELECT depto_real,
           COUNT(*) AS mesas,
           ROUND(SUM(bl)*100.0/NULLIF(SUM(votos_emitidos),0),2) AS pct_blancos,
           ROUND(SUM(nu)*100.0/NULLIF(SUM(votos_emitidos),0),2) AS pct_nulos
    FROM mesa_esp
    GROUP BY depto_real
    ORDER BY pct_nulos DESC;
""").pl()
print("Nulos/Blancos por depto_real:")
print(nb_dept)
print()

# Outliers: mesa con pct_nulos > 15 o pct_blancos > 25
outliers = con.execute("""
    WITH mesa_esp AS (
        SELECT v.codigo_mesa, m.depto_real, v.votos_emitidos,
               SUM(CASE WHEN TRY_CAST(v.partido_codigo AS INT)=80 THEN v.votos ELSE 0 END) AS bl,
               SUM(CASE WHEN TRY_CAST(v.partido_codigo AS INT)=81 THEN v.votos ELSE 0 END) AS nu
        FROM voto v
        JOIN mesa m ON m.codigo_mesa = v.codigo_mesa
        WHERE v.estado_acta='D' AND v.votos_emitidos > 0
        GROUP BY v.codigo_mesa, m.depto_real, v.votos_emitidos
    )
    SELECT codigo_mesa, depto_real, votos_emitidos, bl, nu,
           ROUND(bl*100.0/votos_emitidos,2) AS pct_bl,
           ROUND(nu*100.0/votos_emitidos,2) AS pct_nu
    FROM mesa_esp
    WHERE bl*100.0/votos_emitidos > 25 OR nu*100.0/votos_emitidos > 15
    ORDER BY (bl+nu) DESC
    LIMIT 20;
""").pl()
print("Top-20 mesas outliers (pct_nu>15 OR pct_bl>25):")
print(outliers)
print()

# Count total outliers
n_out = con.execute("""
    WITH mesa_esp AS (
        SELECT v.codigo_mesa, v.votos_emitidos,
               SUM(CASE WHEN TRY_CAST(v.partido_codigo AS INT)=80 THEN v.votos ELSE 0 END) AS bl,
               SUM(CASE WHEN TRY_CAST(v.partido_codigo AS INT)=81 THEN v.votos ELSE 0 END) AS nu
        FROM voto v
        WHERE v.estado_acta='D' AND v.votos_emitidos > 0
        GROUP BY v.codigo_mesa, v.votos_emitidos
    )
    SELECT COUNT(*) FROM mesa_esp
    WHERE bl*100.0/votos_emitidos > 25 OR nu*100.0/votos_emitidos > 15
""").fetchone()[0]
print(f"Total mesas outlier: {n_out:,} de {total_mesas:,} ({n_out*100/total_mesas:.2f}%)")
print()

# ============================================================
# Guardar findings
# ============================================================
findings = {
    "meta": {
        "fecha": "2026-04-20",
        "db": DB,
        "total_mesas": int(total_mesas),
        "tasa_global_impugnadas_pct": round(float(global_imp_pct), 3),
        "caveat_deptos_sospechosos": list(SOSPECHOSOS),
    },
    "geo_bias": geo.to_dicts(),
    "partido_vs_imp_top": pivot.head(8).to_dicts(),
    "partido_vs_imp_bot": pivot.tail(8).to_dicts(),
    "nb_global_D": nb_global.to_dicts(),
    "nb_por_depto": nb_dept.to_dicts(),
    "outliers_nb_top20": outliers.to_dicts(),
    "outliers_nb_total": int(n_out),
}
p = OUT / "findings_0420_v2.json"
p.write_text(json.dumps(findings, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
print(f"OK -> {p}")

con.close()
