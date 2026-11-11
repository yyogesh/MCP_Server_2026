"""Time and date helpers for trip planning.

These are plain functions; the server module registers them as MCP tools.
"""

from datetime import date, datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from mcp.server.mcpserver.exceptions import ToolError


def local_time(timezone: str) -> str:
    """Get the current local date and time in a given timezone.

    Use this to find out what time it is right now at a travel destination,
    for example before suggesting when to call a hotel or whether shops are open.

    Args:
        timezone: An IANA timezone name in "Area/Location" form, such as
            "Asia/Tokyo", "Europe/Paris" or "America/New_York". Also accepts
            "UTC". City names alone ("Tokyo"), abbreviations ("JST", "PST")
            and UTC offsets ("+09:00") are not accepted.

    Returns:
        The local date and time as an ISO 8601 string with the UTC offset,
        for example "2026-11-11T21:30:00+09:00".
    """
    try:
        tz = ZoneInfo(timezone.strip())
    except (ZoneInfoNotFoundError, ValueError):
        raise ToolError(
            f"Unknown timezone {timezone!r}. Use an IANA name such as "
            "'Asia/Tokyo' or 'Europe/London'."
        ) from None
    return datetime.now(tz).isoformat(timespec="seconds")


def trip_days(start_date: date, end_date: date) -> int:
    """Count the days in a trip, including both the first and the last day.

    A trip from 2026-12-01 to 2026-12-03 is 3 days. A trip that starts and
    ends on the same day is 1 day.

    Args:
        start_date: The first day of the trip, in ISO format "YYYY-MM-DD".
        end_date: The last day of the trip, in ISO format "YYYY-MM-DD".
            Must be on or after start_date.

    Returns:
        The number of days in the trip, as a whole number (at least 1).
    """
    if end_date < start_date:
        raise ToolError(
            f"end_date {end_date.isoformat()} is before start_date "
            f"{start_date.isoformat()}. Swap them or check the dates."
        )
    return (end_date - start_date).days + 1
