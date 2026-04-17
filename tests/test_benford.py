"""
tests/test_benford.py

Tests sanity para la función de Benford: detecta distribuciones anómalas
y acepta distribuciones conformes.
"""

from __future__ import annotations

import random
import numpy as np

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.analysis.benford import first_digit, benford_chi2


def test_first_digit_basics():
    assert first_digit(1) == 1
    assert first_digit(9) == 9
    assert first_digit(123) == 1
    assert first_digit(999) == 9
    assert first_digit(1000) == 1
    assert first_digit(0) is None
    assert first_digit(-5) is None


def test_benford_on_synthetic_benford_distribution():
    """Muestras que siguen Benford: el test debe NO rechazar H0."""
    # Generar números cuyo primer dígito siga Benford
    random.seed(42)
    np.random.seed(42)
    # Distribución ln-uniforme entre 1 y 10^6: sigue Benford por construcción
    values = np.exp(np.random.uniform(np.log(1), np.log(1_000_000), size=500))
    r = benford_chi2(values.tolist())
    assert r["sufficient"]
    # Debería ser conforme (p > 0.05) la gran mayoría del tiempo
    assert r["conforms"], (
        f"test rechazó Benford para una distribución Benford: χ²={r['chi2']:.2f}, p={r['p_value']:.3f}"
    )


def test_benford_on_uniform_first_digit():
    """Si el primer dígito es uniforme (anómalo), el test debe rechazar."""
    # Construir 500 números cuyo primer dígito sea uniformemente {1..9}
    values = []
    for _ in range(500):
        d = random.randint(1, 9)
        rest = random.randint(0, 99999)
        values.append(int(f"{d}{rest}"))
    r = benford_chi2(values)
    assert r["sufficient"]
    # Uniforme ≠ Benford: el test debería marcarlo como no conforme
    assert not r["conforms"], (
        f"test NO rechazó distribución uniforme de primer dígito "
        f"(debería haberlo hecho): p={r['p_value']:.3f}"
    )


def test_benford_insufficient_data():
    r = benford_chi2([1, 2, 3])
    assert not r["sufficient"]
