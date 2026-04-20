"""
scripts/test_universe_complete.py — Barrido de bordes ONPE.

Detecta rangos nuevos que ONPE pueda haber agregado fuera del universo conocido.

Universo confirmado 2026-04-20:
  - Normales:  000001-088064 (gap conocido en 087704)
  - Especiales: 900001-904703

Estrategia:
  Probar bordes (n, n+1) para cada rango candidato. Si n existe y n+1 no, el
  rango termina ahí. Si n+1 existe, ampliar y reportar.

Uso:
    py scripts/test_universe_complete.py
    py scripts/test_universe_complete.py --json reports/universe_check.json
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
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
USER_AGENT = "AuditoriaEG2026/1.0 (universe-check)"
TIMEOUT = 20

# Bordes a verificar: (label, codigos_a_probar)
PROBES: list[tuple[str, list[int]]] = [
    ("normales_inicio", [1, 2]),
    ("normales_fin", [88063, 88064, 88065, 88066, 88100]),
    ("gap_087704", [87703, 87704, 87705]),
    ("especiales_inicio", [899999, 900000, 900001, 900002]),
    ("especiales_fin", [904702, 904703, 904704, 904710, 904800, 905000]),
    ("rango_910k_no_esperado", [910000, 920000]),
    ("rango_800k_no_esperado", [800000, 850000]),
]


async def probe(session: aiohttp.ClientSession, codigo: int, eleccion: int) -> dict:
    cod = f"{codigo:06d}"
    url = f"{PROXY_BASE}{ENDPOINT}?codigoMesa={cod}&idEleccion={eleccion}"
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=TIMEOUT)) as r:
            content = await r.read()
            return {
                "codigo": cod,
                "status": r.status,
                "bytes": len(content),
                "exists": r.status == 200 and len(content) > 100,
            }
    except Exception as e:
        return {"codigo": cod, "status": -1, "bytes": 0, "exists": False, "error": str(e)[:80]}


async def run(args):
    headers = {"User-Agent": USER_AGENT, "Cache-Control": "no-cache"}
    results: dict[str, list[dict]] = {}

    async with aiohttp.ClientSession(headers=headers) as session:
        for label, codes in PROBES:
            print(f"\n[{label}]")
            tasks = [probe(session, c, args.eleccion) for c in codes]
            res = await asyncio.gather(*tasks)
            results[label] = res
            for r in res:
                mark = "OK " if r["exists"] else "-- "
                print(f"  {mark} {r['codigo']}  http={r['status']:>3}  bytes={r['bytes']:>6}")

    # Resumen anómalo
    anomalies: list[str] = []
    found = {p["codigo"]: p["exists"] for arr in results.values() for p in arr}

    if found.get("088065") or found.get("088066") or found.get("088100"):
        anomalies.append("Posible nuevo rango normales >88064")
    if found.get("904704") or found.get("904710") or found.get("904800") or found.get("905000"):
        anomalies.append("Posible extensión especiales >904703")
    if found.get("899999") or found.get("900000"):
        anomalies.append("Mesa nueva antes de 900001")
    if found.get("087704"):
        anomalies.append("Gap 087704 ya no existe (mesa apareció)")
    if found.get("910000") or found.get("920000") or found.get("800000") or found.get("850000"):
        anomalies.append("Rango completamente nuevo detectado")

    out = {
        "ts_utc": datetime.now(timezone.utc).isoformat(),
        "eleccion": args.eleccion,
        "probes": results,
        "anomalies": anomalies,
        "status": "OK" if not anomalies else "ANOMALY",
    }

    print()
    print(f"[universe] status={out['status']}")
    if anomalies:
        for a in anomalies:
            print(f"  !! {a}")
    else:
        print("  universo conocido intacto: 1-88064 + 900001-904703 (gap 087704)")

    if args.json:
        Path(args.json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json).write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"  -> {args.json}")

    return 0 if out["status"] == "OK" else 2


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--eleccion", type=int, default=10)
    ap.add_argument("--json", default=None, help="ruta JSON de salida")
    args = ap.parse_args()
    return asyncio.run(run(args))


if __name__ == "__main__":
    sys.exit(main())
