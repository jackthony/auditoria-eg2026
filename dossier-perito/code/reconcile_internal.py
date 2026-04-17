"""
src/analysis/reconcile_internal.py

Finding A0 — Reconciliación interna ONPE: agregado nacional vs suma desagregada regional.

Motivación:
-----------
Ciudadano reportó (17-abril-2026, 08:42-08:57) que la UI ONPE mostraba 633
actas pendientes en agregado mientras el desagregado regional sumaba 773.

Test directo sobre snapshots capturados:
- ¿Suma(regiones) == nacional para cada métrica publicada?
- Si no: la UI/API oficial tiene inconsistencia de agregación.

Este finding NO prueba error en conteo de votos (salto lógico del autor del
post original). Sí demuestra que el sistema tiene integridad de agregación
débil en la capa de presentación.

Severidad: ALTA procesal si diff_actas × votos_prom_acta > margen_final.

Uso:
    py src/analysis/reconcile_internal.py

Outputs:
    reports/reconcile_internal.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load_snapshot(capture_dir: Path) -> tuple[dict, list[dict]]:
    """Carga national + regions desde captures/<ts>/raw/snap{1,2}.json."""
    raw = capture_dir / "raw"
    snaps = sorted(raw.glob("snap*.json"))
    if not snaps:
        raise FileNotFoundError(f"No hay snap*.json en {raw}")

    national = None
    all_regions: list[dict] = []
    seen_names: set[str] = set()

    for p in snaps:
        with open(p, encoding="utf-8") as f:
            data = json.load(f)
        if national is None and "national" in data:
            national = data["national"]
        for r in data.get("regions", []):
            if r.get("name") not in seen_names:
                all_regions.append(r)
                seen_names.add(r["name"])

    if national is None:
        raise ValueError(f"No se encontró 'national' en snapshots de {raw}")

    return national, all_regions


def reconcile(national: dict, regions: list[dict]) -> dict:
    """Compara totales nacionales vs suma desagregada de regiones.

    NOTA MATEMATICA (post-revision red-team):
    Los 4 campos (totalActas, contabilizadas, enviadasJee, pendientesJee)
    estan algebraicamente relacionados: totalActas = contabilizadas +
    enviadasJee + pendientesJee. Por tanto, diff(total) = diff(cont) +
    diff(jee) + diff(pend). Sumar los |diff| triplica la magnitud real.

    Metrica correcta: actas_movidas = max(|diff_cont|, |diff_jee|, |diff_pend|)
    que representa el minimo numero de actas que deben reclasificarse para
    hacer coincidir nacional con regional.
    """
    sum_total = sum(r.get("totalActas", 0) for r in regions)
    sum_cont = sum(r.get("contabilizadas", 0) for r in regions)
    sum_jee = sum(r.get("enviadasJee", 0) for r in regions)
    sum_pend_pure = sum_total - sum_cont - sum_jee

    nat_total = national.get("totalActas", 0)
    nat_cont = national.get("contabilizadas", 0)
    nat_jee = national.get("enviadasJee", 0)
    nat_pend = national.get("pendientesJee", 0)

    diffs = {
        "totalActas": sum_total - nat_total,
        "contabilizadas": sum_cont - nat_cont,
        "enviadasJee": sum_jee - nat_jee,
        "pendientesJee": sum_pend_pure - nat_pend,
    }

    # Métrica honesta: actas que deben reclasificarse para conciliar.
    # Si los diffs son {0, -4, -17, +21}, movieron 21 actas entre buckets.
    actas_movidas = max(abs(v) for v in diffs.values())

    # Métrica auxiliar: discrepancia neta total (debe ser 0 si invariante
    # totalActas = cont + jee + pend se cumple en ambos lados).
    diff_neto = (diffs["contabilizadas"] + diffs["enviadasJee"]
                 + diffs["pendientesJee"] - diffs["totalActas"])

    # Votos promedio por acta (para traducir discrepancia a votos)
    votos_emitidos = national.get("votosEmitidos", 0)
    if nat_cont > 0:
        votos_prom_acta = votos_emitidos / nat_cont
    else:
        votos_prom_acta = 0

    potencial_votos = actas_movidas * votos_prom_acta

    return {
        "nacional": {
            "totalActas": nat_total,
            "contabilizadas": nat_cont,
            "enviadasJee": nat_jee,
            "pendientesJee": nat_pend,
        },
        "desagregado_suma": {
            "totalActas": sum_total,
            "contabilizadas": sum_cont,
            "enviadasJee": sum_jee,
            "pendientes_puras": sum_pend_pure,
        },
        "diffs": diffs,
        "actas_movidas": actas_movidas,
        "diff_neto_invariante": diff_neto,
        "votos_prom_por_acta": round(votos_prom_acta, 1),
        "potencial_votos_en_zona_gris": round(potencial_votos, 0),
        "nota_metodologica": (
            "actas_movidas = max(|diff| por categoria). Es el minimo de actas "
            "que deben reclasificarse entre contabilizadas/JEE/pendientes para "
            "reconciliar nacional con regional. Suma ingenua de |diffs| "
            "triplicaria por dependencia algebraica."
        ),
    }


def run(root: Path | None = None) -> dict:
    root = root or ROOT

    captures = sorted((root / "captures").glob("*Z"))
    if not captures:
        raise FileNotFoundError("No hay capturas en captures/")

    latest = captures[-1]
    national, regions = load_snapshot(latest)

    # Validar completitud del snapshot (26 regiones = 25 dept + Extranjero)
    if len(regions) != 26:
        raise ValueError(
            f"Snapshot incompleto: {len(regions)} regiones (esperado 26). "
            f"Directorio: {latest.name}. Abortar para no reportar finding "
            f"sobre data parcial."
        )

    rec = reconcile(national, regions)

    # Margen actual para contextualizar severidad
    candidates = national.get("candidates", {})
    votos_sanch = candidates.get("sanch_v", 0)
    votos_rla = candidates.get("rla_v", 0)
    margen = abs(votos_sanch - votos_rla)

    ratio_votos_zona_gris_vs_margen = (
        rec["potencial_votos_en_zona_gris"] / margen if margen > 0 else float("inf")
    )

    hay_discrepancia = rec["actas_movidas"] > 0

    if not hay_discrepancia:
        severity = "INFO"
        title = "Reconciliacion interna ONPE OK: nacional == suma regiones."
    elif ratio_votos_zona_gris_vs_margen > 1.0:
        severity = "ALTA"
        title = (
            f"A0 — Inconsistencia agregacion ONPE: {rec['actas_movidas']} actas "
            f"no reconcilian nacional vs regional (~{rec['potencial_votos_en_zona_gris']:.0f} "
            f"votos potenciales vs margen {margen}, ratio {ratio_votos_zona_gris_vs_margen:.1f}x)"
        )
    else:
        severity = "MEDIA"
        title = (
            f"A0 — Inconsistencia agregacion ONPE: {rec['actas_movidas']} actas "
            f"no reconcilian nacional vs regional (por debajo del margen)"
        )

    finding = {
        "id": "A0",
        "severity": severity,
        "title": title,
        "description": (
            "Reconciliacion interna entre el agregado nacional publicado por ONPE y "
            "la suma desagregada de las 26 regiones (25 departamentos + Extranjero). "
            "No prueba error en conteo de votos; demuestra inconsistencia de la capa "
            "de presentacion/agregacion. Requiere explicacion formal de ONPE."
        ),
    }

    out = {
        "method": "Reconciliacion interna ONPE nacional vs suma regiones",
        "snapshot_dir": str(latest.name),
        "fecha": "2026-04-17",
        "reconciliacion": rec,
        "contexto": {
            "margen_sanch_rla": margen,
            "ratio_votos_zona_gris_vs_margen": round(ratio_votos_zona_gris_vs_margen, 2),
        },
        "findings": [finding],
        "caveat": (
            "La discrepancia NO prueba error en conteo de votos (salto logico que "
            "aparecio en el post ciudadano). Puede deberse a: timestamp desalineado "
            "entre endpoint nacional y regional, categoria no contabilizada en el "
            "desagregado, o actas migrando entre estados entre calculo nacional y "
            "regional. Cualquiera sea la causa, ONPE debe explicar."
        ),
    }

    out_dir = root / "reports"
    out_dir.mkdir(exist_ok=True, parents=True)
    (out_dir / "reconcile_internal.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )

    print(f"── A0: Reconciliacion interna ONPE ──")
    print(f"  Snapshot: {latest.name}")
    print(f"  totalActas  nat={rec['nacional']['totalActas']} sum={rec['desagregado_suma']['totalActas']} diff={rec['diffs']['totalActas']:+d}")
    print(f"  contab      nat={rec['nacional']['contabilizadas']} sum={rec['desagregado_suma']['contabilizadas']} diff={rec['diffs']['contabilizadas']:+d}")
    print(f"  enviadasJee nat={rec['nacional']['enviadasJee']} sum={rec['desagregado_suma']['enviadasJee']} diff={rec['diffs']['enviadasJee']:+d}")
    print(f"  pendientes  nat={rec['nacional']['pendientesJee']} sum={rec['desagregado_suma']['pendientes_puras']} diff={rec['diffs']['pendientesJee']:+d}")
    print(f"  actas_movidas={rec['actas_movidas']} (max|diff|), votos potenciales={rec['potencial_votos_en_zona_gris']:.0f}")
    print(f"  Margen Sanch-RLA: {margen}")
    print(f"  [{severity}] {title}")

    return out


def main():
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")
    run()


if __name__ == "__main__":
    main()
