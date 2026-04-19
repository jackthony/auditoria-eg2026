"""
src/analysis/fdr_correction.py

Aplica corrección Benjamini-Hochberg (FDR) sobre todos los p-valores
del pipeline para controlar la tasa de falsos descubrimientos.

Motivación: con ~20 tests independientes a α=0.05, ~1 falso positivo
esperado por azar. FDR limita la proporción de rechazos falsos.

Input:  reports/findings.json
Output: reports/fdr_results.json
Exit:   0 OK, 1 error
"""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any

from statsmodels.stats.multitest import multipletests

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(message)s")

ROOT = Path(__file__).resolve().parents[2]
FINDINGS = ROOT / "reports" / "findings.json"
OUT = ROOT / "reports" / "fdr_results.json"

ALPHA = 0.05


def extract_pvalues(data: dict) -> list[dict[str, Any]]:
    """Extrae todos los p-valores relevantes del findings.json.

    Cada entry: {test, p_value, raw_path}
    """
    r = data.get("results", {})
    items: list[dict[str, Any]] = []

    imp = r.get("impugnation", {})
    if "ztest" in imp and "p_value" in imp["ztest"]:
        items.append({"test": "impugnation.ztest_lima_vs_resto",
                      "p_value": float(imp["ztest"]["p_value"])})

    bf = r.get("benford", {}).get("pool", {})
    if "p_value" in bf:
        items.append({"test": "benford.pool_chi2", "p_value": float(bf["p_value"])})

    ib = r.get("impugnation_bias", {})
    for k, v in ib.items():
        if isinstance(v, dict) and "p_value" in v:
            items.append({"test": f"impugnation_bias.{k}",
                          "p_value": float(v["p_value"])})

    iv = r.get("impugnation_velocity", {}).get("ventana_12h", {}).get("mann_whitney", {})
    if "p_value" in iv:
        items.append({"test": "impugnation_velocity.mann_whitney_12h",
                      "p_value": float(iv["p_value"])})

    ld = r.get("last_digit", {})
    for cand, v in ld.items():
        if isinstance(v, dict) and "chi2_p_value" in v:
            items.append({"test": f"last_digit.{cand}.chi2",
                          "p_value": float(v["chi2_p_value"])})

    sc = r.get("spatial_cluster", {})
    for var, v in sc.items():
        if isinstance(v, dict) and "p" in v:
            items.append({"test": f"spatial_cluster.{var}",
                          "p_value": float(v["p"])})

    return items


def apply_fdr(items: list[dict[str, Any]], alpha: float = ALPHA) -> dict[str, Any]:
    if not items:
        return {"alpha": alpha, "n_tests": 0, "results": []}

    pvals = [i["p_value"] for i in items]
    reject, qvals, _, _ = multipletests(pvals, alpha=alpha, method="fdr_bh")

    results = []
    for item, r, q in zip(items, reject, qvals):
        results.append({
            "test": item["test"],
            "p_value": item["p_value"],
            "q_value_fdr_bh": float(q),
            "reject_at_fdr_05": bool(r),
            "survives": "SI" if bool(r) else "NO",
        })

    results.sort(key=lambda x: x["p_value"])

    survivors = [r for r in results if r["reject_at_fdr_05"]]

    return {
        "alpha": alpha,
        "method": "Benjamini-Hochberg",
        "n_tests": len(items),
        "n_survive_fdr": len(survivors),
        "interpretation": (
            f"De {len(items)} p-valores, {len(survivors)} sobreviven FDR BH "
            f"a α={alpha}. Tests que no sobreviven no deben reportarse como "
            "significativos sin contexto adicional."
        ),
        "results": results,
    }


def main() -> int:
    if not FINDINGS.exists():
        logger.error("No existe %s", FINDINGS)
        return 1

    data = json.loads(FINDINGS.read_text(encoding="utf-8"))
    items = extract_pvalues(data)
    out = apply_fdr(items, ALPHA)

    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Escrito: %s", OUT)
    logger.info("n=%d · sobreviven FDR BH α=%.2f: %d",
                out["n_tests"], out["alpha"], out["n_survive_fdr"])
    logger.info("")
    for r in out["results"]:
        mark = "✓" if r["reject_at_fdr_05"] else "·"
        logger.info(f"  {mark} {r['test']:<48} p={r['p_value']:.4g}  q={r['q_value_fdr_bh']:.4g}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
