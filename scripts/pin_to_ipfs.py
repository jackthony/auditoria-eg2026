"""Pinea archivos clave a IPFS via Pinata (IPFS-01).

Cadena de custodia:
1. captures/{ts}/ (local) + SHA-256
2. GitHub (commit firmado)
3. HuggingFace (parquet inmutable)
4. IPFS / Pinata (descentralizado) <- este script

Uso:
    .venv/Scripts/python scripts/pin_to_ipfs.py

Lee PINATA_JWT de .env. Pinea 4 archivos. Guarda CIDs en
reports/ipfs_cids.json con SHA-256 local para doble verificacion.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

REPO = Path(__file__).resolve().parents[1]
PINATA_ENDPOINT = "https://api.pinata.cloud/pinning/pinFileToIPFS"
CIDS_OUT = REPO / "reports" / "ipfs_cids.json"

# Archivos a pinear (path relativo repo, descripcion humana).
TARGETS: list[tuple[str, str]] = [
    (
        "captures/20260420T074202Z/MESAS_MANIFEST.jsonl",
        "Manifest SHA-256 de 92,766 mesas (cadena custodia v2)",
    ),
    (
        "reports/hf_dataset/onpe_eg2026_mesas_20260420T074202Z.parquet",
        "Parquet 3.79M actas (dataset HF Neuracode)",
    ),
    (
        "reports/hallazgos_20260420/findings_consolidado_0420.json",
        "Findings H1-H4 consolidados v2-92k",
    ),
    (
        "reports/h4_stats.json",
        "Stats H4 completo (z=698, Cohen h=0.73, bootstrap IC95)",
    ),
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def pin_file(path: Path, jwt: str, name: str) -> dict[str, Any]:
    headers = {"Authorization": f"Bearer {jwt}"}
    metadata = json.dumps({"name": name})
    options = json.dumps({"cidVersion": 1})
    with path.open("rb") as f:
        files = {"file": (path.name, f)}
        data = {"pinataMetadata": metadata, "pinataOptions": options}
        resp = requests.post(
            PINATA_ENDPOINT,
            headers=headers,
            files=files,
            data=data,
            timeout=300,
        )
    resp.raise_for_status()
    return resp.json()


def main() -> int:
    load_dotenv(REPO / ".env")
    jwt = os.environ.get("PINATA_JWT", "").strip()
    if not jwt:
        logger.error("PINATA_JWT vacio en .env. Aborto.")
        return 2

    results: list[dict[str, Any]] = []
    errors = 0

    for rel, desc in TARGETS:
        path = REPO / rel
        if not path.exists():
            logger.warning("skip (no existe): %s", rel)
            errors += 1
            continue

        size_mb = path.stat().st_size / (1024 * 1024)
        logger.info("pineando %s (%.2f MB)...", rel, size_mb)
        sha_local = sha256_file(path)

        try:
            api = pin_file(path, jwt, rel)
        except requests.HTTPError as e:
            body = e.response.text[:300] if e.response is not None else ""
            logger.error("HTTP error pineando %s: %s | body=%s", rel, e, body)
            errors += 1
            continue
        except requests.RequestException as e:
            logger.error("network error pineando %s: %s", rel, e)
            errors += 1
            continue

        cid = api.get("IpfsHash")
        results.append({
            "file": rel,
            "description": desc,
            "size_bytes": path.stat().st_size,
            "sha256_local": sha_local,
            "ipfs_cid": cid,
            "pinata_pinned_at": api.get("Timestamp"),
            "gateway_url": f"https://gateway.pinata.cloud/ipfs/{cid}",
            "public_ipfs_url": f"https://ipfs.io/ipfs/{cid}",
        })
        logger.info("OK -> CID=%s", cid)

    payload = {
        "meta": {
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "universo_ts": "20260420T074202Z",
            "total_mesas": 92766,
            "pinned_count": len(results),
            "errors": errors,
        },
        "pins": results,
    }

    CIDS_OUT.parent.mkdir(parents=True, exist_ok=True)
    CIDS_OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("guardado %s (%d pins, %d errores)", CIDS_OUT, len(results), errors)

    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
