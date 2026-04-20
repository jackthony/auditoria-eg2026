"""
src/capture/fetch_onpe_mesas_async.py — Walker mesa-a-mesa ASYNC (MESA-03).

Concurrencia configurable. Resumable. Output idéntico a fetch_onpe_mesas.py.

Universo ONPE EG2026 confirmado 2026-04-20:
  - Normales:  000001-088064 (88,063 mesas; 087704 no existe)
  - Especiales (900k+): 900001-904703 (4,703 mesas — descubierto post-cierre)

Uso:
    py src/capture/fetch_onpe_mesas_async.py --ts auto --concurrency 50
    py src/capture/fetch_onpe_mesas_async.py --ts auto --ranges 1-88064,900001-904703
    py src/capture/fetch_onpe_mesas_async.py --ts auto --from 1 --to 88064  # legacy
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
DEFAULT_RANGES = [(1, 88064), (900001, 904703)]
TIMEOUT = 25


def parse_ranges(s: str) -> list[tuple[int, int]]:
    """Parse '1-88064,900001-904703' into [(1,88064),(900001,904703)]."""
    out: list[tuple[int, int]] = []
    for chunk in s.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        a, b = chunk.split("-")
        out.append((int(a), int(b)))
    return out


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

    # Resolver ranges: --ranges > [--from,--to] > DEFAULT_RANGES
    if args.ranges:
        ranges = parse_ranges(args.ranges)
    elif args.mfrom is not None and args.to is not None:
        ranges = [(args.mfrom, args.to)]
    else:
        ranges = DEFAULT_RANGES

    total_mesas = sum(b - a + 1 for a, b in ranges)
    range_str = ",".join(f"{a}-{b}" for a, b in ranges)
    print(f"[async] ts={ts}  ranges={range_str}  total={total_mesas:,}  concurrency={args.concurrency}")
    print(f"[async] dir: {mesas_dir}")

    connector = aiohttp.TCPConnector(limit=args.concurrency * 2)
    headers = {"User-Agent": USER_AGENT, "Cache-Control": "no-cache"}
    t0 = time.time()

    # Flush manifest cada batch
    done_global = 0
    async with aiohttp.ClientSession(connector=connector, headers=headers) as session:
        batch_size = 1000
        for rmin, rmax in ranges:
            for start in range(rmin, rmax + 1, batch_size):
                end = min(start + batch_size - 1, rmax)
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
                done_global += end - start + 1
                rate = done_global / elapsed if elapsed else 0
                eta_min = (total_mesas - done_global) / rate / 60 if rate else 0
                print(f"  [{end:>6}/{rmax}] ok={stats['ok']} skip={stats['skipped']} "
                      f"empty={stats['empty']} err={stats['errors']} 429={stats['throttled']}  "
                      f"{rate:.1f}req/s  ETA={eta_min:.0f}min")
                if stats["throttled"] > 50:
                    print("  [async] muchos 429 — pausa 30s")
                    await asyncio.sleep(30)
                    stats["throttled"] = 0

    summary = {
        "ts": ts,
        "ranges": [[a, b] for a, b in ranges],
        "total_mesas": total_mesas,
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
    ap.add_argument("--from", dest="mfrom", type=int, default=None)
    ap.add_argument("--to", type=int, default=None)
    ap.add_argument("--ranges", default=None,
                    help="e.g. '1-88064,900001-904703'. Overrides --from/--to.")
    ap.add_argument("--concurrency", type=int, default=50)
    ap.add_argument("--eleccion", type=int, default=10)
    args = ap.parse_args()
    asyncio.run(run(args))
    return 0


if __name__ == "__main__":
    sys.exit(main())
