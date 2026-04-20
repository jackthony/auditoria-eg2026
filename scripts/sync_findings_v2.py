"""
scripts/sync_findings_v2.py — Sincroniza los 3 findings.json del repo.

Construye HALL-0420-H1/H2/H3/H4 sobre el universo v2 (92,766 mesas) y los
escribe a:
  - reports/findings.json                        (maestro, estructura {findings, results})
  - reports/hallazgos_20260420/findings_consolidado_0420.json  (consolidado con meta)
  - web/api/findings.json                        (endpoint del dashboard)

Borra todos los findings stale (R1, A1, A2, C1, D1-D3, E1, G1, H1, H2, F1,
M1-M3, A0, A-AUS-1/2/3, MESA-IMP-1/2). Decisión: stale → eliminar (a).

Lee:
  - reports/h4_stats.json (HALL-0420-H4 ya calculado por stats_h4_especiales_900k.py)
  - reports/hallazgos_20260420/findings_0420_v2.json (H1/H2/H3 raw output)
  - reports/hallazgos_20260420/eg2026.duckdb (validación universo)
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
        "limitations": "Impugnación es recurso procesal; concentración no implica fraude. Universo v2 incluye 4,703 mesas 900k+ recuperadas tras fix walker.",
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

    findings = [h1, h2, h3, h4_finding]

    meta = {
        "fecha": "2026-04-20",
        "version": "0420-v2-92k",
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
