"""
src/capture/fetch_onpe_mesas_async.py — Walker mesa-a-mesa ASYNC (MESA-03).

Concurrencia configurable. Resumable. Output idéntico a fetch_onpe_mesas.py.

Uso:
    py src/capture/fetch_onpe_mesas_async.py --ts auto --from 1 --to 88064 --concurrency 50
"""
from __future__ import annotations

import argparse
import asyncio
import gzip
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import aiohttp

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

PROXY_BASE = os.environ.get(
    "ONPE_PROXY_BASE",
    "https://onpe-proxy-neuracode.jackgptgod.workers.dev",
)
ENDPOINT = "/presentacion-backend/actas/buscar/mesa"
USER_AGENT = "AuditoriaEG2026/1.0 (mesa-walker async - personero acreditado)"

MAX_MESA_DEFAULT = 88064
TIMEOUT = 25


def utc_compact() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


async def fetch_one(session: aiohttp.ClientSession, codigo: str, id_eleccion: int,
                    mesas_dir: Path, manifest_lines: list, stats: dict,
                    sem: asyncio.Semaphore) -> None:
    out = mesas_dir / f"{codigo}.json.gz"
    if out.exists():
        stats["skipped"] += 1
        return
    url = f"{PROXY_BASE}{ENDPOINT}?codigoMesa={codigo}&idEleccion={id_eleccion}"
    async with sem:
        started = datetime.now(timezone.utc).isoformat()
        for attempt in range(3):
            try:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=TIMEOUT)) as r:
                    content = await r.read()
                    status = r.status
                    break
            except Exception as e:
                if attempt == 2:
                    stats["errors"] += 1
                    return
                await asyncio.sleep(2 ** attempt)

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
        manifest_lines.append(json.dumps(entry, separators=(",", ":")))
        stats["ok"] += 1
    elif status == 204:
        stats["empty"] += 1
    elif status == 429:
        stats["throttled"] += 1
    else:
        stats["errors"] += 1


async def run(args):
    ROOT = Path(__file__).resolve().parents[2]
    ts = utc_compact() if args.ts == "auto" else args.ts
    cap_dir = ROOT / "captures" / ts
    mesas_dir = cap_dir / "mesas"
    mesas_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = cap_dir / "MESAS_MANIFEST.jsonl"

    stats = {"ok": 0, "skipped": 0, "empty": 0, "errors": 0, "throttled": 0}
    sem = asyncio.Semaphore(args.concurrency)
    manifest_lines: list[str] = []

    print(f"[async] ts={ts}  range={args.mfrom}..{args.to}  concurrency={args.concurrency}")
    print(f"[async] dir: {mesas_dir}")

    connector = aiohttp.TCPConnector(limit=args.concurrency * 2)
    headers = {"User-Agent": USER_AGENT, "Cache-Control": "no-cache"}
    t0 = time.time()

    # Flush manifest cada 500 mesas
    async with aiohttp.ClientSession(connector=connector, headers=headers) as session:
        tasks = []
        batch_size = 1000
        for start in range(args.mfrom, args.to + 1, batch_size):
            end = min(start + batch_size - 1, args.to)
            batch = [
                fetch_one(session, f"{n:06d}", args.eleccion, mesas_dir,
                          manifest_lines, stats, sem)
                for n in range(start, end + 1)
            ]
            await asyncio.gather(*batch, return_exceptions=True)
            # Flush manifest
            with manifest_path.open("a", encoding="utf-8", newline="\n") as mf:
                for line in manifest_lines:
                    mf.write(line + "\n")
            manifest_lines.clear()
            elapsed = time.time() - t0
            done = end - args.mfrom + 1
            total = args.to - args.mfrom + 1
            rate = done / elapsed if elapsed else 0
            eta_min = (total - done) / rate / 60 if rate else 0
            print(f"  [{end:>6}/{args.to}] ok={stats['ok']} skip={stats['skipped']} "
                  f"empty={stats['empty']} err={stats['errors']} 429={stats['throttled']}  "
                  f"{rate:.1f}req/s  ETA={eta_min:.0f}min")
            # Backoff si throttled
            if stats["throttled"] > 50:
                print("  [async] muchos 429 — pausa 30s")
                await asyncio.sleep(30)
                stats["throttled"] = 0

    summary = {
        "ts": ts,
        "range": [args.mfrom, args.to],
        "concurrency": args.concurrency,
        **stats,
        "elapsed_s": round(time.time() - t0, 1),
    }
    (cap_dir / "mesas_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print()
    print(f"[async] FIN en {summary['elapsed_s']:.0f}s  ({summary['elapsed_s']/60:.1f}min)")
    print(f"[async] ok={stats['ok']} skip={stats['skipped']} empty={stats['empty']} err={stats['errors']}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ts", default="auto")
    ap.add_argument("--from", dest="mfrom", type=int, default=1)
    ap.add_argument("--to", type=int, default=MAX_MESA_DEFAULT)
    ap.add_argument("--concurrency", type=int, default=50)
    ap.add_argument("--eleccion", type=int, default=10)
    args = ap.parse_args()
    asyncio.run(run(args))
    return 0


if __name__ == "__main__":
    sys.exit(main())
