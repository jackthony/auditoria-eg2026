"""
make.py — Orquestador CLI para auditoria-eg2026.

Uso:
    py make.py verify          # verifica integridad MANIFEST SHA-256
    py make.py analyze         # corre análisis vivos (H1-H3 + ausentismo + impugnadas)
    py make.py report          # genera figuras + docx
    py make.py test            # pytest (15 tests)
    py make.py sync            # sincroniza findings H1-H12 en los 3 JSONs
    py make.py rebuild-db      # rebuild eg2026.duckdb desde parquet
    py make.py clean           # borra outputs regenerables

Comandos archivados (captura cerrada — conteo terminado):
    capture        → src/capture/fetch_onpe.py (requiere IP peruana + Worker)
    capture-mesas  → src/capture/fetch_onpe_mesas_async.py
    build          → src/process/build_dataset.py
    analyze-mesas  → scripts análisis mesa-a-mesa
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PY = sys.executable


def run(args: list[str], cwd: Path | None = None) -> None:
    print(f"\n$ {' '.join(str(a) for a in args)}")
    r = subprocess.run(args, cwd=cwd or ROOT)
    if r.returncode != 0:
        sys.exit(r.returncode)


def verify() -> None:
    captures = sorted(
        p for p in (ROOT / "captures").iterdir()
        if p.is_dir() and p.name[0].isdigit()
    )
    if not captures:
        print("No hay capturas para verificar.")
        sys.exit(1)
    for c in captures:
        run([PY, str(ROOT / "src" / "capture" / "verify_manifest.py"), str(c)])


def analyze() -> None:
    run([PY, "-m", "src.analysis.run_all"])


def report() -> None:
    run([PY, str(ROOT / "src" / "report" / "figures.py")])
    run([PY, str(ROOT / "src" / "report" / "build_report.py")])


def test() -> None:
    run([PY, "-m", "pytest", "tests/", "-v"])


def sync() -> None:
    run([PY, str(ROOT / "scripts" / "sync_findings_v2.py")])


def rebuild_db() -> None:
    run([PY, str(ROOT / "scripts" / "build_duckdb_and_fix.py")])


def clean() -> None:
    reports = ROOT / "reports"
    targets = [
        reports / "figures",
        reports / "summary.txt",
        reports / "impugnation_bias.json",
        reports / "ausentismo_comparacion.json",
        reports / "Informe_Tecnico_v1.docx",
        reports / "Informe_Tecnico_v1.txt",
    ]
    for t in targets:
        if t.is_dir():
            shutil.rmtree(t, ignore_errors=True)
            t.mkdir(parents=True, exist_ok=True)
            print(f"  limpiado: {t.relative_to(ROOT)}")
        elif t.exists():
            t.unlink()
            print(f"  borrado: {t.relative_to(ROOT)}")


ACTIONS: dict[str, object] = {
    "verify":     verify,
    "analyze":    analyze,
    "report":     report,
    "test":       test,
    "sync":       sync,
    "rebuild-db": rebuild_db,
    "clean":      clean,
}


def main() -> None:
    if len(sys.argv) == 1:
        print(__doc__)
        sys.exit(0)
    action = sys.argv[1]
    fn = ACTIONS.get(action)
    if not fn:
        print(f"Acción desconocida: {action!r}")
        print(f"Acciones disponibles: {', '.join(ACTIONS)}")
        sys.exit(2)
    fn()  # type: ignore[operator]


if __name__ == "__main__":
    main()
