"""Valida si gap oficial 92.766 vs walker 88.063 se explica por copias de acta.

Multiprocessing. Solo idEleccion=10 (presi).
"""
from __future__ import annotations
import gzip, json, sys
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

TS = sys.argv[1] if len(sys.argv) > 1 else "20260419T035056Z"
MESAS_DIR = Path("captures") / TS / "mesas"


def process(path_str: str) -> dict:
    with gzip.open(path_str, "rb") as fh:
        d = json.loads(fh.read().decode("utf-8"))
    data = d.get("data") or []
    presi = [x for x in data if x.get("idEleccion") == 10]
    if not presi:
        return {"has_presi": 0}
    out = {"has_presi": 1, "actas": len(presi), "codigo": presi[0]["codigoMesa"]}
    out["copias"] = [a.get("numeroCopia") for a in presi]
    out["estados"] = [a.get("estadoActa") for a in presi]
    out["ambitos"] = [a.get("idAmbitoGeografico") for a in presi]
    return out


def main() -> None:
    files = sorted(str(p) for p in MESAS_DIR.glob("*.json.gz"))
    print(f"files: {len(files)}", flush=True)

    mesas_presi = 0
    actas_presi_total = 0
    copias = Counter()
    estados = Counter()
    ambitos = Counter()
    mesas_extranjero = set()
    mesas_nacional = set()

    with Pool(processes=8) as pool:
        for i, r in enumerate(pool.imap_unordered(process, files, chunksize=200)):
            if i % 10000 == 0:
                print(f"  {i}/{len(files)}", flush=True)
            if not r.get("has_presi"):
                continue
            mesas_presi += 1
            actas_presi_total += r["actas"]
            for nc in r["copias"]:
                copias[nc] += 1
            for est in r["estados"]:
                estados[est] += 1
            for amb in r["ambitos"]:
                ambitos[amb] += 1
            if 2 in r["ambitos"]:
                mesas_extranjero.add(r["codigo"])
            else:
                mesas_nacional.add(r["codigo"])

    print("=" * 60, flush=True)
    print(f"mesas con presi:          {mesas_presi:,}", flush=True)
    print(f"actas presi total:        {actas_presi_total:,}", flush=True)
    print(f"distrib numeroCopia:      {dict(copias)}", flush=True)
    print(f"distrib estadoActa:       {dict(estados)}", flush=True)
    print(f"distrib idAmbito:         {dict(ambitos)}", flush=True)
    print(f"mesas extranjero unicas:  {len(mesas_extranjero):,}", flush=True)
    print(f"mesas nacional unicas:    {len(mesas_nacional):,}", flush=True)
    print("=" * 60, flush=True)
    oficial = 92766
    gap = oficial - actas_presi_total
    if gap < 500:
        print(f"VEREDICTO: F2 MAL. actas {actas_presi_total:,} ≈ oficial {oficial:,} (gap {gap}). Copias explican todo.", flush=True)
    elif actas_presi_total <= mesas_presi + 10:
        print(f"VEREDICTO: F2 RESISTE. actas {actas_presi_total:,} = mesas {mesas_presi:,}. Gap {oficial - mesas_presi:,} real.", flush=True)
    else:
        print(f"VEREDICTO: MIXTO. actas {actas_presi_total:,} vs mesas {mesas_presi:,} vs oficial {oficial:,}.", flush=True)


if __name__ == "__main__":
    main()
