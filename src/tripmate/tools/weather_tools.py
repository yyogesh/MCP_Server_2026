"""Weather tools: daily forecasts from Open-Meteo via tripmate.clients.weather."""

from typing import Any

from mcp.server.mcpserver import Context
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import BaseModel, Field

from tripmate.clients import AppContext, get_http
from tripmate.clients.weather import City, DayForecast, find_city, get_daily_forecast

MIN_DAYS = 1
MAX_DAYS = 7


class Forecast(BaseModel):
    """A daily weather forecast for one city."""

    city: City = Field(description="The city the forecast is for, as found by name lookup.")
    days: list[DayForecast] = Field(description="One entry per day, starting today in the city's local time.")


async def get_forecast(city: str, ctx: Context[AppContext, Any], days: int = 3) -> Forecast:
    """Get the daily weather forecast for a city for the next 1 to 7 days.

    Use this when the user asks about the weather at a destination, or what to
    pack for a trip starting within the next week. Forecasts only reach 7 days
    ahead, so for trips further out say the forecast is not available yet.

    Args:
        city: The city name only, preferably in English, e.g. "Tokyo" or "Munich".
            Do not add a country or region; the best-known match for the name is
            used, and the result shows which country was picked.
        days: How many days to forecast, starting today: a whole number from 1 to 7.
            Defaults to 3.

    Returns the matched city (name, country, coordinates, time zone) and, for
    each day: the date (YYYY-MM-DD), max and min temperature in °C, the highest
    chance of rain in percent, and a short description such as "Light rain".
    """
    if not MIN_DAYS <= days <= MAX_DAYS:
        raise ToolError(f"days must be between {MIN_DAYS} and {MAX_DAYS}, got {days}.")
    name = city.strip()
    if not name:
        raise ToolError('city must not be empty. Give a city name, e.g. "Tokyo".')

    http = get_http(ctx)
    found = await find_city(http, name)
    return Forecast(city=found, days=await get_daily_forecast(http, found, days))
