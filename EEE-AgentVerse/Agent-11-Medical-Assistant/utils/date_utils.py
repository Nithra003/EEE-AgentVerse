"""
utils/date_utils.py — Date/time parsing, formatting, and calculation helpers.
"""
from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import Optional


_PARSE_FMTS = [
    "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%m/%d/%Y",
    "%d %b %Y", "%d %B %Y", "%B %d, %Y",
]
_TIME_FMTS = ["%H:%M", "%I:%M %p", "%I:%M%p", "%H:%M:%S"]


def parse_date(value: str) -> Optional[date]:
    """Try multiple formats; return None on failure."""
    for fmt in _PARSE_FMTS:
        try:
            return datetime.strptime(value.strip(), fmt).date()
        except ValueError:
            continue
    return None


def parse_time(value: str) -> Optional[time]:
    """Try multiple formats; return None on failure."""
    for fmt in _TIME_FMTS:
        try:
            return datetime.strptime(value.strip(), fmt).time()
        except ValueError:
            continue
    return None


def format_date(d: date, fmt: str = "%d %b %Y") -> str:
    return d.strftime(fmt)


def format_time(t: time, fmt: str = "%I:%M %p") -> str:
    return t.strftime(fmt)


def today_str() -> str:
    return date.today().isoformat()


def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def days_until(target: date) -> int:
    return (target - date.today()).days


def add_days(d: date, n: int) -> date:
    return d + timedelta(days=n)


def medicine_end_date(start: date, duration_days: int) -> date:
    return start + timedelta(days=duration_days - 1)


def is_past(d: date) -> bool:
    return d < date.today()


def friendly_date(d: date) -> str:
    """Return 'Today', 'Tomorrow', 'Yesterday', or formatted date."""
    delta = (d - date.today()).days
    if delta == 0:
        return "Today"
    if delta == 1:
        return "Tomorrow"
    if delta == -1:
        return "Yesterday"
    return format_date(d)
