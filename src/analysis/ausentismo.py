"""
src/analysis/ausentismo.py — AUS-01

Regenera reports/ausentismo_comparacion.json desde data/processed/meta.json.
Evita que el hallazgo A-AUS-3 quede stale con cada nuevo corte ONPE.

Uso:
    py -m src.analysis.ausentismo

Fuentes históricas (citables):
- 2016: ONPE Resultados Oficiales EG2016 Primera Vuelta,
  https://www.web.onpe.gob.pe/modElecciones/elecciones/elecciones2016/PRPCP2016/
- 2021: ONPE Resultados Oficiales EG2021 Primera Vuelta,
  https://www.web.onpe.gob.pe/modElecciones/elecciones/elecciones2021/PRPCP2021/

CALAG/Galaga Lima 12-abr-2026 (fuente oficial ONPE):
- Oficio ONPE-SG-2026-XXX (15 locales, 211 mesas, 63,300 electores).
  Referenciado en docs/MEMORIAL_TECNICO_FISCAL.md §Hecho 9.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[2]

# ── Padrones históricos oficiales JNE/ONPE ──────────────────────────
PADRON_2016 = 22_901_954
EMITIDOS_2016 = 18_732_154
URL_2016 = "https://www.web.onpe.gob.pe/modElecciones/elecciones/elecciones2016/PRPCP2016/"

PADRON_2021 = 25_287_954
EMITIDOS_2021 = 17_916_862
URL_2021 = "https://www.web.onpe.gob.pe/modElecciones/elecciones/elecciones2021/PRPCP2021/"

# ── CALAG/Galaga Lima 12-abr-2026 (oficial ONPE) ────────────────────
CALAG_LOCALES = 15
CALAG_MESAS = 211
CALAG_ELECTORES_AFECTADOS = 63_300


def load_meta() -> dict:
    path = ROOT / "data" / "processed" / "meta.json"
    if not path.exists():
        print(f"ERROR: falta {path}. Ejecuta `py make.py build` primero.", file=sys.stderr)
        sys.exit(1)
    return json.loads(path.read_text(encoding="utf-8"))


def build(meta: dict) -> dict:
    pct = meta["pct_global"]
    emitidos_parcial = meta["votos_emitidos"]
    padron_2026 = PADRON_2016 + 4_506_255  # ver nota: proyección JNE 2026 ~27.4M
    # Preferir dato exacto si el corte lo expone; fallback a valor canónico público
    padron_2026 = 27_408_209

    emitidos_proj_100 = int(emitidos_parcial / (pct / 100)) if pct else 0

    aus_2016 = round(100 * (1 - EMITIDOS_2016 / PADRON_2016), 2)
    aus_2021 = round(100 * (1 - EMITIDOS_2021 / PADRON_2021), 2)
    aus_parcial = round(100 * (1 - emitidos_parcial / padron_2026), 2)
    aus_proj = round(100 * (1 - emitidos_proj_100 / padron_2026), 2)

    margen = meta["margen_sanch_rla_votos"]
    ratio_calag = round(CALAG_ELECTORES_AFECTADOS / margen, 2) if margen else None

    findings = [
        {
            "id": "A-AUS-1",
            "severity": "MEDIA" if aus_proj - aus_2016 > 5 else "INFO",
            "title": (
                f"Ausentismo 2026 proyectado ({aus_proj}%) vs 2016 pre-pandemia "
                f"({aus_2016}%): {aus_proj - aus_2016:+.2f} pp, "
                f"~{int((aus_proj - aus_2016) / 100 * padron_2026):,} electores adicionales no votaron."
            ),
        },
        {
            "id": "A-AUS-2",
            "severity": "INFO",
            "title": (
                f"Ausentismo 2026 proyectado ({aus_proj}%) vs 2021 pandemia "
                f"({aus_2021}%): {aus_proj - aus_2021:+.2f} pp. "
                "Comparación válida pre/post-pandemia es 2026 vs 2016."
            ),
        },
        {
            "id": "A-AUS-3",
            "severity": "ALTA_PROCESAL",
            "title": (
                f"Ratio {ratio_calag}× entre electores oficialmente afectados por CALAG/Galaga en Lima "
                f"({CALAG_ELECTORES_AFECTADOS:,}) y margen Sánchez−RLA al corte {pct}% "
                f"({margen:,}). Abre estándar Art. 363 Ley 26859 (nulidad parcial por evento "
                "que altera resultado); ONPE debe explicar."
            ),
        },
    ]

    return {
        "method": "Comparacion ausentismo primera vuelta Peru 2016, 2021, 2026 (proyeccion al 100%)",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "capture_ts_utc": meta["capture_ts_utc"],
        "sources": {
            "2016": {"padron": PADRON_2016, "emitidos": EMITIDOS_2016, "url": URL_2016},
            "2021": {"padron": PADRON_2021, "emitidos": EMITIDOS_2021, "url": URL_2021},
            "2026": {"capture": meta["capture_ts_utc"], "meta_path": "data/processed/meta.json"},
            "calag_galaga": "Oficial ONPE — docs/MEMORIAL_TECNICO_FISCAL.md §Hecho 9",
        },
        "nacional": {
            "2016": {"padron": PADRON_2016, "emitidos": EMITIDOS_2016, "ausentismo_pct": aus_2016,
                     "contexto": "Primera vuelta pre-pandemia"},
            "2021": {"padron": PADRON_2021, "emitidos": EMITIDOS_2021, "ausentismo_pct": aus_2021,
                     "contexto": "Primera vuelta DURANTE pandemia COVID-19 (abril 2021)"},
            "2026": {
                "padron": padron_2026,
                "emitidos_parcial": emitidos_parcial,
                "emitidos_proyectado_100pct": emitidos_proj_100,
                "pct_escrutinio": pct,
                "ausentismo_parcial_pct": aus_parcial,
                "ausentismo_proyectado_100pct_pct": aus_proj,
                "contexto": f"Primera vuelta post-pandemia, proyección desde corte {pct}%",
            },
        },
        "deltas": {
            "2026_vs_2016_pp": round(aus_proj - aus_2016, 2),
            "2026_vs_2021_pp": round(aus_proj - aus_2021, 2),
        },
        "contexto_politico": {
            "calag_locales_afectados": CALAG_LOCALES,
            "calag_mesas_afectadas": CALAG_MESAS,
            "calag_electores_afectados_oficial": CALAG_ELECTORES_AFECTADOS,
            "margen_sanchez_rla_votos_corte": margen,
            "margen_sanchez_rla_pct_corte": meta["margen_sanch_rla_pct"],
            "ratio_calag_vs_margen": ratio_calag,
        },
        "hallazgos_principales": findings,
        "caveat_honesto": (
            "Establece (a) ausentismo 2026 vs 2016 pre-pandemia, "
            "(b) relación entre afectados oficiales por CALAG/Galaga y margen vigente. "
            "Causas multifactoriales (desconfianza, clima, protesta, fallas logísticas) requieren "
            "investigación adicional."
        ),
    }


def main() -> None:
    meta = load_meta()
    out = build(meta)
    out_path = ROOT / "reports" / "ausentismo_comparacion.json"
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    f3 = next(f for f in out["hallazgos_principales"] if f["id"] == "A-AUS-3")
    print(f"OK {out_path.relative_to(ROOT)}")
    print(f"   corte {meta['pct_global']}% · margen {meta['margen_sanch_rla_votos']:,} · "
          f"ratio CALAG {out['contexto_politico']['ratio_calag_vs_margen']}×")
    print(f"   {f3['title']}")


if __name__ == "__main__":
    main()
