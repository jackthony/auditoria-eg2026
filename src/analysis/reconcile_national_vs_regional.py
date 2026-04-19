"""
Reconciliación nacional vs regional.

Verifica que totales nacionales coincidan con suma de regiones
(totalActas, contabilizadas, enviadasJee, pendientes).
Usa formato viejo de snapshot (snap*.json).
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime
from pathlib import Path

from src.models.findings import Finding, ReconcileResult

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

logger = logging.getLogger(__name__)

THRESHOLD_PCT = 0.1
THRESHOLD_ABS = 50


def _find_capture_ts(capture_dir: Path) -> str:
    """Extrae timestamp ISO desde MANIFEST.jsonl o captura_dir name."""
    manifest = capture_dir / "MANIFEST.jsonl"
    if manifest.exists():
        try:
            for line in manifest.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                entry = json.loads(line)
                ts = entry.get("fetched_at_utc")
                if ts:
                    return ts
        except Exception as e:
            logger.warning(f"Error leyendo MANIFEST: {e}")

    ts_str = capture_dir.name
    try:
        dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        return dt.isoformat()
    except ValueError:
        return datetime.now().isoformat()


def _load_snapshot(raw_dir: Path) -> dict | None:
    """Carga primer snap*.json encontrado."""
    snap_files = sorted(raw_dir.glob("snap*.json"))
    if not snap_files:
        logger.warning(f"No snap*.json en {raw_dir}")
        return None

    snap_file = snap_files[0]
    logger.info(f"Cargando {snap_file.name}")
    try:
        return json.loads(snap_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error cargando {snap_file}: {e}")
        return None


def _get_snapshot_sha256(raw_dir: Path) -> str | None:
    """SHA-256 del snap*.json principal desde MANIFEST.jsonl."""
    manifest = raw_dir.parent / "MANIFEST.jsonl"
    if not manifest.exists():
        logger.warning("No MANIFEST.jsonl, calculando SHA-256 manual")
        snap_files = sorted(raw_dir.glob("snap*.json"))
        if not snap_files:
            return None
        try:
            content = snap_files[0].read_bytes()
            from hashlib import sha256
            return sha256(content).hexdigest()
        except IOError as e:
            logger.error(f"Error hasheando: {e}")
            return None

    try:
        for line in manifest.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            entry = json.loads(line)
            if "snap" in entry.get("local_path", ""):
                return entry.get("sha256")
    except Exception as e:
        logger.error(f"Error leyendo MANIFEST: {e}")
    return None


def _sum_regions(regions: list[dict], metric: str) -> int:
    """Suma métrica sobre todas las regiones."""
    total = 0
    for region in regions:
        val = region.get(metric) or 0
        total += int(val)
    return total


def _compare_metrics(snapshot: dict) -> dict:
    """Compara nacional vs Σ(regional) para cada métrica."""
    nat = snapshot.get("national", {})
    regions = snapshot.get("regions", [])

    metrics_check = ["totalActas", "contabilizadas", "enviadasJee", "pendientes"]
    results = {}
    critical = False

    for metric in metrics_check:
        nat_val = nat.get(metric)
        if nat_val is None:
            continue

        nat_val = int(nat_val)
        reg_sum = _sum_regions(regions, metric)
        diff = nat_val - reg_sum
        pct = 100 * diff / nat_val if nat_val > 0 else 0

        alert = abs(pct) > THRESHOLD_PCT and abs(diff) > THRESHOLD_ABS
        if alert:
            critical = True

        results[metric] = {
            "national": nat_val,
            "regional_sum": reg_sum,
            "diff": diff,
            "diff_pct": round(pct, 3),
            "alert": alert,
        }

        logger.info(
            f"  {metric:<20} nat={nat_val:>8,} reg={reg_sum:>8,} "
            f"diff={diff:+,} ({pct:+.3f}%) {'⚠' if alert else '✓'}"
        )

    return {
        "severity": "CRÍTICO" if critical else "INFO",
        "metrics": results,
    }


def run(root: Path | None = None) -> ReconcileResult:
    """
    Ejecuta reconciliación nacional vs regional.

    Retorna ReconcileResult con findings Pydantic validados.
    """
    if root is None:
        root = Path(__file__).resolve().parents[2]

    reports_dir = root / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    try:
        meta_file = root / "data" / "processed" / "meta.json"
        if meta_file.exists():
            meta_data = json.loads(meta_file.read_text(encoding="utf-8"))
            capture_dir = root / meta_data.get("capture_dir", "captures/latest")
        else:
            capture_dir = root / "captures" / "latest"
    except Exception as e:
        logger.warning(f"Error detectando captura: {e}")
        capture_dir = root / "captures" / "latest"

    raw_dir = capture_dir / "raw"
    snapshot = _load_snapshot(raw_dir)

    capture_ts = _find_capture_ts(capture_dir)
    sha256_val = _get_snapshot_sha256(raw_dir) or "unknown"

    if snapshot is None:
        finding = Finding(
            id="RECNR0",
            severity="INFO",
            test="Reconciliación Nacional-Regional",
            h0="Totales nacionales = suma regional",
            interpretation="No se encontraron datos de snapshot.",
            limitations="Formato snap*.json no disponible.",
            captura_sha256=sha256_val,
            captura_ts=capture_ts,
        )
        result = ReconcileResult(
            findings=[finding],
            capture_ts=capture_ts,
            status="OK",
        )
        output_file = reports_dir / "reconcile_national_regional.json"
        output_file.write_text(
            json.dumps(
                {
                    "findings": [f.model_dump(mode="json") for f in result.findings],
                    "capture_ts": result.capture_ts,
                    "status": result.status,
                },
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        logger.info(f"Guardado: {output_file}")
        return result

    comparison = _compare_metrics(snapshot)
    severity = comparison["severity"]
    metrics = comparison["metrics"]

    if severity == "CRÍTICO":
        interpretation = (
            f"Diferencias > {THRESHOLD_PCT}% o {THRESHOLD_ABS} actas: "
            + ", ".join(m for m, v in metrics.items() if v.get("alert"))
        )
    else:
        interpretation = (
            f"Totales nacionales coinciden con suma regional "
            f"(tolerancia: {THRESHOLD_PCT}% o {THRESHOLD_ABS} actas)."
        )

    finding = Finding(
        id="RECNR1",
        severity=severity,
        test="Reconciliación Nacional-Regional",
        h0="national.totalActas == sum(regions.totalActas); etc.",
        interpretation=interpretation,
        limitations=(
            "Solo compara campo-a-campo. No valida votos por candidato. "
            "Umbrales: 0.1% o 50 actas."
        ),
        captura_sha256=sha256_val,
        captura_ts=capture_ts,
        statistic=None,
        p_value=None,
    )

    result = ReconcileResult(
        findings=[finding],
        capture_ts=capture_ts,
        status="OK" if severity == "INFO" else "WARN",
    )

    output_file = reports_dir / "reconcile_national_regional.json"
    output_data = {
        "findings": [f.model_dump(mode="json") for f in result.findings],
        "capture_ts": result.capture_ts,
        "status": result.status,
        "metrics": metrics,
    }
    output_file.write_text(
        json.dumps(output_data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    logger.info(f"Guardado: {output_file}")

    return result


def main() -> None:
    """CLI entry point."""
    import argparse

    logging.basicConfig(
        level=logging.INFO,
        format="[%(name)s] %(message)s",
    )

    parser = argparse.ArgumentParser(
        description="Reconciliación nacional vs regional"
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Raíz proyecto. Default: deduce automáticamente.",
    )

    args = parser.parse_args()

    print("═" * 70)
    print(" RECONCILIACIÓN NACIONAL vs REGIONAL")
    print("═" * 70)

    result = run(root=args.root)

    print()
    finding = result.findings[0]
    print(f"Finding: {finding.id}")
    print(f"Severity: {finding.severity}")
    print(f"Interpretation: {finding.interpretation}")
    print()


if __name__ == "__main__":
    main()
