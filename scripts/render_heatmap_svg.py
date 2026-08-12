"""
render_heatmap_svg.py — Render the contribution heatmap as an animated SVG.
Run: python scripts/render_heatmap_svg.py
Reads: data/contributions.json
Output: contrib-heatmap.svg
"""

import json
import math
import os
import sys
from datetime import date, timedelta

INPUT = "data/contributions.json"
OUTPUT = "contrib-heatmap.svg"

BG = "#0d1117"
BORDER = "#21262d"
LABEL_COLOR = "#8b949e"
LEGEND_COLOR = "#8b949e"
TEXT_COLOR = "#c9d1d9"
GREEN_COLOR = "#39d353"

PALETTE = [
    "#161b22",  # 0 — no contributions
    "#0e4429",  # 1
    "#006d32",  # 2
    "#26a641",  # 3
    "#39d353",  # 4
    "#69f0a0",  # 5 — brightest
]

BOX = 11
GAP = 3
STEP = BOX + GAP
WEEKS = 53
DAYS = 7

PAD_LEFT = 30    # space for day labels
PAD_TOP = 28     # space for month labels
PAD_RIGHT = 14
PAD_BOTTOM = 42  # space for legend + stats

GRID_W = WEEKS * STEP - GAP
GRID_H = DAYS * STEP - GAP
SVG_W = PAD_LEFT + GRID_W + PAD_RIGHT
SVG_H = PAD_TOP + GRID_H + PAD_BOTTOM

DAY_LABELS = ["", "Mon", "", "Wed", "", "Fri", ""]
MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def load_data(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_grid(days: list[dict]) -> list[list[dict]]:
    """Build a 53×7 grid aligned to ISO weeks (Mon first)."""
    by_date = {d["date"]: d for d in days}
    if not days:
        return [[{"date": "", "level": 0, "count": 0}] * 7 for _ in range(WEEKS)]

    # Find the Sunday that starts week 0 of our window
    last_day = date.fromisoformat(days[-1]["date"])
    # Align to last Sunday
    last_sunday = last_day + timedelta(days=(6 - last_day.weekday() + 1) % 7)
    start = last_sunday - timedelta(weeks=WEEKS - 1)

    grid = []
    for w in range(WEEKS):
        week = []
        for d in range(DAYS):
            day_date = start + timedelta(weeks=w, days=d)
            ds = str(day_date)
            cell = by_date.get(ds, {"date": ds, "level": 0, "count": 0})
            week.append(cell)
        grid.append(week)
    return grid


def month_labels(grid: list[list[dict]]) -> list[tuple[int, str]]:
    labels = []
    seen = set()
    for w, week in enumerate(grid):
        for cell in week:
            if not cell["date"]:
                continue
            d = date.fromisoformat(cell["date"])
            key = (d.year, d.month)
            if key not in seen:
                seen.add(key)
                labels.append((w, MONTH_NAMES[d.month - 1]))
            break
    return labels


def diagonal_delay(w: int, d: int) -> float:
    """Diagonal reveal: boxes along the same anti-diagonal appear together."""
    diag = w + d
    return diag * 0.012


def render(data: dict) -> str:
    grid = build_grid(data.get("days", []))
    total = data.get("total_contributions", 0)
    streak = data.get("current_streak", 0)
    longest = data.get("longest_streak", 0)
    best = data.get("best_day", {})
    fetched = data.get("fetched", str(date.today()))

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{SVG_W}" height="{SVG_H}" '
        f'viewBox="0 0 {SVG_W} {SVG_H}">'
    )
    parts.append(f'<rect width="100%" height="100%" fill="{BG}" rx="6"/>')

    # CSS keyframe for the reveal animation
    parts.append("<style>")
    parts.append("  @keyframes pop {")
    parts.append("    from { opacity: 0; transform: scale(0.4); }")
    parts.append("    to   { opacity: 1; transform: scale(1); }")
    parts.append("  }")
    parts.append("  .box { transform-box: fill-box; transform-origin: center; }")
    parts.append("</style>")

    # Month labels
    for w, name in month_labels(grid):
        x = PAD_LEFT + w * STEP
        parts.append(
            f'<text x="{x}" y="{PAD_TOP - 6}" '
            f'font-family="\'Courier New\', monospace" '
            f'font-size="10" fill="{LABEL_COLOR}">{name}</text>'
        )

    # Day labels (Mon / Wed / Fri)
    for d, label in enumerate(DAY_LABELS):
        if not label:
            continue
        y = PAD_TOP + d * STEP + BOX - 1
        parts.append(
            f'<text x="{PAD_LEFT - 4}" y="{y}" '
            f'font-family="\'Courier New\', monospace" '
            f'font-size="9" fill="{LABEL_COLOR}" text-anchor="end">{label}</text>'
        )

    # Boxes
    for w, week in enumerate(grid):
        for d, cell in enumerate(week):
            level = min(cell["level"], 5)
            color = PALETTE[level]
            x = PAD_LEFT + w * STEP
            y = PAD_TOP + d * STEP
            delay = diagonal_delay(w, d)
            cnt = cell.get("count", 0)
            title = f'{cell["date"]}: {cnt} contribution{"s" if cnt != 1 else ""}'
            parts.append(
                f'<rect class="box" x="{x}" y="{y}" width="{BOX}" height="{BOX}" '
                f'rx="2" fill="{color}" '
                f'style="animation: pop 0.25s ease-out {delay:.3f}s both;">'
                f'<title>{title}</title>'
                f'</rect>'
            )

    # Legend
    legend_y = PAD_TOP + GRID_H + 14
    parts.append(
        f'<text x="{PAD_LEFT}" y="{legend_y + BOX - 1}" '
        f'font-family="\'Courier New\', monospace" '
        f'font-size="10" fill="{LEGEND_COLOR}">Less</text>'
    )
    lx = PAD_LEFT + 32
    for i, color in enumerate(PALETTE):
        parts.append(
            f'<rect x="{lx + i * (BOX + 2)}" y="{legend_y}" '
            f'width="{BOX}" height="{BOX}" rx="2" fill="{color}"/>'
        )
    more_x = lx + len(PALETTE) * (BOX + 2) + 2
    parts.append(
        f'<text x="{more_x}" y="{legend_y + BOX - 1}" '
        f'font-family="\'Courier New\', monospace" '
        f'font-size="10" fill="{LEGEND_COLOR}">More</text>'
    )

    # Stats footer
    stats_y = legend_y + BOX + 14
    stats = (
        f"{total:,} contributions · "
        f"streak {streak} · "
        f"longest {longest} · "
        f"refreshed {fetched}"
    )
    parts.append(
        f'<text x="{SVG_W // 2}" y="{stats_y}" '
        f'font-family="\'Courier New\', monospace" '
        f'font-size="10" fill="{LEGEND_COLOR}" text-anchor="middle">{stats}</text>'
    )

    parts.append("</svg>")
    return "\n".join(parts)


if __name__ == "__main__":
    if not os.path.exists(INPUT):
        print(f"Error: {INPUT} not found. Run fetch_contributions.py first.")
        sys.exit(1)
    data = load_data(INPUT)
    svg = render(data)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Saved {OUTPUT}")
