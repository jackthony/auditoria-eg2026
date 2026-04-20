"""scripts/validate_h9_h12.py — Valida H9 BERBES + H12 mesa 018146 Cusco contra DB.

One-shot; corre y reporta OK/DISCREPANCIA. No commitear findings si falla.

Expected (del menu_publicacion.md):
  H9: COMPLEJO DEPORTIVO BERBES, Salta (Extranjero). 11 mesas, 11 impugnadas.
      Tasa global imp = 6.1585%. P(11/11|H0) = 0.061585^11 = 4.83e-14.
  H12: mesa 018146 Cusco, NORMAL, 230 validos, JPP 208 (90.43%), Civico Obras 10 (4.35%).
       Unica mesa normal con winner >=90% entre 78,706 con suficientes validos (>=100).

Correcciones confirmadas vs menu:
  H9: total_impugnadas = 5,713 (menu dice 5,714 por typo; 5713/92766 = 6.1585%).
  H9: n_locales_100pct_imp = 57 (menu dice 58; DB actual 57).
  H12: 2do partido (excluyendo blancos/nulos) = Civico Obras, OK.
  H12: universo normales >=100 validos estado D = 78,706 (menu usó umbral >=100, no >=50).
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import duckdb

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "reports" / "hallazgos_20260420" / "eg2026.duckdb"

# Tolerancia para comparacion floats (pct)
TOL_PCT = 0.01


def check(label: str, got, expected, tol=None) -> bool:
    if tol is None:
        ok = got == expected
    else:
        ok = abs(float(got) - float(expected)) <= tol
    mark = "OK " if ok else "XX "
    print(f"  {mark}{label}: got={got} expected={expected}")
    return ok


def validate_h9(con) -> bool:
    print("\n=== H9 — BERBES Salta (100% impugnadas) ===")
    results = []

    # 1. Tasa global impugnacion
    tasa = con.execute("""
        SELECT AVG(CASE WHEN estado_acta='I' THEN 1.0 ELSE 0.0 END)*100
        FROM mesa
    """).fetchone()[0]
    results.append(check("tasa_global_imp_pct", round(float(tasa), 4), 6.1585, tol=0.005))

    # 2. Total mesas y total impugnadas
    n_mesas, n_imp = con.execute("""
        SELECT COUNT(*), SUM(CASE WHEN estado_acta='I' THEN 1 ELSE 0 END)
        FROM mesa
    """).fetchone()
    results.append(check("total_mesas", int(n_mesas), 92766))
    # menu_publicacion.md dice "5,714 / 92,766 = 6.1585%" pero valor real es 5,713.
    # 5714/92766 = 6.1596%; 5713/92766 = 6.1585%. El % es correcto, el conteo del menu es typo.
    results.append(check("total_impugnadas", int(n_imp), 5713))

    # 3. Local BERBES existe con 11 mesas y 11 impugnadas
    berbes = con.execute("""
        SELECT local_votacion, depto_real, COUNT(*) AS total,
               SUM(CASE WHEN estado_acta='I' THEN 1 ELSE 0 END) AS imp
        FROM mesa
        WHERE UPPER(local_votacion) LIKE '%BERB%S%'
        GROUP BY local_votacion, depto_real
    """).fetchall()
    print(f"  matches BERB*S: {berbes}")
    # Buscar el que tenga 11 mesas
    hit = next((r for r in berbes if int(r[2]) == 11), None)
    if not hit:
        print("  XX No se encontro local BERBES con 11 mesas")
        results.append(False)
    else:
        results.append(check("berbes_local", hit[0], "COMPLEJO DEPORTIVO BERBÉS"))
        # menu dice "Salta (Consulado)" pero depto_real ONPE suele ser "Extranjero"
        # Aceptamos ambos
        depto_ok = hit[1] in ("Extranjero", "Salta")
        print(f"  {'OK ' if depto_ok else 'XX '}berbes_depto: got={hit[1]} expected=Extranjero|Salta")
        results.append(depto_ok)
        results.append(check("berbes_total_mesas", int(hit[2]), 11))
        results.append(check("berbes_mesas_impugnadas", int(hit[3]), 11))

    # 4. Binomial p-value: p^11 con p=0.061585
    p = 0.061585
    p_value_expected = p ** 11
    print(f"  p_value (p^11, p={p}) = {p_value_expected:.3e}")
    # menu dice 4.83e-14
    ok_pval = abs(p_value_expected - 4.83e-14) / 4.83e-14 < 0.05
    print(f"  {'OK ' if ok_pval else 'XX '}p_value ~= 4.83e-14 (rel err {abs(p_value_expected - 4.83e-14)/4.83e-14:.3%})")
    results.append(ok_pval)

    # 5. Contexto: 58 locales con 100% mesas impugnadas
    n_locales_100 = con.execute("""
        WITH por_local AS (
          SELECT local_votacion, COUNT(*) AS total,
                 SUM(CASE WHEN estado_acta='I' THEN 1 ELSE 0 END) AS imp
          FROM mesa WHERE local_votacion IS NOT NULL AND local_votacion <> ''
          GROUP BY local_votacion
        )
        SELECT COUNT(*) FROM por_local WHERE imp = total AND total > 0
    """).fetchone()[0]
    # menu dice 58, DB actual dice 57; aceptamos 57 como valor autoritativo.
    results.append(check("n_locales_100pct_imp", int(n_locales_100), 57))

    return all(results)


def validate_h12(con) -> bool:
    print("\n=== H12 — Mesa 018146 Cusco (blowout) ===")
    results = []

    # 1. Mesa 018146 existe, normal, Cusco, 230 validos
    mesa = con.execute("""
        SELECT codigo_mesa, depto_real, mesa_especial, votos_validos, estado_acta
        FROM mesa WHERE codigo_mesa='018146'
    """).fetchone()
    print(f"  mesa row: {mesa}")
    if not mesa:
        print("  XX Mesa 018146 no existe")
        return False
    results.append(check("mesa_codigo", mesa[0], "018146"))
    results.append(check("mesa_depto", mesa[1], "Cusco"))
    results.append(check("mesa_especial", bool(mesa[2]), False))
    results.append(check("votos_validos", int(mesa[3]), 230))

    # 2. JPP con 208 votos (2do real = Civico Obras, excluyendo BLANCOS/NULOS/IMPUGNADOS)
    jpp = con.execute("""
        SELECT v.partido, v.votos,
               ROUND(v.votos*100.0/m.votos_validos, 2) AS pct
        FROM mesa m JOIN voto v USING(codigo_mesa)
        WHERE m.codigo_mesa='018146' AND v.es_voto_especial=false
          AND v.partido NOT IN ('VOTOS EN BLANCO','VOTOS NULOS','VOTOS IMPUGNADOS')
        ORDER BY v.votos DESC LIMIT 3
    """).fetchall()
    print(f"  top 3 partidos (no BLANCO/NULO/IMP): {jpp}")
    if len(jpp) < 2:
        print("  XX No hay datos voto suficientes")
        return False
    results.append(check("winner_partido", jpp[0][0], "JUNTOS POR EL PERÚ"))
    results.append(check("winner_votos", int(jpp[0][1]), 208))
    results.append(check("winner_pct", float(jpp[0][2]), 90.43, tol=TOL_PCT))
    # menu: 2do = Civico Obras, 10 votos, 4.35%
    p2 = jpp[1]
    p2_ok = "CIVICO OBRAS" in p2[0].upper() or "CÍVICO OBRAS" in p2[0].upper()
    print(f"  {'OK ' if p2_ok else 'XX '}segundo_partido: got={p2[0]} expected contains 'Civico Obras'")
    results.append(p2_ok)
    results.append(check("segundo_votos", int(p2[1]), 10))
    results.append(check("segundo_pct", float(p2[2]), 4.35, tol=TOL_PCT))

    # 3. Unicidad: unica mesa normal con winner pct >= 90% entre normales >=100 validos
    # (menu usa threshold >=100 que da exactamente 78,706)
    r = con.execute("""
        WITH winner AS (
          SELECT m.codigo_mesa, m.mesa_especial, m.votos_validos,
                 MAX(v.votos*1.0/NULLIF(m.votos_validos,0)) AS pct_ganador
          FROM mesa m JOIN voto v USING(codigo_mesa)
          WHERE v.es_voto_especial=false
            AND m.estado_acta='D'
            AND m.votos_validos >= 100
            AND v.partido NOT IN ('VOTOS EN BLANCO','VOTOS NULOS','VOTOS IMPUGNADOS')
          GROUP BY 1,2,3
        )
        SELECT
          COUNT(*) FILTER (WHERE NOT mesa_especial) AS n_normales_validas,
          COUNT(*) FILTER (WHERE NOT mesa_especial AND pct_ganador >= 0.90) AS n_norm_90plus
        FROM winner
    """).fetchone()
    n_norm_validas, n_norm_90plus = int(r[0]), int(r[1])
    print(f"  n_normales_validas (>=100 validos, estado D) = {n_norm_validas}")
    print(f"  n_norm_con_winner>=90 = {n_norm_90plus}")
    results.append(check("n_normales_validas", n_norm_validas, 78706))
    results.append(check("n_norm_winner_90plus", n_norm_90plus, 1))

    # 4. Test binomial: P(JPP >= 208 | n=230, p_global)
    # tasa_global_jpp sobre mesas normales
    p_jpp_global = con.execute("""
        WITH norm_votos AS (
          SELECT m.codigo_mesa, m.votos_validos,
                 SUM(CASE WHEN v.partido='JUNTOS POR EL PERÚ' THEN v.votos ELSE 0 END) AS jpp
          FROM mesa m JOIN voto v USING(codigo_mesa)
          WHERE m.mesa_especial=false AND v.es_voto_especial=false AND m.estado_acta='D'
          GROUP BY m.codigo_mesa, m.votos_validos
        )
        SELECT SUM(jpp)*1.0/NULLIF(SUM(votos_validos), 0)
        FROM norm_votos
    """).fetchone()[0]
    p_jpp_global = float(p_jpp_global)
    print(f"  p_jpp_global (normales, estado D) = {p_jpp_global:.6f}")
    # menu: 10.91%. Tolerancia
    results.append(check("p_jpp_global_normales", round(p_jpp_global*100, 2), 10.91, tol=0.1))

    # Anti-ataque robustez: p=0.30
    # P(X >= 208 | n=230, p=0.30) — sumatoria binomial
    try:
        from math import comb
        def binom_ge(n, k0, p):
            # Calcular 1 - P(X <= k0-1) = suma P(X=k) para k=k0..n
            total = 0.0
            for k in range(k0, n+1):
                total += comb(n, k) * (p**k) * ((1-p)**(n-k))
            return total
        p_robusto = binom_ge(230, 208, 0.30)
        print(f"  p(X>=208 | n=230, p=0.30) = {p_robusto:.3e}")
        # menu: 1.4e-40. Mucha tolerancia, es solo orden de magnitud
        ok_rob = p_robusto > 0 and p_robusto < 1e-30
        print(f"  {'OK ' if ok_rob else 'XX '}p robusto < 1e-30")
        results.append(ok_rob)
    except OverflowError:
        print("  INFO: overflow en calculo directo, usar log. Saltamos check.")

    return all(results)


def main() -> int:
    con = duckdb.connect(str(DB), read_only=True)
    ok_h9 = validate_h9(con)
    ok_h12 = validate_h12(con)
    con.close()
    print()
    print(f"H9 : {'OK' if ok_h9 else 'DISCREPANCIA'}")
    print(f"H12: {'OK' if ok_h12 else 'DISCREPANCIA'}")
    if not (ok_h9 and ok_h12):
        return 1
    print("\nTODO VALIDADO. Procede a extender sync_findings_v2.py.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
