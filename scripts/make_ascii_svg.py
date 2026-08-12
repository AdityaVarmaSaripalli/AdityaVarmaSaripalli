"""
make_ascii_svg.py — Convert source-prepped.png to a self-typing monochrome ASCII SVG.
Run: python scripts/make_ascii_svg.py
Output: aditya-ascii.svg
"""

import os
import sys
from PIL import Image

INPUT = "source-prepped.png"
OUTPUT = "aditya-ascii.svg"

COLS = 95
ROWS = 50
CHAR_W = 7.2
CHAR_H = 13.5
FONT_SIZE = 12
FILL_COLOR = "#c9d1d9"
BG_COLOR = "#0d1117"

# Bright (sparse) → dark (dense)
RAMP = " .`':-=+*cs#%@"


def brightness_to_char(b: int) -> str:
    # Bright pixels → sparse (leading space), dark pixels → dense (@)
    idx = int((1 - b / 255) * (len(RAMP) - 1))
    return RAMP[idx]


def image_to_grid(path: str, cols: int, rows: int) -> list[list[str]]:
    img = Image.open(path).convert("L")
    img = img.resize((cols, rows), Image.LANCZOS)
    grid = []
    for y in range(rows):
        row = []
        for x in range(cols):
            row.append(brightness_to_char(img.getpixel((x, y))))
        grid.append(row)
    return grid


def escape(ch: str) -> str:
    return ch.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def make_svg(grid: list[list[str]]) -> str:
    rows = len(grid)
    cols = len(grid[0]) if grid else 0
    svg_w = cols * CHAR_W
    svg_h = rows * CHAR_H + 10

    # Stagger per row: each row wipes left-to-right in ~0.3 s, staggered 0.05 s apart
    row_dur = 0.28
    stagger = 0.045
    total = rows * stagger + row_dur + 0.3

    lines = []
    lines.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{svg_w:.1f}" height="{svg_h:.1f}" '
        f'viewBox="0 0 {svg_w:.1f} {svg_h:.1f}">'
    )
    lines.append(
        f'<rect width="100%" height="100%" fill="{BG_COLOR}"/>'
    )
    lines.append("<style>")
    lines.append(f"  text {{ font-family: 'Courier New', Courier, monospace; font-size: {FONT_SIZE}px; fill: {FILL_COLOR}; white-space: pre; }}")
    lines.append("</style>")
    lines.append("<defs>")

    for r in range(rows):
        begin = r * stagger
        lines.append(
            f'  <clipPath id="cr{r}">'
            f'<rect x="0" y="{r * CHAR_H:.1f}" width="0" height="{CHAR_H:.1f}">'
            f'<animate attributeName="width" from="0" to="{svg_w:.1f}" '
            f'dur="{row_dur}s" begin="{begin:.3f}s" fill="freeze"/>'
            f'</rect></clipPath>'
        )

    lines.append("</defs>")

    for r, row in enumerate(grid):
        text = "".join(escape(ch) for ch in row)
        y = (r + 1) * CHAR_H
        lines.append(
            f'<text x="0" y="{y:.1f}" clip-path="url(#cr{r})">{text}</text>'
        )

    lines.append("</svg>")
    return "\n".join(lines)


if __name__ == "__main__":
    if not os.path.exists(INPUT):
        print(f"Error: {INPUT} not found. Run prep_photo.py first.")
        sys.exit(1)

    print(f"Reading {INPUT} ...")
    grid = image_to_grid(INPUT, COLS, ROWS)
    svg = make_svg(grid)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Saved {OUTPUT}  ({COLS}×{ROWS} chars)")
