"""Dates, times, and the timezone rules that bite.

The single most important habit: **store and compute in UTC, convert only for
display**. A naive datetime (no tzinfo) is ambiguous — it could mean anything —
and comparing naive with aware raises.

`datetime.utcnow()` is a trap: it returns a *naive* datetime holding UTC time,
which then gets treated as local. Use `datetime.now(timezone.utc)`.

`zoneinfo` (3.9+) reads the IANA database, so DST transitions are handled
correctly. Arithmetic on aware datetimes is absolute-time arithmetic: adding
24 hours across a DST boundary is not the same as "the same clock time
tomorrow".
"""

from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo


def main() -> None:
    utc_now = datetime(2026, 3, 8, 9, 30, tzinfo=timezone.utc)  # fixed, for stable output
    print(f"UTC:      {utc_now.isoformat()}")

    ny = ZoneInfo("America/New_York")
    tokyo = ZoneInfo("Asia/Tokyo")
    print(f"New York: {utc_now.astimezone(ny).isoformat()}")
    print(f"Tokyo:    {utc_now.astimezone(tokyo).isoformat()}")

    naive = datetime(2026, 3, 8, 9, 30)
    print(f"naive is ambiguous: {naive}, tzinfo={naive.tzinfo}")
    try:
        naive < utc_now
    except TypeError as exc:
        print(f"TypeError: {exc}")

    # DST: on this date New York springs forward at 02:00 local.
    before = datetime(2026, 3, 8, 1, 30, tzinfo=ny)
    print(f"before DST: {before} (offset {before.utcoffset()})")
    after_absolute = before + timedelta(hours=1)
    print(f"+1 real hour: {after_absolute} (offset {after_absolute.utcoffset()})")
    print("  local clock jumped two hours: 02:00-02:59 does not exist that day")

    # Wall-clock arithmetic vs absolute arithmetic.
    day_later_absolute = before.astimezone(timezone.utc) + timedelta(days=1)
    print(f"+24h absolute -> {day_later_absolute.astimezone(ny)}")
    print(f"same wall clock next day -> {before.replace(day=9)}")

    # Parsing and formatting.
    parsed = datetime.fromisoformat("2026-07-22T15:04:05+00:00")
    print(f"fromisoformat: {parsed}, strftime: {parsed.strftime('%Y-%m-%d %H:%M %Z')}")
    print(f"strptime: {datetime.strptime('22/07/2026', '%d/%m/%Y').date()}")

    # timedelta arithmetic and dates.
    d1, d2 = date(2026, 1, 1), date(2026, 7, 22)
    delta = d2 - d1
    print(f"days between: {delta.days}, weeks {delta.days // 7}")
    print(f"timestamp round-trip: "
          f"{datetime.fromtimestamp(utc_now.timestamp(), timezone.utc) == utc_now}")

    print("rules: UTC in storage, aware datetimes everywhere, zoneinfo for display")


if __name__ == "__main__":
    main()
