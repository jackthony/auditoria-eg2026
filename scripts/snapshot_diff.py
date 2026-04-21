"""
scripts/snapshot_diff.py

Compara último captures/ vs snapshot previo. Emite signal.json si hay cambio
relevante. Usado por sensor.yml cron en GitHub Actions.

Flujo:
1. Lee último captures/{tsUTC}/ (por mtime)
2. Carga reports/snapshots/last.json (si existe)
3. Computa diff de métricas clave (universe N, mesa counts, impugnadas %, etc.)
4. Si delta ≥ umbral → escribe reports/signals/sig_<ts>.json + imprime signal
5. Siempre actualiza snapshot

Uso:
  py scripts/snapshot_diff.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAPTURES = ROOT / "captures"
SNAPSHOTS_DIR = ROOT / "reports" / "snapshots"
SIGNALS_DIR = ROOT / "reports" / "signals"
DB_PATH = ROOT / "reports" / "hallazgos_20260420" / "eg2026.duckdb"

THRESHOLDS = {
    "delta_pp_high": 1.0,
    "delta_pp_medium": 0.5,
    "new_mesa_min_n": 10,
}


def latest_capture_dir() -> Path | None:
    if not CAPTURES.exists():
        return None
    dirs = [p for p in CAPTURES.iterdir() if p.is_dir()]
    if not dirs:
        return None
    return max(dirs, key=lambda p: p.stat().st_mtime)


def read_manifest(capture_dir: Path) -> list[dict]:
    m = capture_dir / "MANIFEST.jsonl"
    if not m.exists():
        return []
    return [json.loads(line) for line in m.read_text(encoding="utf-8").splitlines() if line.strip()]


def compute_snapshot(capture_dir: Path) -> dict:
    manifest = read_manifest(capture_dir)
    total_bytes = sum(e.get("size", 0) for e in manifest)
    files_count = len(manifest)

    db_sha = ""
    if DB_PATH.exists():
        h = hashlib.sha256()
        with open(DB_PATH, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        db_sha = h.hexdigest()

    return {
        "ts_utc": datetime.now(timezone.utc).isoformat(),
        "capture_dir": capture_dir.name,
        "files_count": files_count,
        "total_bytes": total_bytes,
        "db_sha256": db_sha,
    }


def load_last_snapshot() -> dict | None:
    last = SNAPSHOTS_DIR / "last.json"
    if not last.exists():
        return None
    return json.loads(last.read_text(encoding="utf-8"))


def diff_snapshots(prev: dict, curr: dict) -> dict:
    return {
        "files_delta": curr["files_count"] - prev["files_count"],
        "bytes_delta": curr["total_bytes"] - prev["total_bytes"],
        "db_changed": curr["db_sha256"] != prev["db_sha256"],
    }


def priority_from_diff(d: dict) -> str:
    if d["db_changed"] or abs(d["files_delta"]) >= 10:
        return "high"
    if abs(d["files_delta"]) >= 3:
        return "medium"
    if d["files_delta"] > 0:
        return "low"
    return "skip"


def emit_signal(curr: dict, diff: dict, priority: str) -> Path:
    SIGNALS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    sig_path = SIGNALS_DIR / f"sig_{ts}.json"
    signal = {
        "id": f"sig_{ts}",
        "ts_utc": datetime.now(timezone.utc).isoformat(),
        "capture_ts": curr["capture_dir"],
        "trigger": "db_changed" if diff["db_changed"] else "files_delta",
        "diff": diff,
        "priority": priority,
        "action": "dispatch_pipeline" if priority in ("high", "medium") else "update_snapshot_only",
    }
    sig_path.write_text(json.dumps(signal, indent=2), encoding="utf-8")
    return sig_path


def save_snapshot(curr: dict) -> None:
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    (SNAPSHOTS_DIR / "last.json").write_text(json.dumps(curr, indent=2), encoding="utf-8")


def main() -> int:
    cap = latest_capture_dir()
    if cap is None:
        print(json.dumps({"status": "no_captures"}))
        return 0

    curr = compute_snapshot(cap)
    prev = load_last_snapshot()

    if prev is None:
        save_snapshot(curr)
        print(json.dumps({"status": "first_snapshot_saved", "snapshot": curr}))
        return 0

    diff = diff_snapshots(prev, curr)
    priority = priority_from_diff(diff)

    if priority != "skip":
        sig_path = emit_signal(curr, diff, priority)
        save_snapshot(curr)
        print(json.dumps({
            "status": "signal_emitted",
            "signal_path": str(sig_path.relative_to(ROOT)),
            "priority": priority,
            "diff": diff,
        }))
    else:
        save_snapshot(curr)
        print(json.dumps({"status": "no_change", "diff": diff}))

    return 0


if __name__ == "__main__":
    sys.exit(main())
