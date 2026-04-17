"""
make.py — Orquestador simple tipo Makefile para Windows.

Uso:
    py make.py               # ejecuta todo: capture -> build -> analyze -> report
    py make.py capture       # sólo captura
    py make.py build         # sólo consolidación
    py make.py analyze       # sólo análisis
    py make.py report        # sólo informe final
    py make.py verify        # verifica integridad de capturas
    py make.py test          # corre los tests pytest
    py make.py clean         # borra outputs regenerables
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


def report():
    run([PY, str(ROOT / "src" / "report" / "figures.py")])
    run([PY, str(ROOT / "src" / "report" / "build_report.py")])


def test():
    run([PY, "-m", "pytest", "tests/", "-v"])


def clean():
    targets = [
        ROOT / "data" / "processed",
        ROOT / "reports" / "figures",
        ROOT / "reports" / "Informe_Tecnico_v1.docx",
        ROOT / "reports" / "findings.json",
        ROOT / "reports" / "summary.txt",
        ROOT / "reports" / "impugnadas_por_region.csv",
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
    "capture": capture,
    "verify":  verify,
    "build":   build,
    "analyze": analyze,
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
