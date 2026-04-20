"""
San Martín deep-dive.
- ¿Qué partidos dominan SM en mesas D?
- ¿Qué locales concentran impugnación?
- ¿Hay correlación partido-voto vs tasa impugnación intra-SM?
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import duckdb

sys.stdout.reconfigure(encoding="utf-8")

DB = "reports/hallazgos_20260420/eg2026.duckdb"
OUT = Path("reports/hallazgos_20260420")
con = duckdb.connect(DB)

print("=" * 72)
print("A. Ranking partidos en San Martín (mesas D)")
print("=" * 72)
rank = con.execute("""
    SELECT v.partido,
           SUM(v.votos) AS votos_sm,
           ROUND(SUM(v.votos)*100.0 /
                 (SELECT SUM(votos) FROM voto v2
                  JOIN mesa m2 ON m2.codigo_mesa=v2.codigo_mesa
                  WHERE m2.depto_real='San Martín'
                    AND v2.estado_acta='D'
                    AND TRY_CAST(v2.partido_codigo AS INT) BETWEEN 1 AND 38), 3) AS pct_sm
    FROM voto v
    JOIN mesa m ON m.codigo_mesa = v.codigo_mesa
    WHERE m.depto_real='San Martín'
      AND v.estado_acta='D'
      AND TRY_CAST(v.partido_codigo AS INT) BETWEEN 1 AND 38
    GROUP BY v.partido
    ORDER BY votos_sm DESC
    LIMIT 10;
""").pl()
print(rank)
print()

print("=" * 72)
print("B. Top-15 locales San Martín por pct_imp (>=3 mesas)")
print("=" * 72)
locs = con.execute("""
    SELECT local_votacion,
           COUNT(*) AS mesas,
           SUM(CASE WHEN estado_acta='I' THEN 1 ELSE 0 END) AS imp,
           ROUND(SUM(CASE WHEN estado_acta='I' THEN 1 ELSE 0 END)*100.0/COUNT(*), 2) AS pct_imp,
           ROUND(AVG(electores_habiles), 0) AS avg_electores
    FROM mesa
    WHERE depto_real='San Martín'
    GROUP BY local_votacion
    HAVING COUNT(*) >= 3
    ORDER BY pct_imp DESC, mesas DESC
    LIMIT 15;
""").pl()
print(locs)
print()

print("=" * 72)
print("C. Partidos SM — locales ALTA impugnación vs BAJA impugnación")
print("=" * 72)
# Usar quintiles dentro de SM
q = con.execute("""
    WITH ls AS (
        SELECT local_votacion,
               SUM(CASE WHEN estado_acta='I' THEN 1 ELSE 0 END)*1.0/COUNT(*) AS tasa_imp,
               COUNT(*) AS mesas
        FROM mesa
        WHERE depto_real='San Martín'
        GROUP BY local_votacion
        HAVING COUNT(*) >= 3
    )
    SELECT quantile_cont(tasa_imp, 0.80) AS q80,
           quantile_cont(tasa_imp, 0.20) AS q20
    FROM ls
""").fetchone()
q80, q20 = float(q[0]), float(q[1])
print(f"SM quintil 20 tasa_imp <= {q20:.3f}")
print(f"SM quintil 80 tasa_imp >= {q80:.3f}")
print()

rank_buckets = con.execute(f"""
    WITH ls AS (
        SELECT local_votacion,
               SUM(CASE WHEN estado_acta='I' THEN 1 ELSE 0 END)*1.0/COUNT(*) AS tasa_imp,
               COUNT(*) AS mesas
        FROM mesa
        WHERE depto_real='San Martín'
        GROUP BY local_votacion
        HAVING COUNT(*) >= 3
    ),
    buckets AS (
        SELECT local_votacion,
               CASE WHEN tasa_imp >= {q80} THEN 'ALTO'
                    WHEN tasa_imp <= {q20} THEN 'BAJO' ELSE 'MEDIO' END AS bucket
        FROM ls
    ),
    votos AS (
        SELECT b.bucket, v.partido, SUM(v.votos) AS votos
        FROM voto v
        JOIN mesa m ON m.codigo_mesa = v.codigo_mesa
        JOIN buckets b ON b.local_votacion = m.local_votacion
        WHERE v.estado_acta='D'
          AND TRY_CAST(v.partido_codigo AS INT) BETWEEN 1 AND 38
          AND m.depto_real='San Martín'
        GROUP BY b.bucket, v.partido
    ),
    tot AS (SELECT bucket, SUM(votos) AS total FROM votos GROUP BY bucket)
    SELECT v.partido,
           ROUND(SUM(CASE WHEN v.bucket='ALTO' THEN votos*100.0/t.total END), 3) AS pct_alto,
           ROUND(SUM(CASE WHEN v.bucket='BAJO' THEN votos*100.0/t.total END), 3) AS pct_bajo,
           ROUND(SUM(CASE WHEN v.bucket='ALTO' THEN votos*100.0/t.total END) -
                 SUM(CASE WHEN v.bucket='BAJO' THEN votos*100.0/t.total END), 3) AS delta_pp
    FROM votos v JOIN tot t USING(bucket)
    WHERE v.bucket IN ('ALTO','BAJO')
    GROUP BY v.partido
    ORDER BY delta_pp DESC NULLS LAST;
""").pl()
print("Partidos SM — top 5 suben y top 5 bajan en locales ALTA impugnación:")
print("TOP SUBEN:")
print(rank_buckets.head(5))
print()
print("TOP BAJAN:")
print(rank_buckets.tail(5))
print()

# Guardar
findings = {
    "depto": "San Martín",
    "ranking_partidos_sm": rank.to_dicts(),
    "locales_top_impugnacion": locs.to_dicts(),
    "bucket_quintiles": {"q20": q20, "q80": q80},
    "partidos_por_bucket": rank_buckets.to_dicts(),
}
p = OUT / "h1_san_martin.json"
p.write_text(json.dumps(findings, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
print(f"OK -> {p}")
con.close()
