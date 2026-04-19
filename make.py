"""
make.py — Orquestador simple tipo Makefile para Windows.

Uso:
    py make.py                   # ejecuta todo: capture -> build -> analyze -> report
    py make.py capture           # captura backend agregado ONPE
    py make.py capture-mesas     # walker mesa-a-mesa (async, vía Worker)
    py make.py build             # sólo consolidación
    py make.py analyze           # sólo análisis agregado (run_all)
    py make.py analyze-mesas     # análisis mesa-a-mesa (requiere capture-mesas previa)
    py make.py report            # sólo informe final
    py make.py verify            # verifica integridad de capturas
    py make.py test              # corre los tests pytest
    py make.py clean             # borra outputs regenerables
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PY = sys.executable


def run(args, cwd=None):
    print(f"\n$ {' '.join(args)}")
    r = subprocess.run(args, cwd=cwd or ROOT)
    if r.returncode != 0:
        sys.exit(r.returncode)


def capture():
    run([PY, str(ROOT / "src" / "capture" / "fetch_onpe.py")])


def capture_mesas():
    run([PY, str(ROOT / "src" / "capture" / "fetch_onpe_mesas_async.py"),
         "--ts", "auto", "--concurrency", "50"])


def verify():
    captures = sorted(
        [p for p in (ROOT / "captures").iterdir()
         if p.is_dir() and p.name[0].isdigit()]
    )
    if not captures:
        print("No hay capturas para verificar.")
        sys.exit(1)
    for c in captures:
        run([PY, str(ROOT / "src" / "capture" / "verify_manifest.py"), str(c)])


def build():
    run([PY, str(ROOT / "src" / "process" / "build_dataset.py")])


def analyze():
    run([PY, "-m", "src.analysis.run_all"])


def analyze_mesas():
    caps = sorted(
        (p for p in (ROOT / "captures").iterdir()
         if p.is_dir() and (p / "mesas").is_dir()),
        key=lambda p: p.name,
    )
    if not caps:
        print("No hay captura mesa-a-mesa. Ejecuta: py make.py capture-mesas")
        sys.exit(1)
    ts = caps[-1].name
    print(f"[analyze-mesas] ts={ts}")
    run([PY, str(ROOT / "src" / "analysis" / "reconcile_endpoints.py"), str(caps[-1])])
    run([PY, "-m", "src.analysis.reconcile_gap", ts])
    run([PY, str(ROOT / "src" / "analysis" / "validate_acta_vs_mesa.py"), ts])
    run([PY, "-m", "src.analysis.extract_mesa_votes", ts])


def report():
    run([PY, str(ROOT / "src" / "report" / "figures.py")])
    run([PY, str(ROOT / "src" / "report" / "build_report.py")])


def test():
    run([PY, "-m", "pytest", "tests/", "-v"])


def clean():
    reports = ROOT / "reports"
    # NO borrar: ausentismo_comparacion.json (input manual histórico), perito/ (artefactos firmados)
    targets = [
        ROOT / "data" / "processed",
        reports / "figures",
        reports / "findings.json",
        reports / "findings_gap.json",
        reports / "forecast.json",
        reports / "reconcile_endpoints.json",
        reports / "reconcile_internal.json",
        reports / "last_digit.json",
        reports / "spatial_cluster.json",
        reports / "ml_anomalies.json",
        reports / "impugnation_bias.json",
        reports / "impugnation_velocity.json",
        reports / "mesas_summary.json",
        reports / "mesas_presidencial.csv",
        reports / "impugnadas_por_region.csv",
        reports / "summary.txt",
        reports / "validate_acta_vs_mesa.log",
        reports / "Informe_Tecnico_v1.docx",
        reports / "Informe_Tecnico_v1.txt",
        reports / "Informe_Tecnico_RP_v3.pdf",
    ]
    for t in targets:
        if t.is_dir():
            shutil.rmtree(t, ignore_errors=True)
            t.mkdir(parents=True, exist_ok=True)
            print(f"  limpiado: {t.relative_to(ROOT)}")
        elif t.exists():
            t.unlink()
            print(f"  borrado: {t.relative_to(ROOT)}")


def all_():
    build()    # asume que ya hay captura
    analyze()
    report()


ACTIONS = {
    "capture":       capture,
    "capture-mesas": capture_mesas,
    "verify":        verify,
    "build":   build,
    "analyze":       analyze,
    "analyze-mesas": analyze_mesas,
    "report":  report,
    "test":    test,
    "clean":   clean,
    "all":     all_,
}


def main():
    if len(sys.argv) == 1:
        all_()
        return
    action = sys.argv[1]
    fn = ACTIONS.get(action)
    if not fn:
        print(f"Acción desconocida: {action}")
        print(f"Acciones: {', '.join(ACTIONS.keys())}")
        sys.exit(2)
    fn()


if __name__ == "__main__":
    main()
