"""
src/analysis/run_all.py

Ejecuta todos los módulos de análisis en secuencia y consolida findings.

Uso:
    py src\\analysis\\run_all.py

Salidas:
    reports/findings.json       — hallazgos consolidados con severidad
    reports/impugnadas_por_region.csv
    reports/summary.txt         — resumen de consola
"""

from __future__ import annotations

import json
import sys
from io import StringIO
from pathlib import Path

from . import reconcile, impugnation_rates, benford, temporal, jee_simulation


def main():
    ROOT = Path(__file__).resolve().parents[2]

    # Verificar pre-requisitos
    if not (ROOT / "data/processed/regiones.csv").exists():
        print("ERROR: falta data/processed/regiones.csv", file=sys.stderr)
        print("Ejecuta primero: py src\\process\\build_dataset.py", file=sys.stderr)
        sys.exit(1)

    all_findings = []
    all_results = {}

    # Capturar output en un buffer para guardarlo
    buf = StringIO()
    orig_stdout = sys.stdout

    def tee(s):
        orig_stdout.write(s)
        buf.write(s)

    # Redirigir prints a tee
    class Tee:
        def write(self, s): tee(s)
        def flush(self): orig_stdout.flush()
    sys.stdout = Tee()

    try:
        # 1. Reconciliación
        r = reconcile.run(ROOT)
        all_findings.extend(r["findings"])
        all_results["reconciliation"] = {"severe": r["severe"], "rows": r["rows"]}

        print()

        # 2. Impugnación por región
        r = impugnation_rates.run(ROOT)
        all_findings.extend(r["findings"])
        all_results["impugnation"] = {
            "outliers": r["outliers"],
            "ztest": r["ztest_lima_vs_resto"],
            "stratum": r["by_stratum"].to_dict("records") if r["by_stratum"] is not None else [],
        }

        print()

        # 3. Benford
        r = benford.run(ROOT)
        all_findings.extend(r["findings"])
        all_results["benford"] = {
            "pool": {k: v for k, v in (r["pool"] or {}).items()
                     if k in ("n", "chi2", "p_value", "conforms")},
        }

        print()

        # 4. Temporal
        r = temporal.run(ROOT)
        all_findings.extend(r["findings"])

        print()

        # 5. Simulación JEE
        r = jee_simulation.run(ROOT)
        all_findings.extend(r["findings"])
        all_results["jee_simulation"] = {
            "margen_actual": r["margen_actual"],
            "votos_juego": r["votos_juego"],
            "margen_proyectado": r["margen_proyectado"],
            "break_even_pct_rla": r["break_even_pct_rla"],
            "historico_pct_rla": r["historico_pct_rla"],
        }

        print()

        # Resumen
        print("═" * 70)
        print(" RESUMEN DE HALLAZGOS")
        print("═" * 70)
        for f in all_findings:
            print(f"  [{f['severity']:7}] {f.get('id','—')}  {f['title']}")

    finally:
        sys.stdout = orig_stdout

    # Guardar findings y summary
    out_dir = ROOT / "reports"
    out_dir.mkdir(exist_ok=True, parents=True)

    (out_dir / "findings.json").write_text(
        json.dumps({"findings": all_findings, "results": all_results},
                   indent=2, ensure_ascii=False, default=str),
        encoding="utf-8"
    )
    (out_dir / "summary.txt").write_text(buf.getvalue(), encoding="utf-8")

    print(f"\n✓ {len(all_findings)} hallazgos escritos a reports/findings.json")
    print(f"✓ resumen completo en reports/summary.txt")


if __name__ == "__main__":
    main()
