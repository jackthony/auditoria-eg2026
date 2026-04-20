"""Generate viral OG images (1200x630) — Peru election dossier style.

Aesthetic: cream newspaper + blood red stamp + massive serif headline.
Matches the 'Algo no cuadra' landing brand. No logo bar noise — the
HEADLINE is the hero. Neuracode signs at the bottom.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "web"
LOGO = WEB / "logo-neuracode.png"

PAPER = (250, 247, 242)
INK = (17, 17, 17)
MUTED = (90, 90, 90)
BLOOD = (176, 23, 31)
RULE = (212, 204, 189)

W, H = 1200, 630

F_SERIF_BLACK = "C:/Windows/Fonts/georgiab.ttf"
F_SERIF = "C:/Windows/Fonts/georgia.ttf"
F_SERIF_ITALIC = "C:/Windows/Fonts/georgiai.ttf"
F_SANS = "C:/Windows/Fonts/arial.ttf"
F_SANS_BOLD = "C:/Windows/Fonts/arialbd.ttf"
F_IMPACT = "C:/Windows/Fonts/impact.ttf"


def f(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def paper_texture(img: Image.Image) -> None:
    """Subtle noise for newsprint feel."""
    import random
    random.seed(42)
    px = img.load()
    for y in range(0, H, 3):
        for x in range(0, W, 3):
            if random.random() < 0.04:
                r, g, b = px[x, y]
                d = random.randint(-8, 2)
                px[x, y] = (max(0, r + d), max(0, g + d), max(0, b + d))


def red_stamp(text: str, size: int = 58, angle: float = -8.0) -> Image.Image:
    font = f(F_IMPACT, size)
    tmp = Image.new("RGBA", (1400, 200), (0, 0, 0, 0))
    td = ImageDraw.Draw(tmp)
    bbox = td.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad_x, pad_y = 28, 14
    box_w, box_h = tw + pad_x * 2, th + pad_y * 2
    stamp = Image.new("RGBA", (box_w + 80, box_h + 80), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stamp)
    # double border
    sd.rectangle([40, 40, 40 + box_w, 40 + box_h], outline=BLOOD + (230,), width=5)
    sd.rectangle([48, 48, 32 + box_w, 32 + box_h], outline=BLOOD + (230,), width=2)
    sd.text((40 + pad_x - bbox[0], 40 + pad_y - bbox[1]), text, font=font, fill=BLOOD + (235,))
    return stamp.rotate(angle, resample=Image.BICUBIC, expand=True)


def draw_strike(d: ImageDraw.ImageDraw, xy: tuple[int, int, int, int], width: int = 10) -> None:
    x1, y1, x2, y2 = xy
    d.line([(x1, y1), (x2, y2)], fill=BLOOD, width=width)


def base_paper() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    paper_texture(img)
    # left red rule
    d.rectangle([0, 0, 10, H], fill=BLOOD)
    # top hairline
    d.line([(40, 60), (W - 40, 60)], fill=RULE, width=1)
    d.line([(40, 64), (W - 40, 64)], fill=RULE, width=1)
    # kicker bar (dateline)
    d.text((40, 28), "AUDITORÍA ELECCIONES GENERALES 2026  ·  PERÚ  ·  NEURACODE",
           font=f(F_SANS_BOLD, 15), fill=INK)
    d.text((W - 230, 28), "EVIDENCIA PÚBLICA · SHA-256",
           font=f(F_SANS_BOLD, 15), fill=BLOOD)
    return img, d


def bottom_sign(d: ImageDraw.ImageDraw, img: Image.Image, tagline: str) -> None:
    # bottom rule
    d.line([(40, H - 92), (W - 40, H - 92)], fill=RULE, width=1)
    d.line([(40, H - 88), (W - 40, H - 88)], fill=RULE, width=1)
    # logo
    if LOGO.exists():
        logo = Image.open(LOGO).convert("RGBA")
        ratio = 44 / logo.height
        logo = logo.resize((int(logo.width * ratio), 44), Image.LANCZOS)
        img.paste(logo, (40, H - 68), logo)
        x_after = 40 + logo.width + 14
    else:
        x_after = 40
    d.text((x_after, H - 60), "neuracode", font=f(F_SERIF_BLACK, 22), fill=INK)
    d.text((x_after, H - 34), tagline, font=f(F_SANS, 14), fill=MUTED)
    d.text((W - 320, H - 54), "auditoria.neuracode.dev",
           font=f(F_SERIF_BLACK, 22), fill=BLOOD)
    d.text((W - 320, H - 28), "datos públicos · código abierto",
           font=f(F_SANS, 13), fill=MUTED)


def render(path: Path, kicker: str, headline1: str, headline2: str,
           stamp_text: str, sub: str, tagline: str,
           stamp_pos: tuple[int, int] = (720, 180),
           stamp_angle: float = -7.0) -> None:
    img, d = base_paper()
    # handwritten-style kicker (italic serif, red)
    d.text((40, 90), kicker, font=f(F_SERIF_ITALIC, 26), fill=BLOOD)
    # massive headline (auto-fit each line to max width 740px)
    max_w = 740
    def fit_size(text: str, start: int = 120, min_size: int = 70) -> int:
        size = start
        while size > min_size:
            font = f(F_SERIF_BLACK, size)
            bbox = d.textbbox((0, 0), text, font=font)
            if bbox[2] - bbox[0] <= max_w:
                return size
            size -= 4
        return min_size
    s1 = fit_size(headline1)
    s2 = fit_size(headline2)
    d.text((40, 140), headline1, font=f(F_SERIF_BLACK, s1), fill=INK)
    d.text((40, 270), headline2, font=f(F_SERIF_BLACK, s2), fill=INK)
    # strikethrough on second line part
    # subheadline (italic serif)
    d.text((40, 410), sub, font=f(F_SERIF_ITALIC, 26), fill=INK)
    # red stamp diagonal
    stamp = red_stamp(stamp_text, size=62, angle=stamp_angle)
    img.paste(stamp, stamp_pos, stamp)
    bottom_sign(d, img, tagline)
    img.save(path, "PNG", optimize=True)
    print(f"wrote {path}")


def main() -> None:
    render(
        WEB / "og-image.png",
        kicker="— peritaje ciudadano del escrutinio ONPE",
        headline1="ALGO NO",
        headline2="CUADRA.",
        stamp_text="4,703 MESAS",
        sub="Mesa por mesa, el 2° puesto cambia. Cualquiera puede volver a contar.",
        tagline="peritaje ciudadano · EG2026",
        stamp_pos=(780, 170),
        stamp_angle=-9.0,
    )
    render(
        WEB / "og-historia.png",
        kicker="— cómo lo descubrimos, paso a paso",
        headline1="LA HISTORIA",
        headline2="COMPLETA.",
        stamp_text="4,703 MESAS",
        sub="Mesa por mesa, el 2° puesto cambia. Reconstruimos el camino.",
        tagline="peritaje público · EG2026",
        stamp_pos=(760, 170),
        stamp_angle=-7.0,
    )
    render(
        WEB / "og-chat.png",
        kicker="— tía María pregunta, yo contesto",
        headline1="SE LO EXPLIQUÉ",
        headline2="A MI TÍA.",
        stamp_text="SIN JERGA",
        sub="Un chat para que cualquiera entienda qué pasó con las elecciones.",
        tagline="explicado para todos · EG2026",
        stamp_pos=(860, 170),
        stamp_angle=-6.0,
    )
    render(
        WEB / "og-dashboard.png",
        kicker="— monitor técnico en vivo",
        headline1="MESA POR",
        headline2="MESA.",
        stamp_text="SHA-256",
        sub="Verificación independiente del escrutinio ONPE. Hashes reproducibles.",
        tagline="dashboard técnico · EG2026",
        stamp_pos=(840, 190),
        stamp_angle=-8.0,
    )


if __name__ == "__main__":
    main()
