"""PERITO-01 — Empaqueta un ZIP forense listo para Fiscalia/JEE.

Contenido:
  - captures/<ultimo_tsUTC>/**  (raw + MANIFEST.jsonl, cadena de custodia)
  - reports/findings.json + forecast.json + summary.txt
  - reports/figures/**
  - docs/MEMORIAL_TECNICO_FISCAL.md + otros memoriales
  - web/data.json (snapshot del dashboard)
  - MANIFEST_ZIP.json  (SHA-256 de CADA archivo del ZIP + meta)
  - README_PERITO.md   (indice legible con hashes y fuente)

Salida:
  reports/perito/perito_<tsUTC>.zip
  reports/perito/perito_<tsUTC>.sha256   (hash del ZIP final)

Uso:
  py scripts/build_perito_zip.py
"""
from __future__ import annotations

import hashlib
import json
import logging
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CAPTURES = ROOT / "captures"
REPORTS = ROOT / "reports"
DOCS = ROOT / "docs"
WEB = ROOT / "web"
OUT_DIR = REPORTS / "perito"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def latest_capture() -> Path:
    candidates = sorted(p for p in CAPTURES.iterdir()
                        if p.is_dir() and len(p.name) == 16 and p.name.endswith("Z"))
    if not candidates:
        raise FileNotFoundError("No hay capturas en captures/")
    return candidates[-1]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def iter_payload(capture_dir: Path) -> list[tuple[Path, str]]:
    """Devuelve pares (path_absoluto, arcname_en_zip)."""
    items: list[tuple[Path, str]] = []

    # Captura inmutable completa.
    for p in capture_dir.rglob("*"):
        if p.is_file():
            items.append((p, f"captures/{capture_dir.name}/{p.relative_to(capture_dir).as_posix()}"))

    # Reportes de analisis.
    for name in ("findings.json", "forecast.json", "summary.txt",
                 "impugnation_bias.json", "impugnation_velocity.json",
                 "last_digit.json", "spatial_cluster.json",
                 "reconcile_internal.json", "ausentismo_comparacion.json",
                 "impugnadas_por_region.csv"):
        p = REPORTS / name
        if p.exists():
            items.append((p, f"reports/{name}"))

    # Figuras.
    figs = REPORTS / "figures"
    if figs.exists():
        for p in figs.rglob("*"):
            if p.is_file():
                items.append((p, f"reports/figures/{p.relative_to(figs).as_posix()}"))

    # Informe Tecnico (ultima version disponible).
    for pat in ("Informe_Tecnico_RP_v*.pdf", "Informe_Tecnico_v*.docx"):
        for p in sorted(REPORTS.glob(pat)):
            items.append((p, f"reports/{p.name}"))

    # Memorial y documentos de apoyo.
    for name in ("MEMORIAL_TECNICO_FISCAL.md", "BRIEFING_FORENSE.md",
                 "FALLAS_TECNICAS_VERIFICADAS.md", "HIPOTESIS_CIENTIFICAS.md",
                 "PRE_REGISTRO_H1_H5.md"):
        p = DOCS / name
        if p.exists():
            items.append((p, f"docs/{name}"))

    # Snapshot publico del dashboard.
    dj = WEB / "data.json"
    if dj.exists():
        items.append((dj, "web/data.json"))

    return items


def build_readme(ts_utc: str, capture_name: str, files: list[dict]) -> str:
    critical = [f for f in files if f["arcname"].startswith("captures/")]
    lines = [
        "# Paquete Pericial — auditoria-eg2026",
        "",
        f"**Generado:** {ts_utc}",
        f"**Captura base:** `{capture_name}` (inmutable, cadena de custodia via SHA-256 + git).",
        "",
        "## Contenido",
        "",
        f"- `captures/{capture_name}/` — raw ONPE + MANIFEST.jsonl (hashes originales).",
        "- `reports/` — findings.json, forecast.json, figures, informe tecnico.",
        "- `docs/` — MEMORIAL_TECNICO_FISCAL.md y documentos de apoyo.",
        "- `web/data.json` — snapshot del dashboard publico.",
        "- `MANIFEST_ZIP.json` — SHA-256 de cada archivo incluido.",
        "",
        "## Verificacion",
        "",
        "```bash",
        "# Hash del ZIP completo (debe coincidir con el .sha256 adjunto):",
        f"sha256sum perito_{ts_utc}.zip",
        "",
        "# Verificar archivo individual tras descomprimir:",
        "python -c \"import hashlib,sys; print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())\" <archivo>",
        "```",
        "",
        f"## Archivos de captura (cadena de custodia — {len(critical)})",
        "",
    ]
    for f in critical[:20]:
        lines.append(f"- `{f['arcname']}` — `{f['sha256']}` ({f['size']:,} B)")
    if len(critical) > 20:
        lines.append(f"- ... (+{len(critical) - 20} archivos mas en MANIFEST_ZIP.json)")
    lines += [
        "",
        "## Autoria",
        "",
        "Jack Aguilar — Neuracode. Aporte ciudadano independiente, sin afiliacion politica.",
        "Codigo MIT, documentos CC-BY-4.0.",
        "Repositorio publico: https://github.com/jackthony/auditoria-eg2026",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    try:
        cap = latest_capture()
    except FileNotFoundError as e:
        logger.error("%s", e)
        return 1

    ts_utc = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = OUT_DIR / f"perito_{ts_utc}.zip"
    sha_path = OUT_DIR / f"perito_{ts_utc}.sha256"

    payload = iter_payload(cap)
    if not payload:
        logger.error("Payload vacio — revisar estado de reports/ y captures/")
        return 1

    manifest: list[dict] = []
    for src, arc in payload:
        manifest.append({
            "arcname": arc,
            "size": src.stat().st_size,
            "sha256": sha256_file(src),
        })

    readme = build_readme(ts_utc, cap.name, manifest)
    manifest_json = json.dumps({
        "generated_at_utc": ts_utc,
        "source_capture": cap.name,
        "repo": "https://github.com/jackthony/auditoria-eg2026",
        "files": manifest,
        "count": len(manifest),
    }, ensure_ascii=False, indent=2)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for src, arc in payload:
            zf.write(src, arcname=arc)
        zf.writestr("MANIFEST_ZIP.json", manifest_json)
        zf.writestr("README_PERITO.md", readme)

    zip_hash = sha256_file(zip_path)
    sha_path.write_text(f"{zip_hash}  perito_{ts_utc}.zip\n", encoding="utf-8")

    logger.info("ZIP listo: %s (%d archivos, %.1f KB)",
                zip_path, len(manifest), zip_path.stat().st_size / 1024)
    logger.info("SHA-256: %s", zip_hash)
    return 0


if __name__ == "__main__":
    sys.exit(main())
