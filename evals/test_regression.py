"""
evals/test_regression.py

Regression: detecta drift si cambian prompts de data-forensic o stats-expert.

Uso:
    py -m pytest evals/test_regression.py -v
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "evals" / "golden"
LATEST = ROOT / "reports" / "stat_findings"

FINDINGS = ["h1", "h2", "h3", "h4", "h9", "h12"]


def _load_golden(fid: str) -> dict:
    return json.loads((GOLDEN / f"stat_{fid}.json").read_text(encoding="utf-8"))


def _load_latest(fid: str) -> dict:
    files = sorted(LATEST.glob(f"stat_{fid}_*.json"))
    assert files, f"No stat_finding para {fid}"
    return json.loads(files[-1].read_text(encoding="utf-8"))


def _extract_p(d: dict) -> float | None:
    """Extrae p_value del stat_finding en cualquiera de sus formas."""
    for key in ("p_value", "p_val", "pvalue"):
        v = d.get(key)
        if v is None:
            continue
        if isinstance(v, (int, float)):
            return float(v)
        if isinstance(v, str):
            m = re.search(r"([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)", v)
            if m:
                try:
                    return float(m.group(1))
                except ValueError:
                    pass
    stat = d.get("statistic") or {}
    for k in ("binomial_p_value", "p_value", "p"):
        v = stat.get(k)
        if isinstance(v, (int, float)):
            return float(v)
    notation = stat.get("p_value_notation") if isinstance(stat, dict) else None
    if isinstance(notation, str):
        m = re.search(r"([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)", notation)
        if m:
            try:
                return float(m.group(1))
            except ValueError:
                pass
    return None


def _log10_diff(a: float, b: float) -> float:
    if a <= 0 or b <= 0:
        return abs(a - b)
    return abs(math.log10(a) - math.log10(b))


@pytest.mark.parametrize("fid", FINDINGS)
def test_p_value_same_order(fid: str) -> None:
    g = _extract_p(_load_golden(fid))
    l = _extract_p(_load_latest(fid))
    if g is None and l is None:
        pytest.skip(f"{fid}: sin p_value top-level (finding no-paramétrico)")
    assert g is not None, f"{fid}: golden sin p_value"
    assert l is not None, f"{fid}: latest sin p_value"
    assert _log10_diff(g, l) < 1.0, f"{fid}: p drift — golden {g} vs latest {l}"


@pytest.mark.parametrize("fid", FINDINGS)
def test_severity_unchanged(fid: str) -> None:
    assert _load_golden(fid)["severity"] == _load_latest(fid)["severity"]


@pytest.mark.parametrize("fid", FINDINGS)
def test_effect_size_close(fid: str) -> None:
    g = _load_golden(fid).get("effect_size", {})
    l = _load_latest(fid).get("effect_size", {})
    gv = g.get("value") if isinstance(g, dict) else None
    lv = l.get("value") if isinstance(l, dict) else None
    if gv is None or lv is None:
        pytest.skip(f"{fid}: sin effect_size")
    assert abs(gv - lv) < 0.05, f"{fid}: effect drift — golden {gv} vs latest {lv}"


@pytest.mark.parametrize("fid", FINDINGS)
def test_method_citation_in_registry(fid: str) -> None:
    citations = _load_latest(fid).get("method_citation", [])
    assert citations, f"{fid}: sin method_citation"
    registry_keys = {
        "clopper", "pearson", "newcombe", "cohen", "efron", "tibshirani",
        "klimek", "mann", "whitney", "bonferroni", "fisher",
        "binomial exacto", "scipy", "mebane",
    }
    for c in citations:
        c_lower = c.lower()
        assert any(k in c_lower for k in registry_keys), (
            f"{fid}: cita fuera de registry — {c}"
        )
