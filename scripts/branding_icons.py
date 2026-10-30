"""Render one canonical Aria piano SVG into all stable and beta PWA icons."""
from pathlib import Path
import shutil
import cairosvg

ROOT = Path(__file__).resolve().parents[1]
ICONS = ROOT / "icons"
SVG = ICONS / "aria.svg"


def render():
    source = SVG.read_bytes()
    if b"<svg" not in source or b"aria" not in source.lower():
        raise ValueError("Missing canonical Aria piano SVG artwork")
    for size in (192, 512):
        path = ICONS / f"aria-{size}.png"
        cairosvg.svg2png(bytestring=source, write_to=str(path),
                         output_width=size, output_height=size)
    # Android maskable safe zone: same icon, with extra space around the artwork.
    mark = source.replace(
        b'<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512" role="img" aria-label="Aria piano A monogram">',
        b'', 1).rsplit(b"</svg>", 1)[0]
    maskable = (b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">'
                b'<rect width="512" height="512" fill="#073b32"/>'
                b'<svg x="52" y="52" width="408" height="408" viewBox="0 0 512 512">'
                + mark + b'</svg></svg>')
    cairosvg.svg2png(bytestring=maskable,
                     write_to=str(ICONS / "aria-maskable-512.png"),
                     output_width=512, output_height=512)
    for suffix in ("192.png", "512.png", "maskable-512.png"):
        shutil.copyfile(ICONS / f"aria-{suffix}", ICONS / f"aria-beta-{suffix}")
    print("Generated matching SVG-based Aria icons for stable and beta")


if __name__ == "__main__":
    render()
