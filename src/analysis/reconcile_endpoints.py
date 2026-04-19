"""
Reconcile contable cross-endpoint — MESA-02.

Verifica consistencia entre los 4 endpoints ONPE de una captura:
  - totales.json            (resumen global)
  - mesa_totales.json       (conteo de mesas)
  - mapa_calor.json         (actas por ámbito)
  - presidencial.json       (votos por candidato)

Detecta discrepancias matemáticas entre agregados. Cualquier mismatch
>= tolerancia se marca como finding.

Uso:
    py src\\analysis\\reconcile_endpoints.py captures\\YYYYMMDDTHHMMSSZ\\
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

# Tolerancias
TOL_VOTES_ABS = 1        # voto (redondeo ONPE)
TOL_PCT_ABS = 0.05       # puntos porcentuales (redondeo a 3 decimales)


def _load(capture_dir: Path, name: str) -> dict:
    p = capture_dir / "raw" / f"{name}.json"
    with p.open(encoding="utf-8") as f:
        return json.load(f)["data"]


def reconcile(capture_dir: Path) -> dict:
    totales = _load(capture_dir, "totales")
    mesa = _load(capture_dir, "mesa_totales")
    mapa = _load(capture_dir, "mapa_calor")
    presi = _load(capture_dir, "presidencial")

    findings: list[dict] = []

    # Check 1: mesa_totales suma == totalActas
    mesas_sum = mesa["mesasInstaladas"] + mesa["mesasNoInstaladas"] + mesa["mesasPendientes"]
    if mesas_sum != totales["totalActas"]:
        findings.append({
            "id": "REC-MESA-SUM",
            "severity": "CRITICO",
            "check": "mesasInstaladas+noInstaladas+pendientes == totalActas",
            "expected": totales["totalActas"],
            "observed": mesas_sum,
            "delta": mesas_sum - totales["totalActas"],
        })

    # Check 2: actas contabilizadas + enviadasJee + pendientesJee == totalActas
    actas_sum = totales["contabilizadas"] + totales["enviadasJee"] + totales["pendientesJee"]
    if abs(actas_sum - totales["totalActas"]) > TOL_VOTES_ABS:
        findings.append({
            "id": "REC-ACTAS-SUM",
            "severity": "CRITICO",
            "check": "contabilizadas+enviadasJee+pendientesJee == totalActas",
            "expected": totales["totalActas"],
            "observed": actas_sum,
            "delta": actas_sum - totales["totalActas"],
        })

    # Check 3: mapa_calor.actasContabilizadas == totales.contabilizadas
    if isinstance(mapa, list) and mapa:
        mapa_actas = mapa[0].get("actasContabilizadas")
        if mapa_actas != totales["contabilizadas"]:
            findings.append({
                "id": "REC-MAPA-ACTAS",
                "severity": "MEDIA",
                "check": "mapa_calor.actasContabilizadas == totales.contabilizadas",
                "expected": totales["contabilizadas"],
                "observed": mapa_actas,
                "delta": (mapa_actas or 0) - totales["contabilizadas"],
            })

    # Separar agrupaciones políticas de blancos/nulos (el endpoint los mezcla).
    def _is_special(c: dict) -> bool:
        name = (c.get("nombreAgrupacionPolitica") or "").upper()
        return "BLANCO" in name or "NULO" in name

    agrupaciones = [c for c in presi if not _is_special(c)]
    especiales = [c for c in presi if _is_special(c)]
    votos_validos = sum(c.get("totalVotosValidos", 0) for c in agrupaciones)
    votos_blancos_nulos = sum(c.get("totalVotosValidos", 0) for c in especiales)

    # Check 4a: suma de votos válidos (sin blancos/nulos) == totales.totalVotosValidos
    if abs(votos_validos - totales["totalVotosValidos"]) > TOL_VOTES_ABS:
        findings.append({
            "id": "REC-VOTOS-VALIDOS",
            "severity": "CRITICO",
            "check": "sum(agrupaciones.totalVotosValidos) == totales.totalVotosValidos",
            "expected": totales["totalVotosValidos"],
            "observed": votos_validos,
            "delta": votos_validos - totales["totalVotosValidos"],
        })

    # Check 4b: válidos + blancos + nulos == totalVotosEmitidos
    emitidos_sum = votos_validos + votos_blancos_nulos
    if abs(emitidos_sum - totales["totalVotosEmitidos"]) > TOL_VOTES_ABS:
        findings.append({
            "id": "REC-VOTOS-EMITIDOS",
            "severity": "CRITICO",
            "check": "sum(todos.totalVotosValidos) == totales.totalVotosEmitidos",
            "expected": totales["totalVotosEmitidos"],
            "observed": emitidos_sum,
            "delta": emitidos_sum - totales["totalVotosEmitidos"],
        })

    # Check 5: suma de porcentajes validos == 100
    pct_sum = round(sum(c.get("porcentajeVotosValidos", 0) for c in agrupaciones), 3)
    if abs(pct_sum - 100.0) > TOL_PCT_ABS:
        findings.append({
            "id": "REC-PCT-SUM",
            "severity": "MEDIA",
            "check": "sum(porcentajeVotosValidos) == 100",
            "expected": 100.0,
            "observed": pct_sum,
            "delta": round(pct_sum - 100.0, 3),
        })

    # Check 6: porcentajeActasContabilizadas coherente
    pct_calc = round(totales["contabilizadas"] / totales["totalActas"] * 100, 3)
    pct_reported = totales["actasContabilizadas"]
    if abs(pct_calc - pct_reported) > TOL_PCT_ABS:
        findings.append({
            "id": "REC-PCT-ACTAS",
            "severity": "BAJA",
            "check": "actasContabilizadas == contabilizadas/totalActas*100",
            "expected": pct_reported,
            "observed": pct_calc,
            "delta": round(pct_calc - pct_reported, 3),
        })

    return {
        "capture": capture_dir.name,
        "snapshot": {
            "actasContabilizadas_pct": totales["actasContabilizadas"],
            "contabilizadas": totales["contabilizadas"],
            "totalActas": totales["totalActas"],
            "totalVotosValidos": totales["totalVotosValidos"],
            "candidatos": len(presi),
            "mesasInstaladas": mesa["mesasInstaladas"],
            "mesasNoInstaladas": mesa["mesasNoInstaladas"],
            "mesasPendientes": mesa["mesasPendientes"],
        },
        "checks_total": 7,
        "votos_validos_sum": votos_validos,
        "votos_blancos_nulos_sum": votos_blancos_nulos,
        "findings_count": len(findings),
        "findings": findings,
        "status": "OK" if not findings else "DISCREPANCIAS",
    }


def main() -> int:
    if len(sys.argv) < 2:
        print("Uso: py src\\analysis\\reconcile_endpoints.py captures\\<ts>\\", file=sys.stderr)
        return 2
    capture_dir = Path(sys.argv[1]).resolve()
    if not capture_dir.exists():
        print(f"ERROR: {capture_dir} no existe", file=sys.stderr)
        return 2

    result = reconcile(capture_dir)

    out_path = Path("reports") / "reconcile_endpoints.json"
    out_path.parent.mkdir(exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"[reconcile] captura: {result['capture']}")
    print(f"[reconcile] status: {result['status']}")
    print(f"[reconcile] checks: {result['checks_total']}  findings: {result['findings_count']}")
    for fnd in result["findings"]:
        print(f"  [{fnd['severity']}] {fnd['id']}: {fnd['check']}")
        print(f"     esperado={fnd['expected']}  observado={fnd['observed']}  delta={fnd['delta']}")
    print(f"[reconcile] output: {out_path}")
    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
