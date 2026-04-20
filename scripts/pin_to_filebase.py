"""Pinea archivos clave a IPFS via Filebase S3 API (IPFS-01).

Filebase free tier:
- 5 GB storage, sin limite bandwidth
- Gateway publico: <bucket>.myfilebase.com/ipfs/<cid>
- S3-compatible: endpoint https://s3.filebase.com, region us-east-1
- CID retornado en metadata x-amz-meta-cid del PUT object

Fix SSL Windows: fuerza AWS_CA_BUNDLE via certifi (evita "unable to get local issuer").

Uso:
    .venv/Scripts/python scripts/pin_to_filebase.py

Lee FILEBASE_ACCESS_KEY + FILEBASE_SECRET_KEY + FILEBASE_BUCKET de .env.
Guarda CIDs en reports/ipfs_cids.json (merge con pins Pinata previos).
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

import certifi
from dotenv import load_dotenv

# Fix SSL Windows: debe estar ANTES de importar boto3.
os.environ.setdefault("AWS_CA_BUNDLE", certifi.where())

import boto3  # noqa: E402
from botocore.config import Config  # noqa: E402
from botocore.exceptions import ClientError  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

REPO = Path(__file__).resolve().parents[1]
CIDS_OUT = REPO / "reports" / "ipfs_cids.json"
FILEBASE_ENDPOINT = "https://s3.filebase.com"
FILEBASE_REGION = "us-east-1"

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


def make_client(access_key: str, secret_key: str) -> Any:
    return boto3.client(
        "s3",
        endpoint_url=FILEBASE_ENDPOINT,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=FILEBASE_REGION,
        config=Config(signature_version="s3v4", retries={"max_attempts": 3}),
    )


def upload_and_get_cid(s3: Any, bucket: str, local: Path, key: str) -> str:
    """Sube archivo a Filebase y devuelve el CID IPFS."""
    s3.upload_file(str(local), bucket, key)
    # Filebase guarda el CID en metadata del objeto.
    head = s3.head_object(Bucket=bucket, Key=key)
    meta = head.get("Metadata", {}) or {}
    cid = meta.get("cid") or meta.get("Cid") or meta.get("CID")
    if not cid:
        # Algunos backends devuelven el CID como x-amz-meta-cid en ResponseMetadata.
        raw = head.get("ResponseMetadata", {}).get("HTTPHeaders", {})
        cid = raw.get("x-amz-meta-cid")
    if not cid:
        raise RuntimeError(f"sin CID en metadata de {key}: meta={meta} head={head}")
    return cid


def main() -> int:
    load_dotenv(REPO / ".env")
    access = os.environ.get("FILEBASE_ACCESS_KEY", "").strip()
    secret = os.environ.get("FILEBASE_SECRET_KEY", "").strip()
    bucket = os.environ.get("FILEBASE_BUCKET", "").strip()
    if not access or not secret or not bucket:
        logger.error("FILEBASE_ACCESS_KEY / SECRET / BUCKET faltantes en .env. Aborto.")
        return 2

    s3 = make_client(access, secret)

    # Sanity check: bucket accesible.
    try:
        s3.head_bucket(Bucket=bucket)
    except ClientError as e:
        logger.error("bucket %s no accesible: %s", bucket, e)
        return 3

    # Gateway publico Filebase (sin config extra). Responde 200 para cualquier CID pineado.
    public_gateway = "ipfs.filebase.io"
    # Gateway dedicado opcional (requiere crear via dashboard -> Gateways).
    dedicated_gateway = f"{bucket}.myfilebase.com"
    results: list[dict[str, Any]] = []
    errors = 0

    for rel, desc in TARGETS:
        path = REPO / rel
        if not path.exists():
            logger.warning("skip (no existe): %s", rel)
            errors += 1
            continue

        size_mb = path.stat().st_size / (1024 * 1024)
        key = rel.replace("\\", "/")
        logger.info("subiendo %s (%.2f MB) -> s3://%s/%s", rel, size_mb, bucket, key)

        sha_local = sha256_file(path)

        try:
            cid = upload_and_get_cid(s3, bucket, path, key)
        except (ClientError, RuntimeError) as e:
            logger.error("error subiendo %s: %s", rel, e)
            errors += 1
            continue

        results.append({
            "file": rel,
            "description": desc,
            "size_bytes": path.stat().st_size,
            "sha256_local": sha_local,
            "ipfs_cid": cid,
            "filebase_bucket": bucket,
            "filebase_s3_key": key,
            "primary_url": f"https://{public_gateway}/ipfs/{cid}",
            "dedicated_url_pending": f"https://{dedicated_gateway}/ipfs/{cid}",
            "ipfs_io_url": f"https://ipfs.io/ipfs/{cid}",
            "dweb_url": f"https://dweb.link/ipfs/{cid}",
        })
        logger.info("OK -> CID=%s", cid)

    # Merge con pins Pinata previos (backup proof).
    prior_pinata: list[dict[str, Any]] = []
    if CIDS_OUT.exists():
        try:
            prev = json.loads(CIDS_OUT.read_text(encoding="utf-8"))
            prior_pinata = prev.get("pinata_pins") or prev.get("pins") or []
        except (json.JSONDecodeError, KeyError):
            logger.warning("no se pudo leer %s previo; se sobrescribe", CIDS_OUT)

    payload = {
        "meta": {
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "universo_ts": "20260420T074202Z",
            "total_mesas": 92766,
            "primary_provider": "filebase",
            "backup_provider": "pinata",
            "filebase_pinned_count": len(results),
            "errors": errors,
        },
        "filebase_pins": results,
        "pinata_pins": prior_pinata,
    }

    CIDS_OUT.parent.mkdir(parents=True, exist_ok=True)
    CIDS_OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("guardado %s (%d filebase pins, %d pinata backup)",
                CIDS_OUT, len(results), len(prior_pinata))

    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
