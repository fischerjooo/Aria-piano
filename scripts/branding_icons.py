"""Generate crisp, low-detail Aria Piano and Aria Piano (beta) icons.

The geometric A is the visual first letter of the homepage wordmark.
No hairlines or miniature piano-key stripes: it remains legible at 32 px.
"""
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
ICONS = ROOT / "icons"
BACKGROUND = "#14352f"
BETA_BACKGROUND = "#193b4a"
LETTER = "#f9f4de"
BETA_DOT = "#75c9df"


def quadratic(p0, p1, p2, steps=12):
    return [
        (
            (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
            (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1],
        )
        for t in (i / steps for i in range(steps + 1))
    ]


def icon(beta=False, maskable=False, size=512):
    upscale = 3 if size >= 192 else 6
    factor = size * upscale / 512
    bg = BETA_BACKGROUND if beta else BACKGROUND
    im = Image.new("RGB", (size * upscale, size * upscale), bg)
    d = ImageDraw.Draw(im)

    def p(xy):
        x, y = xy
        shrink = 0.82 if maskable else 1
        return ((256 + (x - 256) * shrink) * factor,
                (256 + (y - 256) * shrink) * factor)

    # One heavy, subtly rounded A silhouette with a large open counter and bar.
    outline = [(100, 402), (223, 118)]
    outline += quadratic((223, 118), (242, 65), (256, 83), 10)
    outline += quadratic((256, 83), (272, 84), (289, 118), 10)
    outline += [(413, 402), (340, 402), (317, 346), (195, 346), (172, 402)]
    d.polygon([p(xy) for xy in outline], fill=LETTER)
    d.polygon([p(xy) for xy in [(219, 286), (256, 193), (294, 286)]], fill=bg)
    if beta:
        x, y = p((397, 395))
        radius = 35 * factor * (0.82 if maskable else 1)
        d.ellipse((x - radius, y - radius, x + radius, y + radius), fill=BETA_DOT)

    return im.resize((size, size), Image.Resampling.LANCZOS)


def make_icons():
    ICONS.mkdir(parents=True, exist_ok=True)
    for label, beta in (("aria", False), ("aria-beta", True)):
        for size in (192, 512):
            icon(beta, size=size).save(ICONS / f"{label}-{size}.png", optimize=True)
        icon(beta, maskable=True).save(ICONS / f"{label}-maskable-512.png", optimize=True)
    print("Generated legible 192/512/maskable Aria piano and beta icons")


if __name__ == "__main__":
    make_icons()
