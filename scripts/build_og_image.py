"""Genera web/og-image.png (1200x630) — estilo flagship Neuracode.

Paleta: paper #faf7f2, ink #111, blood #b0171f.
Hook: "4.703 MESAS NO APARECEN · 2° PUESTO CAMBIA" cuando hay findings_gap,
fallback a margen Sánchez−RLA.

Uso:
    py scripts/build_og_image.py
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "web" / "data.json"
OUT = ROOT / "web" / "og-image.png"

W, H = 1200, 630
PAPER = (250, 247, 242)
INK = (17, 17, 17)
BLOOD = (176, 23, 31)
MUTED = (61, 61, 61)
RULE = (212, 204, 189)


def font(size: int, bold: bool = False, serif: bool = False) -> ImageFont.FreeTypeFont:
    if serif:
        candidates = [
            "C:/Windows/Fonts/georgiab.ttf" if bold else "C:/Windows/Fonts/georgia.ttf",
        ]
    else:
        candidates = [
            "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
            "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        ]
    for p in candidates:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def fmt_int(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def render_gap(fp: dict, s: dict) -> Image.Image:
    F1 = next(f for f in fp["findings"] if f["id"] == "GAP-F1-RANKING")
    F2 = next(f for f in fp["findings"] if f["id"] == "GAP-F2-MESAS-FALTANTES")
    mesas_falt = int(F2["delta_universo"])
    oficial2 = F1["top10_oficial"][1][0]
    mesa2 = F1["top10_mesa_a_mesa"][1][0]

    img = Image.new("RGB", (W, H), PAPER)
    dr = ImageDraw.Draw(img)

    # Kicker (blood)
    dr.text((60, 60), "AUDITORÍA EG2026 · APORTE CIUDADANO", font=font(22, True), fill=BLOOD)
    # Rule
    dr.rectangle([60, 100, 300, 103], fill=INK)

    # Hook: número gigante serif
    dr.text((60, 130), fmt_int(mesas_falt), font=font(220, True, serif=True), fill=BLOOD)
    dr.text((60, 380), "mesas no aparecen.", font=font(52, True, serif=True), fill=INK)
    dr.text((60, 445), "El 2° puesto cambia al sumar mesa por mesa.",
            font=font(28), fill=MUTED)

    # Mini comparación
    dr.rectangle([60, 505, W - 60, 508], fill=RULE)
    dr.text((60, 520), f"Oficial dice 2°: {oficial2[:28]}", font=font(18), fill=MUTED)
    dr.text((60, 548), f"Sumando mesas da 2°: {mesa2[:28]}", font=font(18, True), fill=BLOOD)

    # Firma
    dr.text((60, H - 42), "Jack de Neuracode · neuracode.dev", font=font(17, True), fill=INK)
    dr.text((W - 360, H - 42), "datos públicos · SHA-256 · MIT",
            font=font(17), fill=MUTED)
    return img


def render_margen(s: dict) -> Image.Image:
    margen = int(s["margen_sanch_rla"])
    pct = float(s["pct"])
    ts_h = s["ts_human"]
    sign = "+" if margen >= 0 else ""

    img = Image.new("RGB", (W, H), PAPER)
    dr = ImageDraw.Draw(img)

    dr.text((60, 60), "AUDITORÍA EG2026 · APORTE CIUDADANO", font=font(22, True), fill=BLOOD)
    dr.rectangle([60, 100, 300, 103], fill=INK)

    dr.text((60, 130), "Margen 2° vs 3°", font=font(32), fill=MUTED)
    dr.text((60, 175), f"{sign}{fmt_int(margen)}", font=font(180, True, serif=True), fill=INK)
    dr.text((60, 390), "votos deciden la segunda vuelta.",
            font=font(36, True, serif=True), fill=BLOOD)

    dr.rectangle([60, 475, W - 60, 478], fill=RULE)
    dr.text((60, 490), f"Escrutinio oficial: {pct:.2f}%  ·  Corte: {ts_h}",
            font=font(20), fill=MUTED)

    dr.text((60, H - 42), "Jack de Neuracode · neuracode.dev", font=font(17, True), fill=INK)
    dr.text((W - 360, H - 42), "datos públicos · SHA-256 · MIT",
            font=font(17), fill=MUTED)
    return img


def main() -> None:
    d = json.loads(DATA.read_text(encoding="utf-8"))
    s = d["state"]
    fp = d.get("findings_gap")
    img = render_gap(fp, s) if fp else render_margen(s)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, "PNG", optimize=True)
    print(f"OK: {OUT} ({OUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
