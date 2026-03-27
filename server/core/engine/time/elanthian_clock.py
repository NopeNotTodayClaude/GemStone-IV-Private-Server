"""
ElanthianClock
Pure conversion functions. No state, no ticking, no DB.
Reads scripts/data/time_config.lua once at import time.

Public API:
    from server.core.engine.time.elanthian_clock import ElanthianClock

    now   = ElanthianClock.now()          # full snapshot dict
    day   = ElanthianClock.day_name()     # "Feastday"
    month = ElanthianClock.month_name()   # "Charlatos"
    year  = ElanthianClock.elanthian_year() # 5126
    period = ElanthianClock.period()      # "morning", "evening", etc.
    period_id = ElanthianClock.period_id() # "morning", "late_evening", etc.
    hour_name = ElanthianClock.hour_name() # "Hour of Lumnis"
    holiday = ElanthianClock.holiday()    # "Feast of the Immortals" or None
    time_str = ElanthianClock.format_time() # GS4-canonical TIME output string
    cal_day_table  = ElanthianClock.calendar_day_table()
    cal_month_table = ElanthianClock.calendar_month_table()
    cal_time_table  = ElanthianClock.calendar_time_table()
    cal_holiday_table = ElanthianClock.calendar_holiday_table()
"""

import os
import logging
from datetime import datetime

log = logging.getLogger(__name__)

_HERE         = os.path.dirname(os.path.abspath(__file__))
# time/ -> engine/ -> core/ -> server/ -> project_root  =  4 levels up
_PROJECT_ROOT = os.path.normpath(os.path.join(_HERE, "..", "..", "..", ".."))
_LUA_CFG      = os.path.join(_PROJECT_ROOT, "scripts", "data", "time_config.lua")


def _load_config() -> dict:
    try:
        from lupa import LuaRuntime  # type: ignore
        lua = LuaRuntime(unpack_returned_tuples=True)
        with open(_LUA_CFG, "r", encoding="utf-8") as f:
            src = f.read()
        tbl = lua.execute(src)

        def _cvt(t):
            if t is None:
                return None
            if hasattr(t, "items"):
                items = list(t.items())
                if items and all(isinstance(k, int) for k, _ in items):
                    return {k: _cvt(v) for k, v in items}
                return {k: _cvt(v) for k, v in items}
            return t

        return _cvt(tbl)
    except Exception as e:
        log.warning("time_config.lua load failed (%s) — using hardcoded defaults", e)
        return _DEFAULTS


# ── Hardcoded fallback (exact match of time_config.lua) ───────────────────────
_DEFAULTS = {
    "year_offset": 3100,
    "days": {
        0: "Volnes", 1: "Tilamaires", 2: "Leyan", 3: "Niiman",
        4: "Day of the Huntress", 5: "Feastday", 6: "Restday",
    },
    "months": {
        1: "Lormesta", 2: "Fashanos", 3: "Charlatos", 4: "Olaesta",
        5: "Ivastaen", 6: "Lumnea", 7: "Koaratos", 8: "Phoenatos",
        9: "Imaerasta", 10: "Jastatos", 11: "Eoantos", 12: "Eorgaen",
    },
    "hour_names": {
        0:  {"hour": "Hour of Ronan",  "period": "deep night",   "period_id": "deep_night"},
        1:  {"hour": "Hour of Ronan",  "period": "deep night",   "period_id": "deep_night"},
        2:  {"hour": "Hour of Ronan",  "period": "deep night",   "period_id": "deep_night"},
        3:  {"hour": "Hour of Ronan",  "period": "deep night",   "period_id": "deep_night"},
        4:  {"hour": "Hour of Ronan",  "period": "deep night",   "period_id": "deep_night"},
        5:  {"hour": "Hour of Lumnis", "period": "dawn",         "period_id": "dawn"},
        6:  {"hour": "Hour of Lumnis", "period": "dawn",         "period_id": "dawn"},
        7:  {"hour": "Hour of Lumnis", "period": "morning",      "period_id": "morning"},
        8:  {"hour": "Hour of Lumnis", "period": "morning",      "period_id": "morning"},
        9:  {"hour": "Hour of Lumnis", "period": "morning",      "period_id": "morning"},
        10: {"hour": "Hour of Lumnis", "period": "morning",      "period_id": "morning"},
        11: {"hour": "Hour of Phoen",  "period": "midday",       "period_id": "midday"},
        12: {"hour": "Hour of Phoen",  "period": "midday",       "period_id": "midday"},
        13: {"hour": "Hour of Phoen",  "period": "midday",       "period_id": "midday"},
        14: {"hour": "Hour of Phoen",  "period": "afternoon",    "period_id": "afternoon"},
        15: {"hour": "Hour of Phoen",  "period": "afternoon",    "period_id": "afternoon"},
        16: {"hour": "Hour of Phoen",  "period": "afternoon",    "period_id": "afternoon"},
        17: {"hour": "Hour of Phoen",  "period": "afternoon",    "period_id": "afternoon"},
        18: {"hour": "Hour of Tonis",  "period": "evening",      "period_id": "evening"},
        19: {"hour": "Hour of Tonis",  "period": "evening",      "period_id": "evening"},
        20: {"hour": "Hour of Tonis",  "period": "evening",      "period_id": "evening"},
        21: {"hour": "Hour of Tonis",  "period": "late evening", "period_id": "late_evening"},
        22: {"hour": "Hour of Ronan",  "period": "late evening", "period_id": "late_evening"},
        23: {"hour": "Hour of Ronan",  "period": "night",        "period_id": "night"},
    },
    "holidays": [
        {"month": 2,  "day": 14, "name": "Day of Voaris and Laethe"},
        {"month": 4,  "day": 1,  "name": "Day of Zelia's Warning"},
        {"month": 5,  "day": 1,  "name": "Day of Kuon's Blessing"},
        {"month": 5,  "day": 20, "name": "Festival of Oleani"},
        {"month": 7,  "day": 14, "name": "Cholen's Eve"},
        {"month": 10, "day": 31, "name": "Eve of the Reunion"},
        {"month": 12, "day": 20, "name": "Feast of the Immortals"},
        {"month": 12, "day": 21, "name": "Feast of the Immortals"},
        {"month": 12, "day": 22, "name": "Feast of the Immortals"},
        {"month": 12, "day": 23, "name": "Feast of the Immortals"},
        {"month": 12, "day": 24, "name": "Feast of the Immortals"},
        {"month": 12, "day": 25, "name": "Feast of the Immortals"},
        {"month": 12, "day": 31, "name": "Lornon's Eve"},
    ],
}

_CFG = _load_config()


class ElanthianClock:
    """
    Static helper class. All methods operate on datetime.now() unless
    a `dt` argument is provided. Thread-safe — no mutable state.
    """

    # ── Core conversions ──────────────────────────────────────────────────────

    @staticmethod
    def elanthian_year(dt: datetime = None) -> int:
        dt = dt or datetime.now()
        return dt.year + int(_CFG.get("year_offset", 3100))

    @staticmethod
    def day_name(dt: datetime = None) -> str:
        dt = dt or datetime.now()
        days = _CFG.get("days", _DEFAULTS["days"])
        return days.get(dt.weekday(), str(dt.strftime("%A")))

    @staticmethod
    def month_name(dt: datetime = None) -> str:
        dt = dt or datetime.now()
        months = _CFG.get("months", _DEFAULTS["months"])
        return months.get(dt.month, dt.strftime("%B"))

    @staticmethod
    def _hour_data(dt: datetime = None) -> dict:
        dt = dt or datetime.now()
        hour_names = _CFG.get("hour_names", _DEFAULTS["hour_names"])
        return hour_names.get(dt.hour, {
            "hour": "Hour of Ronan", "period": "night", "period_id": "night"
        })

    @staticmethod
    def hour_name(dt: datetime = None) -> str:
        """e.g. 'Hour of Lumnis'"""
        return ElanthianClock._hour_data(dt).get("hour", "Hour of Ronan")

    @staticmethod
    def period(dt: datetime = None) -> str:
        """e.g. 'morning', 'late evening'"""
        return ElanthianClock._hour_data(dt).get("period", "night")

    @staticmethod
    def period_id(dt: datetime = None) -> str:
        """e.g. 'morning', 'late_evening' — use for comparisons"""
        return ElanthianClock._hour_data(dt).get("period_id", "night")

    @staticmethod
    def holiday(dt: datetime = None) -> "str | None":
        """Returns the Elanthian holiday name for today, or None."""
        dt = dt or datetime.now()
        holidays = _CFG.get("holidays", _DEFAULTS["holidays"])
        if isinstance(holidays, dict):
            holidays = list(holidays.values())
        for h in holidays:
            if isinstance(h, dict):
                if h.get("month") == dt.month and h.get("day") == dt.day:
                    return h.get("name")
        return None

    # ── Full snapshot ─────────────────────────────────────────────────────────

    @staticmethod
    def now(dt: datetime = None) -> dict:
        """
        Returns a full Elanthian time snapshot dict:
          {
            day_name, month_name, day, year, hour_name, period, period_id,
            time_24, time_12, holiday, elanthian_year
          }
        """
        dt = dt or datetime.now()
        return {
            "day_name":      ElanthianClock.day_name(dt),
            "month_name":    ElanthianClock.month_name(dt),
            "day":           dt.day,
            "elanthian_year": ElanthianClock.elanthian_year(dt),
            "hour_name":     ElanthianClock.hour_name(dt),
            "period":        ElanthianClock.period(dt),
            "period_id":     ElanthianClock.period_id(dt),
            "time_24":       dt.strftime("%H:%M"),
            "time_12":       dt.strftime("%I:%M %p").lstrip("0"),
            "holiday":       ElanthianClock.holiday(dt),
        }

    # ── GS4-canonical output strings ─────────────────────────────────────────

    @staticmethod
    def format_time(dt: datetime = None) -> str:
        """
        Exact GS4 TIME verb format:
          "Today is Leyan, day 21 of the month Ivastaen in the year 5114.
           It is 20:46 by the elven time standard.
           It is currently late evening."
        """
        dt  = dt or datetime.now()
        snap = ElanthianClock.now(dt)
        day_suffix = _ordinal(snap["day"])
        lines = [
            f"Today is {snap['day_name']}, day {snap['day']}{day_suffix} of the month "
            f"{snap['month_name']} in the year {snap['elanthian_year']}.",
            f"It is {snap['time_24']} by the elven time standard.",
            f"It is currently {snap['period']}.",
        ]
        holiday = snap.get("holiday")
        if holiday:
            lines.append(f"Today is {holiday}.")
        return "\n".join(lines)

    # ── CALENDAR sub-command tables ───────────────────────────────────────────

    @staticmethod
    def calendar_day_table() -> str:
        days = _CFG.get("days", _DEFAULTS["days"])
        mundane = ["Sunday", "Monday", "Tuesday", "Wednesday",
                   "Thursday", "Friday", "Saturday"]
        # weekday() 0=Mon, so map: Restday=Sun=6, Volnes=Mon=0, ...
        order = [6, 0, 1, 2, 3, 4, 5]   # Sun, Mon, Tue, Wed, Thu, Fri, Sat
        lines = ["Days of the Week:", ""]
        for i, weekday_idx in enumerate(order):
            el_name = days.get(weekday_idx, "")
            lines.append(f"   {el_name:<24} - {mundane[i]}")
        return "\n".join(lines)

    @staticmethod
    def calendar_month_table() -> str:
        months  = _CFG.get("months", _DEFAULTS["months"])
        mundane = ["", "January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"]
        lines = ["Months of the Year:", ""]
        for i in range(1, 13):
            lines.append(f"   {months.get(i, ''):<14} - {mundane[i]}")
        return "\n".join(lines)

    @staticmethod
    def calendar_time_table() -> str:
        return (
            "Hours of the Day:\n"
            "\n"
            "   Hour of Lumnis      - Dawn\n"
            "   Hour of Phoen       - Noon\n"
            "   Hour of Tonis       - Dusk\n"
            "   Hour of Ronan       - Midnight"
        )

    @staticmethod
    def calendar_holiday_table() -> str:
        holidays = _CFG.get("holidays", _DEFAULTS["holidays"])
        if isinstance(holidays, dict):
            holidays = list(holidays.values())
        months   = _CFG.get("months", _DEFAULTS["months"])
        lines    = ["Elanthian Holidays:", ""]
        seen     = set()
        for h in holidays:
            if not isinstance(h, dict):
                continue
            name = h.get("name", "")
            if name in seen:
                continue
            seen.add(name)
            m    = h.get("month", 0)
            d    = h.get("day", 0)
            mname = months.get(m, str(m))
            day_s = _ordinal(d)
            lines.append(f"   {name:<38} - {d}{day_s} of {mname}")
        return "\n".join(lines)

    @staticmethod
    def calendar_convert(year: int, month: int, day: int) -> str:
        try:
            dt       = datetime(year, month, day)
            snap     = ElanthianClock.now(dt)
            day_s    = _ordinal(snap["day"])
            holiday  = snap.get("holiday")
            result   = (
                f"{snap['day_name']}, the {snap['day']}{day_s} of "
                f"{snap['month_name']}, {snap['elanthian_year']} Modern Era."
            )
            if holiday:
                result += f"  ({holiday})"
            return result
        except Exception as e:
            return f"Invalid date: {e}"


def _ordinal(n: int) -> str:
    """Return ordinal suffix: 1→'st', 2→'nd', 3→'rd', 4→'th'."""
    if 11 <= (n % 100) <= 13:
        return "th"
    return {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
