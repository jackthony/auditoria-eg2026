"""Bucle de captura continua ONPE — cada N minutos.

Uso:
    py scripts/capture_loop.py --interval 15

Corre hasta Ctrl+C. Cada iteración:
  1. Invoca src/capture/fetch_onpe.py
  2. Guarda capture en captures/YYYYMMDDTHHMMSSZ/
  3. Compara hash con captura anterior; si idéntico, loggea "sin cambios".
  4. Si hubo cambio, corre src/process/build_dataset.py y src/analysis/run_all.py.
"""
from __future__ import annotations

import argparse
import hashlib
import logging
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("capture_loop")


def tracking_hash() -> str | None:
    caps = sorted((ROOT / "captures").glob("*/raw/tracking.json"))
    if not caps:
        return None
    return hashlib.sha256(caps[-1].read_bytes()).hexdigest()


def run(cmd: list[str]) -> int:
    log.info("exec: %s", " ".join(cmd))
    proc = subprocess.run(cmd, cwd=ROOT)
    return proc.returncode


def iterate():
    before = tracking_hash()
    rc = run([PY, "src/capture/fetch_onpe.py"])
    if rc != 0:
        log.error("capture falló rc=%d", rc)
        return
    after = tracking_hash()
    if before == after:
        log.info("sin cambios en tracking (proxy cacheado)")
        return
    log.info("tracking actualizado — re-procesando dataset y análisis")
    run([PY, "src/process/build_dataset.py"])
    run([PY, "src/analysis/run_all.py"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--interval", type=int, default=15,
                    help="minutos entre capturas (default 15)")
    ap.add_argument("--max-iters", type=int, default=0,
                    help="número máximo de iteraciones (0 = infinito)")
    args = ap.parse_args()

    n = 0
    log.info("capture_loop iniciado — intervalo=%d min", args.interval)
    while True:
        n += 1
        log.info("=== iteración %d @ %s UTC ===", n,
                 datetime.now(timezone.utc).strftime("%H:%M:%S"))
        try:
            iterate()
        except Exception:
            log.exception("iteración %d falló", n)
        if args.max_iters and n >= args.max_iters:
            log.info("alcanzado max-iters=%d, saliendo", args.max_iters)
            break
        time.sleep(args.interval * 60)


if __name__ == "__main__":
    main()
