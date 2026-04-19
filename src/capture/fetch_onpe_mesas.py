"""
src/capture/fetch_onpe_mesas.py — Walker mesa-a-mesa ONPE (MESA-03).

Itera codigoMesa 000001..MAX_MESA y guarda respuesta de
/presentacion-backend/actas/buscar/mesa?codigoMesa=X (contiene las 5 elecciones).

Output:
    captures/{ts}/mesas/{codigoMesa}.json.gz    (raw gzipped, fuera de git)
    captures/{ts}/MESAS_MANIFEST.jsonl          (SHA-256 por mesa)
    captures/{ts}/mesas_summary.json            (stats)

Resumable: si captures/{ts}/mesas/{codigo}.json.gz existe, skip.

Uso:
    py src/capture/fetch_onpe_mesas.py --ts 20260419T040000Z --from 1 --to 88064
    py src/capture/fetch_onpe_mesas.py --ts auto --rate 5
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

PROXY_BASE = os.environ.get(
    "ONPE_PROXY_BASE",
    "https://onpe-proxy-neuracode.jackgptgod.workers.dev",
)
ENDPOINT = "/presentacion-backend/actas/buscar/mesa"
USER_AGENT = "AuditoriaEG2026/1.0 (mesa-walker - personero acreditado)"

MAX_MESA_DEFAULT = 88064
RATE_DEFAULT = 5.0
TIMEOUT = 20
RETRIES = 3


def utc_compact() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def fetch_mesa(codigo: str, id_eleccion: int = 10) -> tuple[int, bytes]:
    url = f"{PROXY_BASE}{ENDPOINT}?codigoMesa={codigo}&idEleccion={id_eleccion}"
    headers = {"User-Agent": USER_AGENT, "Cache-Control": "no-cache"}
    last_exc = None
    for attempt in range(RETRIES):
        try:
            r = requests.get(url, headers=headers, timeout=TIMEOUT)
            return r.status_code, r.content
        except Exception as e:
            last_exc = e
            time.sleep(2 ** attempt)
    return 0, f"FETCH_ERROR: {last_exc}".encode()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ts", default="auto", help="timestamp de captura (auto = now)")
    ap.add_argument("--from", dest="mfrom", type=int, default=1)
    ap.add_argument("--to", type=int, default=MAX_MESA_DEFAULT)
    ap.add_argument("--rate", type=float, default=RATE_DEFAULT, help="req/s")
    ap.add_argument("--eleccion", type=int, default=10, help="idEleccion (contexto)")
    args = ap.parse_args()

    ROOT = Path(__file__).resolve().parents[2]
    ts = utc_compact() if args.ts == "auto" else args.ts
    cap_dir = ROOT / "captures" / ts
    mesas_dir = cap_dir / "mesas"
    mesas_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = cap_dir / "MESAS_MANIFEST.jsonl"

    delay = 1.0 / args.rate if args.rate > 0 else 0
    total = args.to - args.mfrom + 1
    ok = skipped = empty = errs = 0
    t0 = time.time()
    mf = manifest_path.open("a", encoding="utf-8", newline="\n")

    print(f"[walker] ts={ts}  range={args.mfrom}..{args.to}  rate={args.rate}/s")
    print(f"[walker] dir: {mesas_dir}")
    print(f"[walker] ETA: {total * delay / 3600:.1f}h")

    try:
        for n in range(args.mfrom, args.to + 1):
            codigo = f"{n:06d}"
            out = mesas_dir / f"{codigo}.json.gz"
            if out.exists():
                skipped += 1
                continue

            started = datetime.now(timezone.utc).isoformat()
            status, content = fetch_mesa(codigo, args.eleccion)

            if status == 200 and len(content) > 100:
                gz = gzip.compress(content)
                out.write_bytes(gz)
                entry = {
                    "codigoMesa": codigo,
                    "fetched_at_utc": started,
                    "http_status": status,
                    "bytes_raw": len(content),
                    "bytes_gz": len(gz),
                    "sha256_raw": sha256_bytes(content),
                    "local_path": f"mesas/{codigo}.json.gz",
                }
                mf.write(json.dumps(entry, separators=(",", ":")) + "\n")
                mf.flush()
                ok += 1
            elif status == 204:
                empty += 1
            else:
                errs += 1

            if (n - args.mfrom + 1) % 100 == 0:
                elapsed = time.time() - t0
                rate = (n - args.mfrom + 1) / elapsed if elapsed else 0
                remaining = (args.to - n) / rate if rate else 0
                print(f"  [{n:>6}/{args.to}]  ok={ok} skip={skipped} empty={empty} err={errs}  "
                      f"{rate:.1f}req/s  ETA={remaining/60:.0f}min")

            if delay > 0:
                time.sleep(delay)

    except KeyboardInterrupt:
        print("\n[walker] interrumpido (resumable: correr de nuevo skipea existentes)")
    finally:
        mf.close()

    summary = {
        "ts": ts,
        "range": [args.mfrom, args.to],
        "ok": ok,
        "skipped_existing": skipped,
        "empty_204": empty,
        "errors": errs,
        "elapsed_s": round(time.time() - t0, 1),
    }
    (cap_dir / "mesas_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print()
    print(f"[walker] {ok} mesas ok, {skipped} skip, {empty} vacías, {errs} errores")
    print(f"[walker] manifest: {manifest_path}")
    return 0 if errs == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
