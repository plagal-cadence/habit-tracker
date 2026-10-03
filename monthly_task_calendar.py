#!/usr/bin/env python3
"""Generate the printable monthly task checklist calendar.

Usage:
    python monthly_task_calendar.py                 # the current month
    python monthly_task_calendar.py 2026-09         # September 2026
    python monthly_task_calendar.py 2026-09-14      # the month containing that date
    python monthly_task_calendar.py 2026-09 -m 4    # Sep-Dec 2026, one page each
    python monthly_task_calendar.py 2026-09 -o sept.html

Writes month_task_calendar.html next to this script unless -o is given. The
output is a self-contained HTML page sized for 8in x 5.5in paper, one page per month.
"""

from __future__ import annotations

import argparse
import calendar
import datetime as dt
from pathlib import Path

DEFAULT_OUTPUT = Path(__file__).with_name("month_task_calendar.html")

DAILY_TASKS = [
    {"icon": "book-open-page-variant", "name": "Devotions", "color": "#2f7fc7"},
    {"icon": "tooth-outline", "name": "Floss", "color": "#16926f"},
    {"icon": "human-handsup", "name": "Stretch / Hinge Health", "color": "#9b59b6"},
    {"icon": "bike-fast", "name": "Exercise", "color": "#e67e22"},
    {"icon": "musical-note", "name": "Music practice", "color": "#d6455d"},
    {"icon": "star-outline", "name": "One Thing", "color": "#b8860b"},
]

WEEKLY_TASKS = [
    {"icon": "phone", "name": "Call Dad", "color": "#3b6fb6"},
    {"icon": "bathtub-outline", "name": "Bathrooms", "color": "#2d9c83"},
    {"icon": "vacuum", "name": "Vacuum", "color": "#8a6ecf"},
    {"icon": "heart-outline", "name": "Date night", "color": "#d65472"},
]

MONTHLY_TASKS = [
    {"icon": "snowflake", "name": "HVAC filter 20x25x1", "color": "#4687d6"},
    {"icon": "shower", "name": "Drain declogger", "color": "#1f9b8a"},
    {"icon": "music-clef-treble", "name": "Review music planner", "color": "#c2673d"},
]

ICON_PATHS = {
    "bathtub-outline": '<path fill="currentColor" d="M7 5C8.11 5 9 5.9 9 7S8.11 9 7 9 5 8.11 5 7 5.9 5 7 5M20 13V4.83C20 3.27 18.73 2 17.17 2C16.42 2 15.7 2.3 15.17 2.83L13.92 4.08C13.76 4.03 13.59 4 13.41 4C13 4 12.64 4.12 12.33 4.32L15.09 7.08C15.29 6.77 15.41 6.4 15.41 6C15.41 5.82 15.38 5.66 15.34 5.5L16.59 4.24C16.74 4.09 16.95 4 17.17 4C17.63 4 18 4.37 18 4.83V13H11.15C10.85 12.79 10.58 12.55 10.33 12.28L8.93 10.73C8.74 10.5 8.5 10.35 8.24 10.23C7.93 10.08 7.59 10 7.24 10C6 10 5 11 5 12.25V13H2V19C2 20.1 2.9 21 4 21C4 21.55 4.45 22 5 22H19C19.55 22 20 21.55 20 21C21.1 21 22 20.1 22 19V13H20M20 19H4V15H20V19Z" />',
    "bike-fast": '<path fill="currentColor" d="M16 1.2C15 1.2 14.2 2 14.2 3S15 4.8 16 4.8 17.8 4 17.8 3 17 1.2 16 1.2M12.4 4.1C11.93 4.1 11.5 4.29 11.2 4.6L7.5 8.29C7.19 8.6 7 9 7 9.5C7 10.13 7.33 10.66 7.85 10.97L11.2 13V18H13V11.5L10.75 9.85L13.07 7.5L14.8 10H19V8.2H15.8L13.86 4.93C13.57 4.43 13 4.1 12.4 4.1M10 3H3C2.45 3 2 2.55 2 2S2.45 1 3 1H12.79C12.58 1.34 12.41 1.71 12.32 2.11C11.46 2.13 10.65 2.45 10 3M5 12C2.24 12 0 14.24 0 17S2.24 22 5 22 10 19.76 10 17 7.76 12 5 12M5 20.5C3.07 20.5 1.5 18.93 1.5 17S3.07 13.5 5 13.5 8.5 15.07 8.5 17 6.93 20.5 5 20.5M19 12C16.24 12 14 14.24 14 17S16.24 22 19 22 24 19.76 24 17 21.76 12 19 12M19 20.5C17.07 20.5 15.5 18.93 15.5 17S17.07 13.5 19 13.5 22.5 15.07 22.5 17 20.93 20.5 19 20.5M5.32 11H1C.448 11 0 10.55 0 10S.448 9 1 9H5.05C5.03 9.16 5 9.33 5 9.5C5 10.03 5.12 10.54 5.32 11M6 7H2C1.45 7 1 6.55 1 6S1.45 5 2 5H7.97L6.09 6.87C6.05 6.91 6 6.96 6 7Z" />',
    "book-open-page-variant": '<path fill="currentColor" d="M19 2L14 6.5V17.5L19 13V2M6.5 5C4.55 5 2.45 5.4 1 6.5V21.16C1 21.41 1.25 21.66 1.5 21.66C1.6 21.66 1.65 21.59 1.75 21.59C3.1 20.94 5.05 20.5 6.5 20.5C8.45 20.5 10.55 20.9 12 22C13.35 21.15 15.8 20.5 17.5 20.5C19.15 20.5 20.85 20.81 22.25 21.56C22.35 21.61 22.4 21.59 22.5 21.59C22.75 21.59 23 21.34 23 21.09V6.5C22.4 6.05 21.75 5.75 21 5.5V19C19.9 18.65 18.7 18.5 17.5 18.5C15.8 18.5 13.35 19.15 12 20V6.5C10.55 5.4 8.45 5 6.5 5Z" />',
    "heart-outline": '<path fill="currentColor" d="M12.1,18.55L12,18.65L11.89,18.55C7.14,14.24 4,11.39 4,8.5C4,6.5 5.5,5 7.5,5C9.04,5 10.54,6 11.07,7.36H12.93C13.46,6 14.96,5 16.5,5C18.5,5 20,6.5 20,8.5C20,11.39 16.86,14.24 12.1,18.55M16.5,3C14.76,3 13.09,3.81 12,5.08C10.91,3.81 9.24,3 7.5,3C4.42,3 2,5.41 2,8.5C2,12.27 5.4,15.36 10.55,20.03L12,21.35L13.45,20.03C18.6,15.36 22,12.27 22,8.5C22,5.41 19.58,3 16.5,3Z" />',
    "human-handsup": '<path fill="currentColor" d="M5,1C5,3.7 6.56,6.16 9,7.32V22H11V15H13V22H15V7.31C17.44,6.16 19,3.7 19,1H17A5,5 0 0,1 12,6A5,5 0 0,1 7,1M12,1C10.89,1 10,1.89 10,3C10,4.11 10.89,5 12,5C13.11,5 14,4.11 14,3C14,1.89 13.11,1 12,1Z" />',
    "music-clef-treble": '<path fill="currentColor" d="M13 11V7.5L15.2 5.29C16 4.5 16.15 3.24 15.59 2.26C15.14 1.47 14.32 1 13.45 1C13.24 1 13 1.03 12.81 1.09C11.73 1.38 11 2.38 11 3.5V6.74L7.86 9.91C6.2 11.6 5.7 14.13 6.61 16.34C7.38 18.24 9.06 19.55 11 19.89V20.5C11 20.76 10.77 21 10.5 21H9V23H10.5C11.85 23 13 21.89 13 20.5V20C15.03 20 17.16 18.08 17.16 15.25C17.16 12.95 15.24 11 13 11M13 3.5C13 3.27 13.11 3.09 13.32 3.03C13.54 2.97 13.77 3.06 13.88 3.26C14 3.46 13.96 3.71 13.8 3.87L13 4.73V3.5M11 11.5C10.03 12.14 9.3 13.24 9.04 14.26L11 14.78V17.83C9.87 17.53 8.9 16.71 8.43 15.57C7.84 14.11 8.16 12.45 9.26 11.33L11 9.5V11.5M13 18V12.94C14.17 12.94 15.18 14.04 15.18 15.25C15.18 17 13.91 18 13 18Z" />',
    "musical-note": '<path fill="currentColor" d="M12 3V13.55C11.41 13.21 10.73 13 10 13C7.79 13 6 14.79 6 17S7.79 21 10 21 14 19.21 14 17V7H18V3H12Z" />',
    "phone": '<path fill="currentColor" d="M6.62,10.79C8.06,13.62 10.38,15.94 13.21,17.38L15.41,15.18C15.69,14.9 16.08,14.82 16.43,14.93C17.55,15.3 18.75,15.5 20,15.5A1,1 0 0,1 21,16.5V20A1,1 0 0,1 20,21A17,17 0 0,1 3,4A1,1 0 0,1 4,3H7.5A1,1 0 0,1 8.5,4C8.5,5.25 8.7,6.45 9.07,7.57C9.18,7.92 9.1,8.31 8.82,8.59L6.62,10.79Z" />',
    "shower": '<path fill="currentColor" d="M21,14V15C21,16.91 19.93,18.57 18.35,19.41L19,22H17L16.5,20C16.33,20 16.17,20 16,20H8C7.83,20 7.67,20 7.5,20L7,22H5L5.65,19.41C4.07,18.57 3,16.91 3,15V14H2V12H20V5A1,1 0 0,0 19,4C18.5,4 18.12,4.34 18,4.79C18.63,5.33 19,6.13 19,7H13A3,3 0 0,1 16,4C16.06,4 16.11,4 16.17,4C16.58,2.84 17.69,2 19,2A3,3 0 0,1 22,5V14H21V14M19,14H5V15A3,3 0 0,0 8,18H16A3,3 0 0,0 19,15V14Z" />',
    "snowflake": '<path fill="currentColor" d="M20.79,13.95L18.46,14.57L16.46,13.44V10.56L18.46,9.43L20.79,10.05L21.31,8.12L19.54,7.65L20,5.88L18.07,5.36L17.45,7.69L15.45,8.82L13,7.38V5.12L14.71,3.41L13.29,2L12,3.29L10.71,2L9.29,3.41L11,5.12V7.38L8.5,8.82L6.5,7.69L5.92,5.36L4,5.88L4.47,7.65L2.7,8.12L3.22,10.05L5.55,9.43L7.55,10.56V13.45L5.55,14.58L3.22,13.96L2.7,15.89L4.47,16.36L4,18.12L5.93,18.64L6.55,16.31L8.55,15.18L11,16.62V18.88L9.29,20.59L10.71,22L12,20.71L13.29,22L14.7,20.59L13,18.88V16.62L15.5,15.17L17.5,16.3L18.12,18.63L20,18.12L19.53,16.35L21.3,15.88L20.79,13.95M9.5,10.56L12,9.11L14.5,10.56V13.44L12,14.89L9.5,13.44V10.56Z" />',
    "star-outline": '<path fill="currentColor" d="M12,15.39L8.24,17.66L9.23,13.38L5.91,10.5L10.29,10.13L12,6.09L13.71,10.13L18.09,10.5L14.77,13.38L15.76,17.66M22,9.24L14.81,8.63L12,2L9.19,8.63L2,9.24L7.45,13.97L5.82,21L12,17.27L18.18,21L16.54,13.97L22,9.24Z" />',
    "tooth-outline": '<path fill="currentColor" d="M7,2C4,2 2,5 2,8C2,10.11 3,13 4,14C5,15 6,22 8,22C12.54,22 10,15 12,15C14,15 11.46,22 16,22C18,22 19,15 20,14C21,13 22,10.11 22,8C22,5 20,2 17,2C14,2 14,3 12,3C10,3 10,2 7,2M7,4C9,4 10,5 12,5C14,5 15,4 17,4C18.67,4 20,6 20,8C20,9.75 19.14,12.11 18.19,13.06C17.33,13.92 16.06,19.94 15.5,19.94C15.29,19.94 15,18.88 15,17.59C15,15.55 14.43,13 12,13C9.57,13 9,15.55 9,17.59C9,18.88 8.71,19.94 8.5,19.94C7.94,19.94 6.67,13.92 5.81,13.06C4.86,12.11 4,9.75 4,8C4,6 5.33,4 7,4Z" />',
    "vacuum": '<path fill="currentColor" d="M23 20V22H16L16 20H18.46L12 4.61C11.81 4.14 11.5 3.76 11.06 3.46S10.14 3 9.61 3C8.9 3 8.28 3.27 7.76 3.79S7 4.92 7 5.64L7 9H8C10.21 9 12 10.79 12 13V22H8C8.61 21.16 9 20.13 9 19C9 16.24 6.76 14 4 14C3.29 14 2.61 14.15 2 14.42V9H5V5.64C5 4.8 5.23 4 5.63 3.32C6.04 2.62 6.59 2.06 7.3 1.63C8 1.21 8.77 1 9.61 1C10.55 1 11.4 1.26 12.16 1.77S13.5 2.97 13.87 3.81L20.66 20H23M7 19C7 20.66 5.66 22 4 22S1 20.66 1 19 2.34 16 4 16 7 17.34 7 19M5 19C5 18.45 4.55 18 4 18S3 18.45 3 19 3.45 20 4 20 5 19.55 5 19Z" />',
}

DAY_NAMES = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

CSS = """
    :root {
      --page-width: 8in;
      --page-height: 5.5in;
      --notes-spacing: 0.15in;
      --ink: #000;
      --line: #666;
      --light-line: #999;
      --bg: #fff;
      --accent: #1f5f9b;
      --accent-soft: #e6f1fb;
      --accent-2: #e67e50;
      --accent-2-soft: #fbede6;
      --weekend-bg: #edf5ff;
      --task-bg: #f1f7ff;
      --panel-bg: #f8fbff;
      --paper-bg: #fcfeff;
      --task-col-width: 1.35in;
      --day-columns: 31;
      --week-columns: 6;
    }

    @page {
      size: 8in 5.5in;
      margin: 0;
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      background: var(--paper-bg);
      color: var(--ink);
      font-family: "Trebuchet MS", "Segoe UI", sans-serif;
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }

    .month-page {
      width: 100%;
      min-height: var(--page-height);
      padding: 0;
      page-break-after: always;
      display: flex;
      flex-direction: column;
      gap: 0.025in;
    }

    .month-page:last-child {
      page-break-after: auto;
    }

    .header {
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      border-bottom: 2px solid var(--accent);
      padding-bottom: 0.03in;
    }

    .header h1 {
      margin: 0;
      font-size: 22px;
      letter-spacing: 0.2px;
      color: #000;
    }

    .header .subtitle {
      margin: 0;
      font-size: 9.63px;
      text-transform: uppercase;
      letter-spacing: 0.6px;
      color: #000;
    }

    .section-title {
      margin: 0.01in 0 0.02in;
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      font-weight: 700;
      color: #000;
    }

    table {
      border-collapse: collapse;
      width: 100%;
      table-layout: fixed;
    }

    .daily-table,
    .weekly-table {
      border: 1px solid var(--accent);
    }

    .daily-table th,
    .daily-table td,
    .weekly-table th,
    .weekly-table td {
      border: 1px solid var(--light-line);
      text-align: center;
      vertical-align: middle;
      height: 0.105in;
      font-size: 8.25px;
      padding: 0;
    }

    .daily-table thead th,
    .weekly-table thead th {
      font-weight: 700;
      font-size: 9.63px;
      line-height: 1.1;
      background: var(--accent-soft);
      color: #000;
    }

    .task-col {
      text-align: left !important;
      padding-left: 3px !important;
      width: var(--task-col-width);
      font-size: 9.63px;
      font-weight: 600;
      background: var(--task-bg);
    }

    .task-label {
      display: inline-flex;
      align-items: center;
      gap: 3px;
    }

    .task-label > span:last-child {
      font-size: 1.14em;
      line-height: 1.1;
    }

    .task-icon {
      width: 17.88px;
      height: 17.88px;
      flex: 0 0 17.88px;
      vertical-align: middle;
      color: var(--accent-2);
    }

    .date-col {
      width: calc((100% - var(--task-col-width)) / var(--day-columns));
      font-size: 6.88px;
    }

    .weekly-table .date-col {
      width: calc((100% - var(--task-col-width)) / var(--week-columns));
    }

    .date-col.week-end,
    .check-cell.week-end {
      border-right: 3px solid var(--line);
      background: var(--weekend-bg);
    }

    .date-col.weekend-day,
    .check-cell.weekend-day {
      background: var(--weekend-bg);
    }

    .day-name {
      display: block;
      font-size: 8.25px;
      line-height: 1;
    }

    .lower-grid {
      display: grid;
      grid-template-columns: 1.8fr 1fr;
      gap: 0.05in;
      margin-top: 0.01in;
      flex: 1;
      min-height: 0;
    }

    .panel {
      border: 1px solid var(--accent);
      background: var(--panel-bg);
      padding: 0.025in;
      display: flex;
      flex-direction: column;
      min-height: 0;
    }

    .dot-grid {
      flex: 1;
      min-height: 0.3in;
      margin-top: 0.04in;
      display: block;
      overflow: hidden;
    }

    .monthly-list {
      margin: 0;
      padding: 0;
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 0.03in;
      font-size: 9.63px;
      font-weight: 600;
    }

    .monthly-list li {
      display: flex;
      align-items: flex-start;
      gap: 4px;
    }

    .monthly-list .task-label > span:last-child {
      font-size: 1em;
      line-height: 1.1;
    }

    .monthly-list .box {
      width: 8px;
      height: 8px;
      border: 1px solid var(--ink);
      background: var(--accent-2-soft);
      margin-top: 1px;
      flex: 0 0 8px;
    }

    .notes-lines {
      margin-top: 0.02in;
      flex: 1;
      min-height: 0;
      background-image: repeating-linear-gradient(
        to bottom,
        transparent 0,
        transparent calc((var(--notes-spacing) * 1.55) - 1px),
        #b1c9e2 calc((var(--notes-spacing) * 1.55) - 1px),
        #b1c9e2 calc(var(--notes-spacing) * 1.55)
      );
    }

    @media screen {
      body {
        padding: 16px;
        background: linear-gradient(160deg, #d8e9fb 0%, #f3eae0 55%, #fef4ed 100%);
      }

      .month-page {
        max-width: var(--page-width);
        min-height: var(--page-height);
        background: var(--paper-bg);
        margin: 0 auto 16px;
        padding: 0;
        box-shadow: 0 6px 18px rgba(27, 74, 120, 0.2);
      }
    }

    @media print {
      .month-page {
        padding: 0;
      }
    }
"""


def render_icon(icon_name: str, color: str | None = None) -> str:
    style = f' style="color:{color}"' if color else ""
    path = ICON_PATHS.get(icon_name, "")
    return f'<svg class="task-icon" viewBox="0 0 24 24" aria-hidden="true"{style}>{path}</svg>'


def task_label(task: dict) -> str:
    return (
        '<span class="task-label">'
        f'{render_icon(task["icon"], task.get("color"))}'
        f'<span>{task["name"]}</span>'
        "</span>"
    )


def month_dates(year: int, month: int) -> list[dt.date]:
    total = calendar.monthrange(year, month)[1]
    return [dt.date(year, month, day) for day in range(1, total + 1)]


def dow(date: dt.date) -> int:
    """Day of week with Sunday == 0, matching DAY_NAMES."""
    return (date.weekday() + 1) % 7


def week_groups(dates: list[dt.date]) -> list[list[dt.date]]:
    """Split the month into calendar weeks (Sunday-Saturday); edges may be partial."""
    groups: list[list[dt.date]] = []
    for date in dates:
        if not groups or dow(date) == 0:
            groups.append([])
        groups[-1].append(date)
    return groups


def format_week_label(group: list[dt.date], index: int) -> str:
    start, end = group[0].day, group[-1].day
    span = str(start) if start == end else f"{start}-{end}"
    return f"W{index}<br>{span}"


def create_daily_table(dates: list[dt.date], groups: list[list[dt.date]]) -> str:
    week_end_days = {group[-1] for group in groups}

    def classes(date: dt.date) -> str:
        parts = []
        if dow(date) in (0, 6):
            parts.append("weekend-day")
        if date in week_end_days and date != dates[-1]:
            parts.append("week-end")
        return (" " + " ".join(parts)) if parts else ""

    html = ['<table class="daily-table"><thead><tr><th class="task-col"></th>']
    for date in dates:
        html.append(
            f'<th class="date-col{classes(date)}">{date.day}'
            f'<span class="day-name">{DAY_NAMES[dow(date)]}</span></th>'
        )
    html.append("</tr></thead><tbody>")

    for task in DAILY_TASKS:
        html.append(f'<tr><th class="task-col">{task_label(task)}</th>')
        for date in dates:
            html.append(f'<td class="check-cell{classes(date)}"></td>')
        html.append("</tr>")

    html.append("</tbody></table>")
    return "".join(html)


def create_weekly_table(groups: list[list[dt.date]]) -> str:
    html = ['<table class="weekly-table"><thead><tr><th class="task-col"></th>']
    for index, group in enumerate(groups, start=1):
        html.append(f'<th class="date-col">{format_week_label(group, index)}</th>')
    html.append("</tr></thead><tbody>")

    for task in WEEKLY_TASKS:
        html.append(f'<tr><th class="task-col">{task_label(task)}</th>')
        html.extend('<td class="check-cell"></td>' for _ in groups)
        html.append("</tr>")

    html.append("</tbody></table>")
    return "".join(html)


def create_monthly_panel() -> str:
    items = "".join(
        f'<li><span class="box"></span>{task_label(task)}</li>' for task in MONTHLY_TASKS
    )
    return f'<ul class="monthly-list">{items}</ul>'


def create_dot_grid_svg(pattern_id: str) -> str:
    # SVG circles always print regardless of "Print Background Graphics" browser setting
    spacing = 20.16  # 0.15in * 1.4 * 96dpi
    offset = 3.84  # 0.04in * 96dpi
    radius = 0.85
    return f"""<svg class="dot-grid" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" width="100%" height="100%">
          <defs>
            <pattern id="{pattern_id}" x="{offset}" y="{offset}" width="{spacing}" height="{spacing}" patternUnits="userSpaceOnUse">
              <circle cx="0" cy="0" r="{radius}" fill="#3a3a3a"/>
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#{pattern_id})"/>
        </svg>"""


def create_month_page(year: int, month: int) -> str:
    dates = month_dates(year, month)
    groups = week_groups(dates)
    title = f"{calendar.month_name[month]} {year}"
    # Day and week counts vary by month, so scope the column widths to this page.
    page_vars = f"--day-columns: {len(dates)}; --week-columns: {len(groups)};"

    return f"""  <section class="month-page" style="{page_vars}">
    <div class="header">
      <h1>{title}</h1>
      <p class="subtitle">Task Checkoff Calendar</p>
    </div>

    <h2 class="section-title">Daily Habit Tracker</h2>
    {create_daily_table(dates, groups)}

    <div class="lower-grid">
      <div class="panel">
        <h2 class="section-title">Weekly Tasks</h2>
        {create_weekly_table(groups)}
        {create_dot_grid_svg(f"dotpat-{year}-{month:02d}")}
      </div>

      <div class="panel">
        <h2 class="section-title">Monthly Tasks</h2>
        {create_monthly_panel()}

        <h2 class="section-title">Notes</h2>
        <div class="notes-lines"></div>
      </div>
    </div>
  </section>"""


def add_months(year: int, month: int, count: int) -> tuple[int, int]:
    index = (year * 12 + month - 1) + count
    return index // 12, index % 12 + 1


def build_html(year: int, month: int, months: int) -> str:
    spans = [add_months(year, month, offset) for offset in range(months)]
    pages = "\n\n".join(create_month_page(y, m) for y, m in spans)

    first = f"{calendar.month_name[spans[0][1]]} {spans[0][0]}"
    last = f"{calendar.month_name[spans[-1][1]]} {spans[-1][0]}"
    title = first if months == 1 else f"{first} - {last}"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Task Calendar ({title})</title>
  <style>{CSS}  </style>
</head>
<body>
{pages}
</body>
</html>
"""


def parse_month(text: str) -> tuple[int, int]:
    """Accept YYYY-MM or any full YYYY-MM-DD date and return (year, month)."""
    for fmt in ("%Y-%m", "%Y-%m-%d"):
        try:
            parsed = dt.datetime.strptime(text, fmt)
        except ValueError:
            continue
        return parsed.year, parsed.month
    raise ValueError(text)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate the printable monthly task checklist calendar."
    )
    parser.add_argument(
        "month",
        nargs="?",
        help="Month to render, as YYYY-MM or YYYY-MM-DD (default: the current month).",
    )
    parser.add_argument(
        "-m",
        "--months",
        type=int,
        default=1,
        help="Number of consecutive months to render, one page each (default: 1).",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output HTML file (default: {DEFAULT_OUTPUT.name}).",
    )
    args = parser.parse_args(argv)

    if args.months < 1:
        parser.error("--months must be at least 1")

    if args.month:
        try:
            args.year, args.month_number = parse_month(args.month)
        except ValueError:
            parser.error(f"could not parse month {args.month!r}; use YYYY-MM or YYYY-MM-DD")
    else:
        today = dt.date.today()
        args.year, args.month_number = today.year, today.month

    return args


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    html = build_html(args.year, args.month_number, args.months)
    args.output.write_text(html, encoding="utf-8")

    end_year, end_month = add_months(args.year, args.month_number, args.months - 1)
    span = f"{args.year}-{args.month_number:02d}"
    if args.months > 1:
        span += f" through {end_year}-{end_month:02d}"
    print(f"Wrote {args.output} ({span})")


if __name__ == "__main__":
    main()
