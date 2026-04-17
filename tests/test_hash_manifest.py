"""
tests/test_hash_manifest.py

Verifica que los hashes del manifiesto inicial sean consistentes con los
archivos capturados.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
CAPTURES = ROOT / "captures"


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def iter_captures():
    if not CAPTURES.exists():
        return []
    return [p for p in CAPTURES.iterdir() if p.is_dir() and p.name[0].isdigit()]


@pytest.mark.parametrize("capture_dir", iter_captures(),
                          ids=lambda p: p.name)
def test_manifest_integrity(capture_dir):
    """Cada archivo del manifest debe coincidir con su hash."""
    manifest = capture_dir / "MANIFEST.jsonl"
    assert manifest.exists(), f"falta MANIFEST.jsonl en {capture_dir}"

    for lineno, line in enumerate(
            manifest.read_text(encoding="utf-8").strip().split("\n"), 1):
        if not line:
            continue
        entry = json.loads(line)
        local = capture_dir / entry["local_path"]
        assert local.exists(), f"archivo referenciado no existe: {local}"
        actual = sha256_of(local)
        assert actual == entry["sha256"], (
            f"hash mismatch para {entry['endpoint']} en línea {lineno}:\n"
            f"  esperado: {entry['sha256']}\n"
            f"  actual:   {actual}"
        )
