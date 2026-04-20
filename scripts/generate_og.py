"""Generate viral OG images (1200x630) for each audit page.

Brand: Neuracode. Style: dark paper with red accent on hero number.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "web"
LOGO = WEB / "logo-neuracode.png"

BG = (15, 15, 20)
INK = (245, 245, 245)
MUTED = (170, 170, 180)
RED = (220, 38, 38)
ACCENT = (168, 85, 247)

W, H = 1200, 630

F_BOLD = "C:/Windows/Fonts/arialbd.ttf"
F_REG = "C:/Windows/Fonts/arial.ttf"
F_BLACK = "C:/Windows/Fonts/ariblk.ttf"


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def draw_base(kicker: str) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    # top red bar
    d.rectangle([0, 0, W, 6], fill=RED)
    # logo
    if LOGO.exists():
        logo = Image.open(LOGO).convert("RGBA")
        ratio = 56 / logo.height
        logo = logo.resize((int(logo.width * ratio), 56), Image.LANCZOS)
        img.paste(logo, (60, 50), logo)
    # kicker
    d.text((60 + 66 + 16, 68), "NEURACODE", font=font(F_BLACK, 24), fill=INK)
    d.text((60 + 66 + 16, 98), kicker, font=font(F_REG, 18), fill=MUTED)
    return img, d


def render(path: Path, kicker: str, hero: str, hero_label: str, title: str,
           subtitle: str, footer: str) -> None:
    img, d = draw_base(kicker)
    # hero number
    d.text((60, 180), hero, font=font(F_BLACK, 200), fill=RED)
    d.text((60, 390), hero_label, font=font(F_BOLD, 28), fill=INK)
    # title
    d.text((60, 450), title, font=font(F_BOLD, 38), fill=INK)
    # subtitle
    d.text((60, 500), subtitle, font=font(F_REG, 22), fill=MUTED)
    # footer
    d.rectangle([0, H - 56, W, H], fill=(25, 25, 32))
    d.text((60, H - 44), footer, font=font(F_BOLD, 20), fill=INK)
    d.text((W - 340, H - 44), "auditoria.neuracode.dev", font=font(F_BOLD, 20), fill=ACCENT)
    img.save(path, "PNG", optimize=True)
    print(f"wrote {path}")


def main() -> None:
    render(
        WEB / "og-image.png",
        kicker="Auditoría Elecciones Generales 2026",
        hero="4,703",
        hero_label="MESAS DE VOTACIÓN FALTANTES EN LA API ONPE",
        title="Algo no cuadra.",
        subtitle="566,233 votos sin cuadrar · margen de 13,624 define 2° puesto",
        footer="Datos públicos · Código abierto · SHA-256 verificable",
    )
    render(
        WEB / "og-historia.png",
        kicker="El peritaje público — EG2026",
        hero="4,703",
        hero_label="MESAS QUE NO APARECEN EN EL ESCRUTINIO OFICIAL",
        title="La historia completa.",
        subtitle="Cómo descubrimos que el 2° puesto cambia al sumar mesa por mesa",
        footer="Lee el peritaje público paso a paso",
    )
    render(
        WEB / "og-chat.png",
        kicker="Tía María pregunta — EG2026",
        hero="4,703",
        hero_label="MESAS QUE LE EXPLIQUÉ A MI TÍA",
        title="Se lo expliqué a mi tía.",
        subtitle="Un chat sin jerga. Lee tú lo que pasó con las elecciones.",
        footer="Explicado para que cualquiera entienda",
    )
    render(
        WEB / "og-dashboard.png",
        kicker="Monitor técnico EG2026",
        hero="4,703",
        hero_label="MESAS FALTANTES · MONITOR MESA-A-MESA",
        title="Dashboard en vivo.",
        subtitle="Verificación independiente del escrutinio ONPE · hashes SHA-256",
        footer="Explora los datos mesa por mesa",
    )


if __name__ == "__main__":
    main()
