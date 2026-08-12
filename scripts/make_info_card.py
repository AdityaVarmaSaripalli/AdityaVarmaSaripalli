"""
make_info_card.py — Render a neofetch-style info card SVG.
Run: python scripts/make_info_card.py
Output: info-card.svg

Set STATIC=1 to emit a frozen (no animation) frame for local preview.
"""

import os

OUTPUT = "info-card.svg"
STATIC = os.environ.get("STATIC", "0") == "1"

BG = "#0d1117"
GREEN = "#39d353"
CYAN = "#58a6ff"
YELLOW = "#e3b341"
GRAY = "#8b949e"
WHITE = "#c9d1d9"
PURPLE = "#bc8cff"

FONT = "'Courier New', Courier, monospace"
W = 490
LINE_H = 22
PAD_X = 18
PAD_TOP = 18

LINES = [
    # (label_color, label, value_color, value)
    (GREEN,  "aditya@github",  WHITE,   ":~$ neofetch"),
    (None,   "",               GRAY,    "─" * 38),
    (CYAN,   "Name",           WHITE,   "Aditya Sai Varma"),
    (CYAN,   "Role",           WHITE,   "Software Engineer"),
    (CYAN,   "Host",           YELLOW,  "American Airlines"),
    (CYAN,   "OS",             WHITE,   "Enterprise · Cloud · AI"),
    (None,   "",               GRAY,    "─" * 38),
    (CYAN,   "Stack",          WHITE,   "Java · Python · Spring · AWS"),
    (CYAN,   "Arch",           WHITE,   "Microservices · Kafka · REST"),
    (CYAN,   "Tools",          WHITE,   "Git · Docker · CI/CD · Linux"),
    (None,   "",               GRAY,    "─" * 38),
    (CYAN,   "LinkedIn",       PURPLE,  "in/aditya-sai-saripalli"),
    (CYAN,   "GitHub",         PURPLE,  "AdityaVarmaSaripalli"),
]

SVG_H = PAD_TOP * 2 + len(LINES) * LINE_H + 10


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def make_svg() -> str:
    stagger = 0.07  # seconds between lines
    fade_dur = 0.30

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{W}" height="{SVG_H}" '
        f'viewBox="0 0 {W} {SVG_H}">'
    )
    parts.append(f'<rect width="100%" height="100%" fill="{BG}" rx="6"/>')
    parts.append(
        f'<style>text{{font-family:{FONT};font-size:13px;}} '
        f'.lbl{{font-weight:bold;}}</style>'
    )

    for i, (lc, label, vc, value) in enumerate(LINES):
        y = PAD_TOP + i * LINE_H + LINE_H
        begin = f"{i * stagger:.2f}s"

        if STATIC:
            opacity_attr = 'opacity="1"'
            anim = ""
        else:
            opacity_attr = 'opacity="0"'
            anim = (
                f'<animate attributeName="opacity" '
                f'from="0" to="1" dur="{fade_dur}s" '
                f'begin="{begin}" fill="freeze"/>'
            )

        if label:
            colon = ": " if value else ""
            x_val = PAD_X + len(label) * 7.8 + 14
            parts.append(
                f'<text {opacity_attr} x="{PAD_X}" y="{y}" fill="{lc}" class="lbl">'
                f'{esc(label)}{esc(colon)}{anim}</text>'
            )
            parts.append(
                f'<text {opacity_attr} x="{x_val:.1f}" y="{y}" fill="{vc}">'
                f'{esc(value)}{anim}</text>'
            )
        else:
            parts.append(
                f'<text {opacity_attr} x="{PAD_X}" y="{y}" fill="{vc}">'
                f'{esc(value)}{anim}</text>'
            )

    parts.append("</svg>")
    return "\n".join(parts)


if __name__ == "__main__":
    svg = make_svg()
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Saved {OUTPUT}  ({'static' if STATIC else 'animated'})")
