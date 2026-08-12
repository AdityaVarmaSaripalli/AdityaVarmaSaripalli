"""
fetch_contributions.py — Scrape real contribution data from GitHub public HTML.
No token required.
Run: python scripts/fetch_contributions.py
Output: data/contributions.json
"""

import json
import os
import re
from datetime import date, timedelta

import requests
from bs4 import BeautifulSoup

USERNAME = "AdityaVarmaSaripalli"
URL = f"https://github.com/users/{USERNAME}/contributions"
OUTPUT = "data/contributions.json"


def fetch() -> dict:
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; profile-readme-bot/1.0)",
        "Accept": "text/html",
    }
    r = requests.get(URL, headers=headers, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    # Level-to-approx-count mapping (GitHub doesn't expose exact counts publicly)
    LEVEL_COUNT = {0: 0, 1: 2, 2: 6, 3: 14, 4: 25, 5: 40}

    days: list[dict] = []
    for el in soup.find_all(attrs={"data-date": True}):
        d = el.get("data-date")
        level = int(el.get("data-level", 0))
        # Try to get exact count from aria-label first
        count_label = el.get("aria-label", "")
        m = re.search(r"(\d+) contribution", count_label)
        count = int(m.group(1)) if m else LEVEL_COUNT.get(level, 0)
        if d:
            days.append({"date": d, "level": level, "count": count})

    days.sort(key=lambda x: x["date"])

    # Stats
    total = sum(d["count"] for d in days)
    best_day = max(days, key=lambda d: d["count"], default={"date": "", "count": 0})

    # Streaks
    current_streak = 0
    longest_streak = 0
    run = 0
    today_str = str(date.today())
    for d in reversed(days):
        if d["count"] > 0:
            run += 1
            if d["date"] <= today_str:
                if current_streak == run - 1:
                    current_streak = run
        else:
            if run > longest_streak:
                longest_streak = run
            run = 0
    if run > longest_streak:
        longest_streak = run

    result = {
        "username": USERNAME,
        "fetched": str(date.today()),
        "total_contributions": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "days": days,
    }

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(
        f"Saved {OUTPUT}  "
        f"({len(days)} days, {total} contributions, "
        f"streak {current_streak})"
    )
    return result


if __name__ == "__main__":
    fetch()
