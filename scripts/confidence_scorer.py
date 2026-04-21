"""
scripts/confidence_scorer.py

Score determinista 0-1 por finding. Input: stat_finding.json + challenge.md.
Output: confidence score + breakdown. Usado por hitl_router.py para decidir publish tier.

Fórmula:
  score = 0.4 * p_factor + 0.3 * effect_factor + 0.3 * challenger_factor

Uso:
  py scripts/confidence_scorer.py <stat_finding.json> <challenge.md>
"""

from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path


def extract_p_value(stat: dict) -> float | None:
    """Extrae p_value en cualquiera de sus formas."""
    for key in ("p_value", "p_val", "pvalue"):
        v = stat.get(key)
        if isinstance(v, (int, float)):
            return float(v)
        if isinstance(v, str):
            m = re.search(r"([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)", v)
            if m:
                try:
                    return float(m.group(1))
                except ValueError:
                    pass
    nested = stat.get("statistic") or {}
    if isinstance(nested, dict):
        for k in ("binomial_p_value", "p_value", "p", "p_chi2", "p_val"):
            v = nested.get(k)
            if isinstance(v, (int, float)):
                return float(v)
    # log_p (log10 p) fallback
    for key in ("log10_p", "log_p"):
        v = stat.get(key)
        if isinstance(v, (int, float)):
            return 10 ** float(v)
    return None


def extract_effect_size(stat: dict) -> float | None:
    """Extrae effect size (Cohen h preferido, fallback OR log, z-score)."""
    es = stat.get("effect_size")
    if isinstance(es, dict):
        v = es.get("value") or es.get("cohen_h") or es.get("h")
        if isinstance(v, (int, float)):
            return abs(float(v))
    if isinstance(es, (int, float)):
        return abs(float(es))

    nested = stat.get("statistic") or {}
    if isinstance(nested, dict):
        # Preferencia: cohen_h, cohen_d, h
        for k in ("cohen_h", "cohen_d", "h"):
            v = nested.get(k)
            if isinstance(v, (int, float)):
                return abs(float(v))
        # OR: convertir a escala proxy. OR>=5 → ~0.8 (large). log(OR)/log(5)
        or_val = nested.get("OR") or nested.get("odds_ratio")
        if isinstance(or_val, (int, float)) and or_val > 0:
            return min(1.0, abs(math.log(or_val)) / math.log(5))
        # z-score proxy (z>=3.5 → 1.0)
        z = nested.get("z")
        if isinstance(z, (int, float)):
            return min(1.0, abs(z) / 3.5)
    return None


def extract_challenger_verdict(challenge_md: str) -> str:
    """Busca SOBREVIVE | DEBIL | CAE en el markdown."""
    upper = challenge_md.upper()
    if "VEREDICTO: CAE" in upper or "VERDICT: CAE" in upper:
        return "CAE"
    if "VEREDICTO: DEBIL" in upper or "VERDICT: DEBIL" in upper or "DÉBIL" in upper:
        return "DEBIL"
    if "VEREDICTO: SOBREVIVE" in upper or "VERDICT: SOBREVIVE" in upper:
        return "SOBREVIVE"
    # Default conservador: si no está explícito, trato como DEBIL
    return "DEBIL"


def p_factor(p: float | None) -> float:
    """0.5 si None, 1.0 si p==0 (underflow) o p<=1e-15, 0 si p>=0.5."""
    if p is None:
        return 0.5
    if p <= 0:
        return 1.0
    log = -math.log10(p)
    return max(0.0, min(1.0, log / 15.0))


def effect_factor(h: float | None) -> float:
    """Cohen h: 0.2=small, 0.5=medium, 0.8=large. 1.0 si h>=0.8."""
    if h is None:
        return 0.5
    return min(1.0, h / 0.8)


def challenger_factor(verdict: str) -> float:
    return {"SOBREVIVE": 1.0, "DEBIL": 0.5, "CAE": 0.0}.get(verdict, 0.5)


def score_finding(stat_path: Path | str, challenge_path: Path | str | None) -> dict:
    stat_path = Path(stat_path)
    stat = json.loads(stat_path.read_text(encoding="utf-8"))
    challenge_md = ""
    if challenge_path:
        cp = Path(challenge_path)
        if cp.exists():
            challenge_md = cp.read_text(encoding="utf-8")

    p = extract_p_value(stat)
    h = extract_effect_size(stat)
    verdict = extract_challenger_verdict(challenge_md)

    pf = p_factor(p)
    ef = effect_factor(h)
    cf = challenger_factor(verdict)

    score = 0.4 * pf + 0.3 * ef + 0.3 * cf

    return {
        "finding_id": stat.get("finding_id") or stat.get("id") or "unknown",
        "score": round(score, 4),
        "breakdown": {
            "p_factor": round(pf, 4),
            "effect_factor": round(ef, 4),
            "challenger_factor": round(cf, 4),
        },
        "inputs": {
            "p_value": p,
            "effect_size": h,
            "challenger_verdict": verdict,
        },
        "tier": tier_from_score(score),
    }


def tier_from_score(score: float) -> str:
    if score >= 0.90:
        return "AUTO"
    if score >= 0.70:
        return "PENDING-JACK"
    return "DRAFT"


def main() -> int:
    if len(sys.argv) < 2:
        print("Uso: py scripts/confidence_scorer.py <stat_finding.json> [challenge.md]", file=sys.stderr)
        return 1

    stat_path = Path(sys.argv[1])
    challenge_path = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    result = score_finding(stat_path, challenge_path)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
