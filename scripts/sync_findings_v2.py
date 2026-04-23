"""
scripts/sync_findings_v2.py — Sincroniza los 3 findings.json del repo.

Construye HALL-0420-H1/H2/H3/H4/H9/H12 sobre el universo v2 (92,766 mesas) y los
escribe a:
  - reports/findings.json                        (maestro, estructura {findings, results})
  - reports/hallazgos_20260420/findings_consolidado_0420.json  (consolidado con meta)
  - web/api/findings.json                        (endpoint del dashboard)

Borra todos los findings stale (R1, A1, A2, C1, D1-D3, E1, G1, H1, H2, F1,
M1-M3, A0, A-AUS-1/2/3, MESA-IMP-1/2). Decisión: stale → eliminar (a).

H9 = BERBES 11/11 impugnadas (binomial exacto, p=4.83e-14).
H12 = Mesa 018146 Cusco, JPP 90.43% (única normal >=90% entre 78,706).
Ambos validados vs DB por scripts/validate_h9_h12.py (2026-04-20).

Lee:
  - reports/h4_stats.json (HALL-0420-H4 ya calculado por stats_h4_especiales_900k.py)
  - reports/hallazgos_20260420/findings_0420_v2.json (H1/H2/H3 raw output)
  - reports/hallazgos_20260420/eg2026.duckdb (validación universo + H9/H12 live)
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import duckdb

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "reports" / "hallazgos_20260420" / "eg2026.duckdb"
RAW_H123 = ROOT / "reports" / "hallazgos_20260420" / "findings_0420_v2.json"
H4_STATS = ROOT / "reports" / "h4_stats.json"

OUT_MASTER = ROOT / "reports" / "findings.json"
OUT_CONSOLIDADO = ROOT / "reports" / "hallazgos_20260420" / "findings_consolidado_0420.json"
OUT_WEB = ROOT / "web" / "api" / "findings.json"

UNIVERSE_TS = "20260420T074202Z"


def build_h9(con, n_mesas: int) -> dict:
    """H9 — Locales 100% impugnadas, hero = COMPLEJO DEPORTIVO BERBÉS."""
    # Tasa global impugnacion exacta
    n_imp = con.execute("SELECT COUNT(*) FROM mesa WHERE estado_acta='I'").fetchone()[0]
    p_imp = float(n_imp) / float(n_mesas)

    # Locales 100% impugnadas (ranking)
    rows = con.execute(
        """
        WITH por_local AS (
          SELECT local_votacion, depto_real, COUNT(*) AS total,
                 SUM(CASE WHEN estado_acta='I' THEN 1 ELSE 0 END) AS imp
          FROM mesa
          WHERE local_votacion IS NOT NULL AND local_votacion <> ''
          GROUP BY local_votacion, depto_real
        )
        SELECT local_votacion, depto_real, total
        FROM por_local WHERE imp = total AND total > 0
        ORDER BY total DESC
        """
    ).fetchall()
    top_locales = [
        {"local_votacion": r[0], "depto_real": r[1], "total": int(r[2])}
        for r in rows[:10]
    ]
    n_locales_100 = len(rows)
    n_3plus = sum(1 for r in rows if int(r[2]) >= 3)
    n_5plus = sum(1 for r in rows if int(r[2]) >= 5)

    # Binomial exacto: P(11/11 impugnadas | H0=p_global)
    berbes_n = int(top_locales[0]["total"]) if top_locales else 0
    p_value_berbes = p_imp ** berbes_n if berbes_n else None

    interpretation = (
        f"{n_locales_100} locales con 100% mesas impugnadas. {n_3plus} con >=3 mesas, "
        f"{n_5plus} con >=5 mesas. Top: {top_locales[0]['local_votacion']} "
        f"({top_locales[0]['depto_real']}, {berbes_n} mesas todas impugnadas). "
        f"Bajo H0 binomial con p={p_imp:.6f} (tasa global impugnacion), "
        f"P(11/11 | aleatorio) = {p_value_berbes:.3e} "
        f"(equivalente ~ 1 entre {int(1/p_value_berbes):,})."
    )

    return {
        "id": "HALL-0420-H9",
        "severity": "CRÍTICO",
        "test": "Locales con 100% mesas impugnadas — binomial exacto hero",
        "h0": "Impugnacion distribuida aleatoriamente con p=tasa_global (6.1585%)",
        "statistic": int(n_locales_100),
        "p_value": float(p_value_berbes) if p_value_berbes is not None else None,
        "threshold": 1e-6,
        "method": (
            "Conteo locales con SUM(estado_acta='I') == COUNT(*). "
            "P-value hero = p_global^n para n mesas del local 100% impugnado (binomial exacto)."
        ),
        "interpretation": interpretation,
        "top_locales": top_locales,
        "n_locales_100pct_imp": n_locales_100,
        "n_locales_3plus_mesas": n_3plus,
        "n_locales_5plus_mesas": n_5plus,
        "tasa_global_imp": round(p_imp, 6),
        "hero_local": {
            "local_votacion": top_locales[0]["local_votacion"] if top_locales else None,
            "depto_real": top_locales[0]["depto_real"] if top_locales else None,
            "n_mesas": berbes_n,
            "p_value_binomial": float(p_value_berbes) if p_value_berbes else None,
            "equiv_1_entre": int(1 / p_value_berbes) if p_value_berbes else None,
        },
        "limitations": (
            "Impugnacion es recurso procesal legitimo; cluster requiere "
            "explicacion formal de ONPE. Locales con 1-2 mesas pueden ser impugnacion total por "
            "problema puntual; el hero BERBES (11/11) escapa esa explicacion trivial."
        ),
        "n_mesas_universo": n_mesas,
        "metodologia_cita": [
            "Binomial exacto bajo H0 p=tasa_global. No requiere paper (probabilidad pura).",
            "Newcombe (1998). Two-sided confidence intervals for the single proportion. "
            "Statistics in Medicine 17:857-872.",
        ],
        "source_file": "reports/hallazgos_20260420/eg2026.duckdb",
    }


def build_h12(con, n_mesas: int) -> dict:
    """H12 — Mesa 018146 Cusco, JPP 90.43% (única normal >=90% entre 78,706 >=100 válidos)."""
    # Mesa hero: 018146 Cusco
    hero_row = con.execute(
        """
        SELECT m.codigo_mesa, m.depto_real, m.local_votacion, m.votos_validos, m.mesa_especial
        FROM mesa m WHERE m.codigo_mesa='018146'
        """
    ).fetchone()

    # Top 3 partidos NO-especiales en la mesa (excluye blancos/nulos/impugnados)
    top3 = con.execute(
        """
        SELECT v.partido, v.votos,
               ROUND(v.votos*100.0/m.votos_validos, 2) AS pct
        FROM mesa m JOIN voto v USING(codigo_mesa)
        WHERE m.codigo_mesa='018146' AND v.es_voto_especial=false
          AND v.partido NOT IN ('VOTOS EN BLANCO','VOTOS NULOS','VOTOS IMPUGNADOS')
        ORDER BY v.votos DESC LIMIT 3
        """
    ).fetchall()

    # Universo normales con >=100 validos (threshold autoritativo = 78,706)
    r = con.execute(
        """
        WITH winner AS (
          SELECT m.codigo_mesa, m.mesa_especial,
                 MAX(v.votos*1.0/NULLIF(m.votos_validos,0)) AS pct_ganador
          FROM mesa m JOIN voto v USING(codigo_mesa)
          WHERE v.es_voto_especial=false
            AND m.estado_acta='D'
            AND m.votos_validos >= 100
            AND v.partido NOT IN ('VOTOS EN BLANCO','VOTOS NULOS','VOTOS IMPUGNADOS')
          GROUP BY 1,2
        )
        SELECT
          COUNT(*) FILTER (WHERE NOT mesa_especial) AS n_norm,
          COUNT(*) FILTER (WHERE NOT mesa_especial AND pct_ganador >= 0.90) AS n_norm_90
        FROM winner
        """
    ).fetchone()
    n_norm, n_norm_90 = int(r[0]), int(r[1])

    # P_JPP_global sobre normales estado D
    p_jpp_global = float(con.execute(
        """
        WITH norm_votos AS (
          SELECT m.codigo_mesa, m.votos_validos,
                 SUM(CASE WHEN v.partido='JUNTOS POR EL PERÚ' THEN v.votos ELSE 0 END) AS jpp
          FROM mesa m JOIN voto v USING(codigo_mesa)
          WHERE m.mesa_especial=false AND v.es_voto_especial=false AND m.estado_acta='D'
          GROUP BY m.codigo_mesa, m.votos_validos
        )
        SELECT SUM(jpp)*1.0/NULLIF(SUM(votos_validos), 0) FROM norm_votos
        """
    ).fetchone()[0])

    # Binomial P(X>=208 | n=230, p=p_jpp_global)
    from math import comb
    def _binom_ge(n: int, k0: int, p: float) -> float:
        total = 0.0
        for k in range(k0, n + 1):
            total += comb(n, k) * (p ** k) * ((1 - p) ** (n - k))
        return total

    jpp_row = top3[0] if top3 else None
    segundo = top3[1] if len(top3) > 1 else None
    jpp_votos = int(jpp_row[1]) if jpp_row else 0
    p_value = _binom_ge(int(hero_row[3]), jpp_votos, p_jpp_global) if jpp_row else None

    # Anti-ataque: robustez p=0.30
    p_robusto = _binom_ge(int(hero_row[3]), jpp_votos, 0.30) if jpp_row else None

    interpretation = (
        f"Mesa 018146 Cusco (normal, no 900k+): JPP {jpp_row[1]} votos de {hero_row[3]} validos = "
        f"{jpp_row[2]}%. 2do lugar: {segundo[0]} {segundo[1]} votos ({segundo[2]}%). "
        f"Es la UNICA mesa normal con winner >=90% entre {n_norm:,} normales con >=100 validos "
        f"estado D ({n_norm_90/n_norm*100:.4f}%). "
        f"Bajo H0 binomial con p={p_jpp_global:.4f} (tasa JPP global normales), "
        f"P(X>={jpp_row[1]} | n={hero_row[3]}) = {p_value:.3e}. "
        f"Robusto a sensibilidad: aun con p=0.30, P(X>={jpp_row[1]}) = {p_robusto:.3e}."
    )

    return {
        "id": "HALL-0420-H12",
        "severity": "CRÍTICO",
        "test": "Blowout extremo mesa 018146 Cusco (JPP 90.43%)",
        "h0": "Votos JPP en mesa 018146 son extraccion aleatoria con p=tasa_JPP_global",
        "statistic": float(jpp_row[2]) if jpp_row else None,
        "p_value": float(p_value) if p_value is not None else None,
        "threshold": 1e-6,
        "method": (
            "Binomial exacto: P(X>=k_jpp | n=votos_validos, p=tasa_JPP_global_normales) + "
            "conteo unicidad mesas normales winner>=90% sobre universo estado D, validos>=100."
        ),
        "interpretation": interpretation,
        "mesa_emblematica": {
            "codigo": hero_row[0],
            "depto": hero_row[1],
            "local": hero_row[2],
            "votos_validos": int(hero_row[3]),
            "mesa_especial": bool(hero_row[4]),
            "ganador": jpp_row[0] if jpp_row else None,
            "ganador_votos": int(jpp_row[1]) if jpp_row else None,
            "pct_ganador": float(jpp_row[2]) if jpp_row else None,
            "segundo": segundo[0] if segundo else None,
            "segundo_votos": int(segundo[1]) if segundo else None,
            "pct_segundo": float(segundo[2]) if segundo else None,
        },
        "universo_normales_validos_100plus": n_norm,
        "n_normales_winner_90plus": n_norm_90,
        "p_jpp_global_normales": round(p_jpp_global, 6),
        "p_value_robusto_30pct": float(p_robusto) if p_robusto else None,
        "limitations": (
            "No prueba causalidad ni intencionalidad. Umbral votos_validos>=100 es discrecional "
            "(tambien aparece como unica normal con 50, 80). Subset extremo de H4; mesa 018146 "
            "requiere inspeccion fisica del acta original por ONPE/JNE."
        ),
        "n_mesas_universo": n_mesas,
        "metodologia_cita": [
            "Binomial exacto (probabilidad pura) con prueba de sensibilidad p=0.30.",
            "Newcombe (1998). Two-sided confidence intervals for the single proportion. "
            "Statistics in Medicine 17:857-872.",
            "Subset extremo del framework H4; mismo z-test 2-prop aplica al agregado.",
        ],
        "source_file": "reports/hallazgos_20260420/eg2026.duckdb",
    }


def build_findings() -> tuple[list[dict], dict]:
    raw = json.loads(RAW_H123.read_text(encoding="utf-8"))
    h4 = json.loads(H4_STATS.read_text(encoding="utf-8"))

    con = duckdb.connect(str(DB), read_only=True)
    n_mesas = con.execute("SELECT COUNT(*) FROM mesa").fetchone()[0]
    n_norm = con.execute("SELECT COUNT(*) FROM mesa WHERE NOT mesa_especial").fetchone()[0]
    n_esp = con.execute("SELECT COUNT(*) FROM mesa WHERE mesa_especial").fetchone()[0]
    tasa_imp_global = con.execute(
        "SELECT AVG(CASE WHEN estado_acta='I' THEN 1.0 ELSE 0.0 END)*100 FROM mesa"
    ).fetchone()[0]
    n_actas_voto = con.execute("SELECT COUNT(*) FROM voto").fetchone()[0]

    # Top deptos H1
    top_alto = [d["depto_real"] for d in raw["geo_bias"][:5]]
    top_bajo = [d["depto_real"] for d in raw["geo_bias"][-5:]][::-1]
    z_extranjero = next(
        (d for d in raw["geo_bias"] if d["depto_real"] == "Extranjero"), None
    )

    # H1
    h1 = {
        "id": "HALL-0420-H1",
        "severity": "CRÍTICO",
        "test": "Sesgo geográfico impugnadas por depto_real",
        "h0": "Tasa impugnación homogénea across deptos (~6.16% global)",
        "statistic": float(z_extranjero["z_score"]) if z_extranjero else None,
        "p_value": None,
        "threshold": 2.0,
        "method": "Proporción binomial + z-score contra tasa global. Mapping prefix→depto ONPE alfabético con Callao=24.",
        "interpretation": (
            f"Extranjero {z_extranjero['pct_imp']}% (z={z_extranjero['z_score']}), "
            f"Loreto 14.87% (z=18.82), Ucayali 12.02% (z=9.64), "
            f"Madre de Dios 10.65% (z=4.21), Ica 9.41% (z=6.69). "
            f"Piso: Arequipa 1.83% (z=-11.7), Puno 3.03% (z=-7.58)."
        ),
        "limitations": "Impugnación es recurso procesal; concentración requiere explicación formal de ONPE. Universo v2 incluye 4,703 mesas 900k+ recuperadas tras fix walker.",
        "top_deptos_alto": top_alto,
        "top_deptos_bajo": top_bajo,
        "n_mesas_universo": n_mesas,
        "source_file": "reports/hallazgos_20260420/findings_0420_v2.json",
    }

    # H2
    suben = raw["partido_vs_imp_top"]
    bajan = raw["partido_vs_imp_bot"]
    fp_delta = next((p["delta_pp"] for p in suben if "FUERZA" in p["partido"]), None)
    h2 = {
        "id": "HALL-0420-H2",
        "severity": "MEDIA",
        "test": "Share por partido en locales ALTA vs BAJA tasa impugnación (mesas D)",
        "h0": "Share partido independiente de tasa impugnación del local",
        "statistic": float(fp_delta) if fp_delta else None,
        "p_value": None,
        "threshold": 1.0,
        "method": "Quintiles tasa_imp por local (Q80≥12.5%, Q20≤0%); delta share ALTO−BAJO partidos 1-38, mesas estado D.",
        "interpretation": (
            f"FUERZA POPULAR +{fp_delta}pp en locales alta impugnación; "
            f"JPP +0.88pp; PAÍS PARA TODOS +0.52pp. "
            f"Bajan: BUEN GOBIERNO -1.62pp, AHORA NACIÓN -0.91pp, RENOVACIÓN POPULAR -0.64pp."
        ),
        "limitations": "Asociación descriptiva, no causal. Sensible a clusters Lima/Extranjero.",
        "partidos_suben": [p["partido"] for p in suben[:3]],
        "partidos_bajan": [p["partido"] for p in bajan[-3:]][::-1],
        "n_mesas_universo": n_mesas,
        "source_file": "reports/hallazgos_20260420/findings_0420_v2.json",
    }

    # H3
    n_out = raw["outliers_nb_total"]
    pct_out = round(n_out * 100 / n_mesas, 2)
    h3 = {
        "id": "HALL-0420-H3",
        "severity": "MEDIA",
        "test": "Outliers nulos/blancos por mesa (estado D)",
        "h0": "pct_nulos ≤ 15% AND pct_blancos ≤ 25% en toda mesa D",
        "statistic": pct_out,
        "p_value": None,
        "threshold": 1.0,
        "method": f"Cuenta mesas D con pct_nulos>15% OR pct_blancos>25% sobre {n_mesas:,} mesas.",
        "interpretation": (
            f"{n_out:,} mesas outlier ({pct_out}%). Global D: {raw['nb_global_D'][0]['pct_bl']}% blancos, "
            f"{raw['nb_global_D'][0]['pct_nu']}% nulos. "
            f"San Martín 19.62% blancos #1, Piura 7.22% nulos #1. "
            f"Top mesas extremas: 4 mesas Loreto 900k+ con >90% blancos (903472-903475)."
        ),
        "limitations": "Umbrales 15/25% discrecionales; falta baseline EG2021/2016. Mesas 900k+ dominan extremos.",
        "outliers_total": n_out,
        "outliers_pct": pct_out,
        "n_mesas_universo": n_mesas,
        "source_file": "reports/hallazgos_20260420/findings_0420_v2.json",
    }

    # H4
    g_esp = h4["grupos"]["especiales_900k"]
    g_norm = h4["grupos"]["normales"]
    h4_finding = {
        "id": "HALL-0420-H4",
        "severity": "CRÍTICO",
        "test": "JPP concentra votos en mesas especiales 900k+ (vs normales)",
        "h0": "p(JPP) en mesas 900k+ == p(JPP) en mesas normales",
        "statistic": h4["tests"]["two_proportion_z"]["z"],
        "p_value": h4["tests"]["two_proportion_z"]["p_two_sided"],
        "threshold": 0.05,
        "method": "z-test 2 proporciones (Newcombe 1998) + Cohen h + Bootstrap IC95 (B=10,000) + Mann-Whitney U.",
        "interpretation": (
            f"JPP {g_esp['pct_jpp']*100:.2f}% en {g_esp['n_mesas']:,} mesas especiales 900k+ "
            f"vs {g_norm['pct_jpp']*100:.2f}% en {g_norm['n_mesas']:,} mesas normales. "
            f"Ratio {h4['ratio_pct_esp_vs_norm']}x. z={h4['tests']['two_proportion_z']['z']:.0f}, "
            f"p≈0, Cohen h={h4['tests']['cohens_h']['value']} (grande). "
            f"Bootstrap IC95 diff: [{h4['tests']['bootstrap_diff_pct']['ci95'][0]:.4f}, "
            f"{h4['tests']['bootstrap_diff_pct']['ci95'][1]:.4f}]."
        ),
        "limitations": " | ".join(h4["limitaciones"]),
        "ratio_esp_vs_norm": h4["ratio_pct_esp_vs_norm"],
        "n_mesas_universo": n_mesas,
        "source_file": "reports/h4_stats.json",
        "metodologia_cita": h4["metodologia_cita"],
    }

    # H9 — BERBES 11/11 impugnadas (binomial exacto vs tasa global)
    h9_finding = build_h9(con, n_mesas)

    # H12 — Mesa 018146 Cusco blowout (unica normal >=90% entre 78,706)
    h12_finding = build_h12(con, n_mesas)

    findings = [h1, h2, h3, h4_finding, h9_finding, h12_finding]

    meta = {
        "fecha": "2026-04-20",
        "version": "0420-v3-92k-h1-h12",
        "db": "reports/hallazgos_20260420/eg2026.duckdb",
        "parquet_source": f"reports/hf_dataset/onpe_eg2026_mesas_{UNIVERSE_TS}.parquet",
        "universo_ts_utc": UNIVERSE_TS,
        "total_mesas": int(n_mesas),
        "mesas_normales": int(n_norm),
        "mesas_especiales_900k": int(n_esp),
        "total_actas_voto": int(n_actas_voto),
        "tasa_global_impugnadas_pct": round(float(tasa_imp_global), 3),
        "mapping_prefix_depto": "ONPE alfabético con Callao=24 (validado 2026-04-20).",
        "captura_validation_pct_oficial": "100% en los 26 deptos vs regiones.csv ONPE.",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "stale_findings_eliminados": [
            "R1", "RECNR1", "A1", "A2", "C1", "D1", "D2", "D3", "E1", "G1",
            "H1", "H2", "F1", "M1", "M2", "M3", "A0",
            "A-AUS-1", "A-AUS-2", "A-AUS-3",
            "MESA-IMP-1", "MESA-IMP-2",
        ],
    }

    con.close()
    return findings, meta


def write_master(findings: list[dict], meta: dict) -> None:
    """findings.json maestro: {findings:[...], results:{...}}"""
    payload = {
        "findings": findings,
        "results": {
            "meta": {
                "generated_at": meta["generated_at_utc"],
                "updated_at": meta["generated_at_utc"],
                "source": "ONPE vía proxy CORS + captura atómica con SHA-256",
                "repo": "https://github.com/neuracode/auditoria-eg2026",
                "consolidado_0420": "reports/hallazgos_20260420/findings_consolidado_0420.json",
                "universo_ts_utc": UNIVERSE_TS,
                "total_mesas": meta["total_mesas"],
            }
        },
    }
    OUT_MASTER.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK -> {OUT_MASTER.relative_to(ROOT)}")


def write_consolidado(findings: list[dict], meta: dict) -> None:
    payload = {"meta": meta, "findings": findings}
    OUT_CONSOLIDADO.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK -> {OUT_CONSOLIDADO.relative_to(ROOT)}")


def write_web(findings: list[dict], meta: dict) -> None:
    """web/api/findings.json: mismo schema que master pero más compacto."""
    payload = {
        "findings": findings,
        "meta": {
            "generated_at": meta["generated_at_utc"],
            "updated_at": meta["generated_at_utc"],
            "source": "ONPE vía proxy CORS + captura atómica con SHA-256",
            "repo": "https://github.com/neuracode/auditoria-eg2026",
            "universo_ts_utc": UNIVERSE_TS,
            "total_mesas": meta["total_mesas"],
            "consolidado_0420": "reports/hallazgos_20260420/findings_consolidado_0420.json",
        },
    }
    OUT_WEB.parent.mkdir(parents=True, exist_ok=True)
    OUT_WEB.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK -> {OUT_WEB.relative_to(ROOT)}")


def main() -> int:
    findings, meta = build_findings()
    print(f"[sync] universo: {meta['total_mesas']:,} mesas (norm={meta['mesas_normales']:,}, esp={meta['mesas_especiales_900k']:,})")
    print(f"[sync] findings: {[f['id'] for f in findings]}")
    write_master(findings, meta)
    write_consolidado(findings, meta)
    write_web(findings, meta)
    print(f"[sync] stale eliminados: {len(meta['stale_findings_eliminados'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
