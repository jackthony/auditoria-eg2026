"""
src/analysis/run_all.py

Ejecuta los módulos de análisis vivos y consolida findings.

Uso:
    py src\\analysis\\run_all.py

Salidas:
    reports/ausentismo_comparacion.json
    reports/summary.txt
"""

from __future__ import annotations

import json
import sys
from io import StringIO
from pathlib import Path

from . import impugnation_rates, impugnation_bias, ausentismo, mesa_impugnadas

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def main() -> None:
    ROOT = Path(__file__).resolve().parents[2]

    if not (ROOT / "data/processed/regiones.csv").exists():
        print("ERROR: falta data/processed/regiones.csv", file=sys.stderr)
        sys.exit(1)

    all_findings: list[dict] = []
    buf = StringIO()
    orig_stdout = sys.stdout

    class Tee:
        def write(self, s: str) -> None:
            orig_stdout.write(s)
            buf.write(s)
        def flush(self) -> None:
            orig_stdout.flush()

    sys.stdout = Tee()  # type: ignore[assignment]

    try:
        # H1/H2/H3 — impugnación por región
        r = impugnation_rates.run(ROOT)
        all_findings.extend(r["findings"])
        print()

        # H2 — sesgo político en impugnaciones
        print("── Sesgo político en impugnaciones ──")
        impugnation_bias.main()
        bias_path = ROOT / "reports" / "impugnation_bias.json"
        if bias_path.exists():
            bias = json.loads(bias_path.read_text(encoding="utf-8"))
            all_findings.extend(bias.get("findings", []))
        print()

        # Ausentismo histórico
        print("── Ausentismo histórico ──")
        ausentismo.main()
        print()

        # Mesas impugnadas (requiere captura mesa-a-mesa)
        print("── Mesas impugnadas ──")
        try:
            imp_out = mesa_impugnadas.run()
            all_findings.extend(imp_out.get("hallazgos", []))
        except SystemExit:
            print("  [skip] sin captura mesa-a-mesa disponible")
        print()

        print("═" * 70)
        print(" RESUMEN")
        print("═" * 70)
        for f in all_findings:
            print(f"  [{f.get('severity','—'):7}] {f.get('id','—')}  {f.get('interpretation', f.get('title', '—'))}")

    finally:
        sys.stdout = orig_stdout

    out_dir = ROOT / "reports"
    out_dir.mkdir(exist_ok=True, parents=True)
    (out_dir / "summary.txt").write_text(buf.getvalue(), encoding="utf-8")
    print(f"\n✓ {len(all_findings)} hallazgos — resumen en reports/summary.txt")


if __name__ == "__main__":
    main()
