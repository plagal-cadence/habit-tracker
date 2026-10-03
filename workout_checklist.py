#!/usr/bin/env python3
"""Generate the printable workout checklist.

Each page covers a two-week block, with AM / midday / PM checkboxes per day.

Usage:
    python workout_checklist.py                 # two weeks starting today
    python workout_checklist.py 2026-09-20      # two weeks starting Sep 20 2026
    python workout_checklist.py 9/20/2026       # same, US format (9/20 = this year)
    python workout_checklist.py 2026-09-20 -p 3 # six weeks, one page per two weeks
    python workout_checklist.py 2026-09-20 -o pt.html

Writes workout_checklist.html next to this script unless -o is given. The output
is a self-contained HTML page sized for 11in x 8.5in landscape.
"""

from __future__ import annotations

import argparse
import datetime as dt
import math
import re
from pathlib import Path

DEFAULT_OUTPUT = Path(__file__).with_name("workout_checklist.html")

HEADER_TITLE = "WORKOUT CHECKLIST"

DAYS_PER_PERIOD = 14

EXERCISES = [
    {"name": "Pulley — straight, lateral, behind back", "detail": "3 sets × 10 reps, hold 3 sec"},
    {"name": "Shoulder abduction with cane", "detail": "2 sets × 10 reps, hold 3 sec"},
    {
        "name": "Bilateral external rotation &amp; and back with band",
        "detail": "3 sets × 8 reps, hold 3 sec",
    },
    {"name": "Cross body — low L to hi R, low R to L shoulder", "detail": "3 sets × 10 reps"},
    {
        "name": "Bodyblade — front low, mid, hi, lateral low, mid, hi",
        "detail": "2 sets × 30 secs each position",
    },
    {"name": "Wax on wax off — forward, lateral", "detail": "3 sets × 10 reps"},
    {"name": "Curls", "detail": "3 sets × 15 reps, 15 lbs"},
    {"name": "Rows", "detail": "3 sets × 15 reps, 15 lbs"},
    {"name": "Abductions", "detail": "3 sets × 12 reps, 5 lbs"},
    {"name": "Presses", "detail": "3 sets × 15 reps, 15 lbs"},
    {"name": "On side ext rotations", "detail": "3 sets × 12 reps, 5 lbs"},
    {"name": "Plank", "detail": "3 sets × 15 secs"},
]

DAY_NAMES = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

TIMING = {
    "setup_sec_per_exercise": 15,
    "rest_between_sets_sec": 10,
    "movement_sec_per_rep": 1,
    "transition_sec_per_rep": 1,
    "bilateral_multiplier": 2,
}

CSS = """
    :root {
      --ink: #111;
      --line: #666;
      --light-line: #bbb;
      --bg: #fff;
    }

    @page {
      size: 11in 8.5in landscape;
      margin: 0.45in 0.5in 0.35in;
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: "Trebuchet MS", "Segoe UI", sans-serif;
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }

    .page {
      width: 100%;
      page-break-after: always;
    }

    .page:last-child {
      page-break-after: auto;
    }

    /* ── Page header ─────────────────────────────── */
    .page-header {
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      border-bottom: 2px solid var(--ink);
      padding-bottom: 2px;
      margin-bottom: 5px;
    }

    .page-header h1 {
      margin: 0;
      font-size: 17px;
      letter-spacing: 0.3px;
    }

    .page-header .subtitle {
      margin: 0;
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.7px;
      color: #444;
    }

    /* ── Main table ──────────────────────────────── */
    table {
      border-collapse: collapse;
      width: 100%;
      table-layout: fixed;
    }

    th,
    td {
      border: 1px solid var(--light-line);
      padding: 0;
      vertical-align: middle;
    }

    /* Exercise label column */
    .ex-col {
      width: 2.6in;
      text-align: left;
      padding: 2px 5px;
      font-size: 10px;
      font-weight: 600;
      background: #fafafa;
      vertical-align: middle;
      line-height: 1.25;
    }

    .ex-col .ex-detail {
      display: block;
      font-weight: 400;
      font-size: 8.5px;
      color: #555;
      margin-top: 0;
    }

    th.ex-col {
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.6px;
      background: #f0f0f0;
      padding: 4px 5px;
    }

    /* Day header cells */
    .day-hdr {
      text-align: center;
      font-size: 9.5px;
      font-weight: 700;
      line-height: 1.2;
      padding: 2px 1px;
      background: #f0f0f0;
      border-bottom: 1.5px solid var(--line);
      border-right: 1.5px solid var(--line);
    }

    .day-hdr .day-num {
      display: block;
      font-size: 13px;
      font-weight: 700;
      line-height: 1.1;
    }

    .day-hdr .session-key {
      font-size: 7px;
      color: #999;
    }

    .day-hdr .month-tag {
      display: block;
      font-size: 7px;
      font-weight: 700;
      letter-spacing: 0.4px;
      color: #777;
    }

    /* Checkbox cells */
    .chk {
      text-align: center;
      vertical-align: middle;
      height: 0.21in;
      padding: 2px;
      font-size: 8px;
      color: #666;
    }

    /* Session background colors */
    .chk.am {
      background: #e8f4fd;
    }

    .chk.noon {
      background: #fff8e8;
    }

    .chk.pm {
      background: #f0f8ee;
      border-right: 1.5px solid var(--line);
    }

    /* Week divider */
    th.week-break,
    td.week-break {
      border-right: 3px solid var(--line) !important;
    }

    @media screen {
      body {
        padding: 20px;
        background: #ddd;
      }

      .page {
        max-width: 11in;
        background: #fff;
        margin: 0 auto 24px;
        padding: 0.45in 0.45in 0.35in;
        box-shadow: 0 2px 14px rgba(0, 0, 0, 0.13);
      }
    }

    @media print {
      body {
        padding: 0;
        background: #fff;
      }
    }
"""


def count_name_variants(name: str) -> int:
    """A name like "Pulley - straight, lateral, behind back" lists 3 movement variants."""
    parts = re.split(r"—|-", name)
    if len(parts) < 2:
        return 1

    variants_part = "-".join(parts[1:])
    variants = [
        cleaned
        for cleaned in (part.replace("(", "").replace(")", "").strip() for part in variants_part.split(","))
        if cleaned
    ]
    return max(1, len(variants))


def estimate_minutes(name: str, detail: str) -> int:
    sets_match = re.search(r"(\d+)\s*sets?", detail, re.I)
    reps_match = re.search(r"(\d+)\s*reps?", detail, re.I)
    directions_match = re.search(r"(\d+)\s*directions?", detail, re.I)
    hold_on_off_match = re.search(
        r"hold\s*(\d+)\s*sec\s*on\s*/\s*(\d+)\s*(?:sec\s*)?off", detail, re.I
    )
    hold_match = re.search(r"hold\s*(\d+)\s*sec", detail, re.I)
    is_bilateral = re.search(r"\bbilateral\b", detail, re.I) is not None

    sets = int(sets_match.group(1)) if sets_match else 1
    reps = int(reps_match.group(1)) if reps_match else 0
    directions = int(directions_match.group(1)) if directions_match else 1

    seconds_per_rep = TIMING["movement_sec_per_rep"] + TIMING["transition_sec_per_rep"]
    if hold_on_off_match:
        on_sec = int(hold_on_off_match.group(1))
        off_sec = int(hold_on_off_match.group(2))
        seconds_per_rep = on_sec + off_sec + TIMING["transition_sec_per_rep"]
    elif hold_match:
        seconds_per_rep = int(hold_match.group(1)) + TIMING["movement_sec_per_rep"]

    variant_count = count_name_variants(name)
    work_seconds = (
        sets
        * reps
        * directions
        * variant_count
        * seconds_per_rep
        * (TIMING["bilateral_multiplier"] if is_bilateral else 1)
    )
    rest_seconds = max(sets - 1, 0) * TIMING["rest_between_sets_sec"]
    total_seconds = work_seconds + rest_seconds + TIMING["setup_sec_per_exercise"]
    # math.floor(x + 0.5) to match JavaScript's Math.round on .5 boundaries.
    return max(1, math.floor(total_seconds / 60 + 0.5))


EXERCISES_WITH_MINUTES = [
    {**exercise, "minutes": estimate_minutes(exercise["name"], exercise["detail"])}
    for exercise in EXERCISES
]

DAY_MINUTES = sum(exercise["minutes"] for exercise in EXERCISES_WITH_MINUTES)


def dow(date: dt.date) -> int:
    """Day of week with Sunday == 0, matching DAY_NAMES."""
    return (date.weekday() + 1) % 7


def period_dates(start: dt.date, period: int) -> list[dt.date]:
    first = start + dt.timedelta(days=period * DAYS_PER_PERIOD)
    return [first + dt.timedelta(days=offset) for offset in range(DAYS_PER_PERIOD)]


def format_period_label(dates: list[dt.date]) -> str:
    start, end = dates[0], dates[-1]
    if start.year != end.year:
        return (
            f"{start.strftime('%b')} {start.day}, {start.year} – "
            f"{end.strftime('%b')} {end.day}, {end.year}"
        )
    if start.month != end.month:
        return f"{start.strftime('%b')} {start.day} – {end.strftime('%b')} {end.day}, {end.year}"
    return f"{start.strftime('%b')} {start.day} – {end.day}, {end.year}"


def build_page(dates: list[dt.date]) -> str:
    # A heavy rule closes each 7-day week.
    week_break = {index: (index + 1) % 7 == 0 for index in range(len(dates))}

    html = ['<div class="page">']
    html.append(
        f"""<div class="page-header">
    <h1>{HEADER_TITLE}</h1>
    <span class="subtitle">{format_period_label(dates)} &nbsp;|&nbsp; ~{DAY_MINUTES} min/day</span>
  </div>"""
    )

    html.append('<table><colgroup><col style="width:2.6in">')
    html.extend("<col><col><col>" for _ in dates)
    html.append("</colgroup>")

    html.append('<thead><tr><th class="ex-col">Exercise</th>')
    previous_month = None
    for index, date in enumerate(dates):
        break_class = " week-break" if week_break[index] else ""
        # Rendered in every header, blank unless the month changes, so day numbers stay aligned.
        tag = date.strftime("%b") if date.month != previous_month else "&nbsp;"
        month_tag = f'<span class="month-tag">{tag}</span>'
        previous_month = date.month
        html.append(
            f'<th class="day-hdr{break_class}" colspan="3">{month_tag}'
            f'<span class="day-num">{date.day}</span>{DAY_NAMES[dow(date)]}<br />'
            '<span class="session-key">AM &nbsp; MD &nbsp; PM</span></th>'
        )
    html.append("</tr></thead><tbody>")

    for exercise in EXERCISES_WITH_MINUTES:
        html.append(
            f'<tr><td class="ex-col">{exercise["name"]}'
            f'<span class="ex-detail">{exercise["detail"]}  ·  ~{exercise["minutes"]} min</span></td>'
        )
        for index in range(len(dates)):
            break_class = " week-break" if week_break[index] else ""
            html.append('<td class="chk am" title="Morning"></td>')
            html.append('<td class="chk noon" title="Midday"></td>')
            html.append(f'<td class="chk pm{break_class}" title="Evening"></td>')
        html.append("</tr>")

    html.append("</tbody></table></div>")
    return "".join(html)


def build_html(start: dt.date, periods: int) -> str:
    page_dates = [period_dates(start, period) for period in range(periods)]
    pages = "\n".join(build_page(dates) for dates in page_dates)

    title = format_period_label(page_dates[0])
    if periods > 1:
        title = f"{page_dates[0][0]:%b %d, %Y} – {page_dates[-1][-1]:%b %d, %Y}"

    return f"""<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{HEADER_TITLE} — {title}</title>
  <style>{CSS}  </style>
</head>

<body>
{pages}
</body>

</html>
"""


def parse_date(text: str) -> dt.date:
    """Accept YYYY-MM-DD, M/D/YYYY, M/D/YY, or M/D (current year)."""
    text = text.strip()
    if text.count("/") == 1:
        # Add the year before parsing so 2/29 is checked against this year, not 1900.
        text = f"{text}/{dt.date.today().year}"
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y"):
        try:
            return dt.datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    raise ValueError(text)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate the printable workout checklist.")
    parser.add_argument(
        "start_date",
        nargs="?",
        help=(
            "First day of the two-week block, as YYYY-MM-DD, M/D/YYYY, or M/D "
            "(default: today)."
        ),
    )
    parser.add_argument(
        "-p",
        "--periods",
        type=int,
        default=1,
        help="Number of consecutive two-week pages to render (default: 1).",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output HTML file (default: {DEFAULT_OUTPUT.name}).",
    )
    args = parser.parse_args(argv)

    if args.periods < 1:
        parser.error("--periods must be at least 1")

    if args.start_date:
        try:
            args.start = parse_date(args.start_date)
        except ValueError:
            parser.error(
                f"could not parse start date {args.start_date!r}; "
                "use YYYY-MM-DD, M/D/YYYY, or M/D"
            )
    else:
        args.start = dt.date.today()

    return args


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    html = build_html(args.start, args.periods)
    args.output.write_text(html, encoding="utf-8")

    end = args.start + dt.timedelta(days=args.periods * DAYS_PER_PERIOD - 1)
    print(
        f"Wrote {args.output} ({args.start.isoformat()} through {end.isoformat()}, "
        f"~{DAY_MINUTES} min/day)"
    )


if __name__ == "__main__":
    main()
