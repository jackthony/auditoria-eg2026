"""Genera web/og-image.png (1200x630) + per-finding PNGs — estilo flagship Neuracode.

Paleta: paper #faf7f2, ink navy #0c1a2e, blood #e63946.

Uso:
    py scripts/build_og_image.py                    # landing: "Algo no cuadra"
    py scripts/build_og_image.py --finding h4      # OG para /h4/
    py scripts/build_og_image.py --finding h9      # OG para /h9/
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FINDINGS = ROOT / "reports" / "hallazgos_20260420" / "findings_consolidado_0420.json"
OUT = ROOT / "web" / "og-image.png"

W, H = 1200, 630
PAPER = (250, 247, 242)
INK_NAVY = (12, 26, 46)
BLOOD = (230, 57, 70)
MUTED = (90, 90, 90)
RULE = (212, 204, 189)


def font(size: int, bold: bool = False, serif: bool = False) -> ImageFont.FreeTypeFont:
    """Load font fallback: Georgia → Segoe UI → Arial."""
    if serif:
        candidates = [
            "C:/Windows/Fonts/georgiab.ttf" if bold else "C:/Windows/Fonts/georgia.ttf",
            "C:/Windows/Fonts/timesnewromanbd.ttf" if bold else "C:/Windows/Fonts/timesnewroman.ttf",
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


def render_landing() -> Image.Image:
    """Landing: 'Algo no cuadra' + 4,703 mesas."""
    img = Image.new("RGB", (W, H), PAPER)
    dr = ImageDraw.Draw(img)

    # Kicker
    dr.text((60, 60), "AUDITORÍA EG2026 · ANÁLISIS FORENSE", font=font(22, True), fill=BLOOD)
    dr.rectangle([60, 100, 380, 103], fill=INK_NAVY)

    # Hero
    dr.text((60, 140), "Algo no", font=font(120, True, serif=True), fill=INK_NAVY)
    dr.text((60, 260), "cuadra", font=font(120, True, serif=True), fill=BLOOD)

    # Sub
    dr.text((60, 380), "4,703 mesas 900k+ con anomalías estadísticas.",
            font=font(40, True), fill=INK_NAVY)
    dr.text((60, 445), "Datos públicos ONPE. Cadena custodia SHA-256 + IPFS.",
            font=font(26), fill=MUTED)

    # Footer
    dr.rectangle([60, 505, W - 60, 508], fill=RULE)
    dr.text((60, 520), "Explicaciones ONPE requeridas.",
            font=font(18), fill=MUTED)
    dr.text((60, H - 42), "auditoria.neuracode.dev · Neuracode · MIT",
            font=font(17, True), fill=INK_NAVY)
    return img


def render_h4() -> Image.Image:
    """H4: JPP 41.65% en mesas 900k+ vs 10.91% normal. z=698."""
    img = Image.new("RGB", (W, H), PAPER)
    dr = ImageDraw.Draw(img)

    # Kicker
    dr.text((60, 60), "HALLAZGO H4 · ANOMALÍA ESTADÍSTICA", font=font(20, True), fill=BLOOD)
    dr.rectangle([60, 100, 380, 103], fill=INK_NAVY)

    # Big number (41.65%)
    dr.text((60, 130), "41.65%", font=font(200, True, serif=True), fill=BLOOD)
    # Label
    dr.text((60, 350), "JPP en 4,703 mesas 900k+", font=font(48, True), fill=INK_NAVY)
    dr.text((60, 420), "vs 10.91% en mesas normales. Ratio 3.82×. z=698.",
            font=font(26), fill=MUTED)

    # Footer
    dr.rectangle([60, 505, W - 60, 508], fill=RULE)
    dr.text((60, 520), "Método: z-test 2-prop Newcombe 1998 + Cohen h (0.73).",
            font=font(16), fill=MUTED)
    dr.text((60, H - 42), "auditoria.neuracode.dev · Neuracode · MIT",
            font=font(17, True), fill=INK_NAVY)
    return img


def render_h9() -> Image.Image:
    """H9: BERBÉS 11/11 mesas impugnadas. p=4.83e-14."""
    img = Image.new("RGB", (W, H), PAPER)
    dr = ImageDraw.Draw(img)

    # Kicker
    dr.text((60, 60), "HALLAZGO H9 · ANOMALÍA PROCESAL", font=font(20, True), fill=BLOOD)
    dr.rectangle([60, 100, 380, 103], fill=INK_NAVY)

    # Big number (11/11)
    dr.text((80, 140), "11", font=font(180, True, serif=True), fill=BLOOD)
    dr.text((280, 210), "de 11", font=font(64, True, serif=True), fill=INK_NAVY)
    # Label
    dr.text((60, 360), "mesas impugnadas",
            font=font(48, True, serif=True), fill=INK_NAVY)
    dr.text((60, 430), "Local BERBÉS (Extranjero). 1 entre 20 billones.",
            font=font(26), fill=MUTED)

    # Footer
    dr.rectangle([60, 505, W - 60, 508], fill=RULE)
    dr.text((60, 520), "Binomial exacto p=4.83e-14 vs tasa global 6.16%.",
            font=font(16), fill=MUTED)
    dr.text((60, H - 42), "auditoria.neuracode.dev · Neuracode · MIT",
            font=font(17, True), fill=INK_NAVY)
    return img


def main() -> None:
    parser = argparse.ArgumentParser(description="Genera OG images para auditoria.neuracode.dev")
    parser.add_argument("--finding", choices=["h4", "h9"], help="Genera OG para finding específico")
    args = parser.parse_args()

    if args.finding == "h4":
        img = render_h4()
        out = ROOT / "web" / "h4" / "og.png"
    elif args.finding == "h9":
        img = render_h9()
        out = ROOT / "web" / "h9" / "og.png"
    else:
        # Landing
        img = render_landing()
        out = OUT

    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "PNG", optimize=True)
    size_kb = out.stat().st_size / 1024
    print(f"OK: {out} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
