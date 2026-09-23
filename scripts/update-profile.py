#!/usr/bin/env python3
"""Render profile cards from unauthenticated GitHub public data.

Run from any directory with Python 3. No token or third-party package is needed.
Only assets/github-*.svg are generated; static artwork is maintained separately.
"""

import json
import re
from datetime import date, datetime, timezone
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen


USER = "Oniums"
ASSETS = Path(__file__).resolve().parents[1] / "assets"
COLORS = ["#192b3b", "#174c50", "#237c73", "#37b5a0", "#6ae6c9"]


def fetch(url):
    request = Request(url, headers={"User-Agent": "Oniums-profile"})
    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


class Calendar(HTMLParser):
    def __init__(self):
        super().__init__()
        self.days = {}

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "td" and "data-date" in attrs and "data-level" in attrs:
            day = date.fromisoformat(attrs["data-date"])
            level = int(attrs["data-level"])
            if level not in range(5):
                raise ValueError("Unexpected contribution level")
            self.days[day] = level


def text(x, y, value, size=18, color="#ccd8e6", weight=400):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" '
            f'font-weight="{weight}">{escape(str(value))}</text>')


def svg(width, height, title, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
            f'height="{height}" viewBox="0 0 {width} {height}" role="img" '
            f'aria-label="{escape(title)}"><title>{escape(title)}</title>'
            f'<rect width="{width}" height="{height}" rx="16" fill="#0d1827"/>'
            '<g font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Arial, sans-serif">'
            f'{body}</g></svg>\n')


def overview(profile, stars, contributions, updated, compact=False):
    items = [(profile["public_repos"], "PUBLIC REPOS"),
             (stars, "STARS"), (profile["followers"], "FOLLOWERS"),
             (contributions, "CONTRIBUTIONS / YEAR")]
    body = text(28, 37, "GITHUB OVERVIEW", 15, "#8da9bc", 600)
    for index, (value, label) in enumerate(items):
        x = 28 + (index % 2) * 262 if compact else 28 + index * 266
        y = 101 + (index // 2) * 102 if compact else 104
        body += text(x, y, f"{value:,}", 42, "#6ae6c9", 600)
        body += text(x, y + 29, label, 12, "#8da9bc")
    height = 285 if compact else 190
    body += text(28, height - 23, f"Public GitHub data / {updated} UTC", 12, "#8da9bc")
    return svg(562 if compact else 1080, height, "GitHub public profile statistics", body)


def activity(days, updated, compact=False):
    ordered = sorted(days)
    if compact:
        # Keep complete calendar columns at the start of the recent window.
        first = ordered[-1].toordinal() - 12 * 7 - (ordered[-1].weekday() + 1) % 7
        ordered = [day for day in ordered if day.toordinal() >= first]
    first = ordered[0].toordinal() - (ordered[0].weekday() + 1) % 7
    columns = (ordered[-1].toordinal() - first) // 7 + 1
    width, step, cell = (562, 37, 28) if compact else (1080, 19, 14)
    height = 390 if compact else 250
    body = text(28, 37, "RECENT ACTIVITY" if compact else "CONTRIBUTION ACTIVITY", 15, "#8da9bc", 600)
    x0 = (width - columns * step) // 2
    last_month = None
    for day in ordered:
        col = (day.toordinal() - first) // 7
        row = (day.weekday() + 1) % 7
        x, y = x0 + col * step, 79 + row * step
        if day.day <= 7 and row == 0 and day.month != last_month:
            body += text(x, 65, day.strftime("%b"), 12, "#8da9bc")
            last_month = day.month
        body += (f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" '
                 f'rx="3" fill="{COLORS[days[day]]}"><title>{day}: '
                 f'GitHub contribution level {days[day]}</title></rect>')
    body += text(28, height - 23, f'{ordered[0]} — {ordered[-1]}', 12, "#8da9bc")
    for index, color in enumerate(COLORS):
        body += f'<rect x="{width - 125 + index * 19}" y="{height - 35}" width="14" height="14" rx="3" fill="{color}"/>'
    return svg(width, height, f"GitHub public contribution calendar, updated {updated}", body)


def main():
    profile = json.loads(fetch(f"https://api.github.com/users/{USER}"))
    repos = []
    page = 1
    while True:
        batch = json.loads(fetch(f"https://api.github.com/users/{USER}/repos?type=owner&per_page=100&page={page}"))
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    html = fetch(f"https://github.com/users/{USER}/contributions")
    calendar = Calendar()
    calendar.feed(html)
    heading = re.search(r'<h2\b[^>]*id="js-contribution-activity-description"[^>]*>\s*([\d,]+)\s+contributions', html)
    # An upstream markup change must fail without replacing good cards with zeroes.
    if not heading or len(calendar.days) < 350:
        raise ValueError("Incomplete public contribution calendar; existing assets preserved")
    stars = sum(repo["stargazers_count"] for repo in repos if not repo["fork"])
    contributions = int(heading[1].replace(",", ""))
    updated = datetime.now(timezone.utc).date().isoformat()
    outputs = {}
    for compact in (False, True):
        suffix = "-compact" if compact else ""
        outputs[f"github-overview{suffix}.svg"] = overview(profile, stars, contributions, updated, compact)
        outputs[f"github-activity{suffix}.svg"] = activity(calendar.days, updated, compact)
    ASSETS.mkdir(exist_ok=True)
    for name, content in outputs.items():
        (ASSETS / name).write_text(content, encoding="utf-8")
    print(f"Updated {len(outputs)} cards: {len(repos)} public repos, {stars} stars, "
          f'{profile["followers"]} followers, {contributions} contributions ({updated} UTC)')


if __name__ == "__main__":
    main()
