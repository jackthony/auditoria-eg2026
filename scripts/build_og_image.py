"""Genera web/og-image.png (1200x630) para previews sociales (Twitter/FB/WhatsApp).

Lee web/data.json y dibuja: margen Sánchez−RLA, % escrutado, timestamp UTC.
Se ejecuta dentro del loop de captura tras `build_dashboard_json.py`.

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
NAVY = (11, 42, 74)
ACCENT = (200, 162, 75)
RED = (180, 51, 43)
GREEN = (46, 107, 63)
WHITE = (255, 255, 255)
BG_SOFT = (244, 241, 234)
MUTED = (92, 103, 112)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
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


def main() -> None:
    d = json.loads(DATA.read_text(encoding="utf-8"))
    s = d["state"]
    margen = int(s["margen_sanch_rla"])
    pct = float(s["pct"])
    ts_h = s["ts_human"]
    actas_jee = int(s["actas_jee"])

    img = Image.new("RGB", (W, H), WHITE)
    dr = ImageDraw.Draw(img)

    # Banda navy superior + borde oro.
    dr.rectangle([0, 0, W, 110], fill=NAVY)
    dr.rectangle([0, 110, W, 116], fill=ACCENT)
    dr.text((40, 28), "Auditoría Técnica · EG2026 Perú", font=font(34, True), fill=WHITE)
    dr.text((40, 72), "Monitor estadístico reproducible · jackthony.github.io/auditoria-eg2026",
            font=font(18), fill=(200, 210, 220))

    # Margen — el dato estrella.
    color = GREEN if margen >= 0 else RED
    sign = "+" if margen >= 0 else ""
    dr.text((40, 160), "MARGEN SÁNCHEZ − LÓPEZ ALIAGA", font=font(22, True), fill=MUTED)
    dr.text((40, 195), f"{sign}{fmt_int(margen)}", font=font(150, True), fill=color)
    dr.text((40, 365), "votos", font=font(28), fill=MUTED)

    # Bloque derecho: % escrutado + actas JEE.
    box_x = 720
    dr.rectangle([box_x, 160, W - 40, 410], fill=BG_SOFT, outline=ACCENT, width=2)
    dr.text((box_x + 30, 185), "ESCRUTINIO OFICIAL", font=font(20, True), fill=MUTED)
    dr.text((box_x + 30, 215), f"{pct:.2f}%", font=font(82, True), fill=NAVY)
    dr.text((box_x + 30, 320), "ACTAS IMPUGNADAS (JEE)", font=font(18, True), fill=MUTED)
    dr.text((box_x + 30, 348), fmt_int(actas_jee), font=font(44, True), fill=RED)

    # Footer info.
    dr.rectangle([0, H - 80, W, H], fill=NAVY)
    dr.text((40, H - 60), f"Corte: {ts_h}", font=font(20), fill=WHITE)
    dr.text((40, H - 32), "Data + hashes SHA-256 reproducibles · Memorial al Fiscal de la Nación",
            font=font(16), fill=(200, 210, 220))
    dr.text((W - 280, H - 46), "@JackDeNeuracode", font=font(22, True), fill=ACCENT)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, "PNG", optimize=True)
    print(f"OK: {OUT} ({OUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
