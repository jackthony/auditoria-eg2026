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

from . import reconcile, impugnation_rates, benford, temporal, jee_simulation, forecast_bayesian, impugnation_bias, impugnation_velocity, last_digit_forensic, spatial_cluster

import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

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

        # 6. Sesgo político en impugnaciones
        print("── Análisis de sesgo político en impugnaciones ──")
        impugnation_bias.main()
        bias_path = ROOT / "reports" / "impugnation_bias.json"
        if bias_path.exists():
            bias = json.loads(bias_path.read_text(encoding="utf-8"))
            all_findings.extend(bias.get("findings", []))
            all_results["impugnation_bias"] = bias["correlaciones"]

        print()

        # 6b. Velocidad temporal de impugnaciones
        print("── Velocidad temporal de impugnaciones (Mann-Whitney pre/post cruce) ──")
        impugnation_velocity.main()
        vel_path = ROOT / "reports" / "impugnation_velocity.json"
        if vel_path.exists():
            vel = json.loads(vel_path.read_text(encoding="utf-8"))
            all_findings.extend(vel.get("findings", []))
            all_results["impugnation_velocity"] = {
                "cruce": vel["resumen"]["cruce"],
                "ventana_12h": next((w for w in vel["ventanas"] if w["hours"] == 12), None),
            }

        print()

        # 7. Forecast bayesiano jerárquico (Dirichlet-Multinomial + Beta prior JEE)
        print("── Forecast bayesiano (Linzer 2013 / NYT Needle) ──")
        forecast_bayesian.main()
        fc_path = ROOT / "reports" / "forecast.json"
        if fc_path.exists():
            fc = json.loads(fc_path.read_text(encoding="utf-8"))
            p_central = fc["escenarios"]["central"]["p_rla_supera_sanchez"]
            p_mixto = fc["escenario_mixto"]["p_rla_supera_sanchez"]
            all_findings.append({
                "id": "F1",
                "severity": "CRÍTICO" if p_central > 0.30 else "MEDIA",
                "title": f"Modelo bayesiano: P(RLA supera Sánchez) = {p_central:.1%} central / {p_mixto:.1%} mixto (n=10,000 simulaciones)",
            })
            all_results["forecast"] = {
                "p_central": p_central,
                "p_mixto": p_mixto,
                "margen_p50_central": fc["escenarios"]["central"]["margen_final"]["p50"],
                "margen_p5_central": fc["escenarios"]["central"]["margen_final"]["p5"],
                "margen_p95_central": fc["escenarios"]["central"]["margen_final"]["p95"],
            }

        print()

        # 8. Test forense M1: último dígito (Mebane 2006 / Beber-Scacco 2012)
        print("── M1: Último dígito de vote counts (test Mebane / Beber-Scacco) ──")
        ld = last_digit_forensic.run()
        all_findings.append({
            "id": ld["finding"]["id"],
            "severity": ld["finding"]["severity"],
            "title": ld["finding"]["description"],
        })
        all_results["last_digit"] = {
            cand: {k: v for k, v in r.items() if k in ("n", "chi2_p_value", "p_round_digits", "verdict")}
            for cand, r in ld["candidates"].items()
        }

        print()

        # 9. Test forense M2: Moran's I clustering espacial
        print("── M2: Autocorrelación espacial (Moran's I + permutación 999) ──")
        sc = spatial_cluster.run()
        all_findings.append({
            "id": sc["finding"]["id"],
            "severity": sc["finding"]["severity"],
            "title": sc["finding"]["description"],
        })
        all_results["spatial_cluster"] = {
            var: {"I": t["morans_I"], "p": t["permutation_p_value"], "verdict": t["verdict"]}
            for var, t in sc["tests"].items()
        }
        all_results["spatial_cluster"]["bivariate_rla_impug"] = {
            "I": sc["bivariate_share_rla_x_tasa_impug"]["morans_I_bivariate"],
            "p": sc["bivariate_share_rla_x_tasa_impug"]["permutation_p_value"],
            "verdict": sc["bivariate_share_rla_x_tasa_impug"]["verdict"],
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
