"""Async client for the free Open-Meteo geocoding and forecast APIs (no API key).

Every function takes the shared httpx.AsyncClient from the server lifespan
(see tripmate.clients.get_http) and returns Pydantic models, never raw JSON.
Network problems become ToolError with a short message for the model.
"""

import datetime as dt
import logging

import httpx
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import BaseModel, Field, ValidationError

from tripmate.clients import get_json
from tripmate.config import settings

logger = logging.getLogger(__name__)

# WMO weather interpretation codes, as used by Open-Meteo.
WMO_CODES: dict[int, str] = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Freezing fog",
    51: "Light drizzle",
    53: "Drizzle",
    55: "Heavy drizzle",
    56: "Light freezing drizzle",
    57: "Freezing drizzle",
    61: "Light rain",
    63: "Rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Freezing rain",
    71: "Light snow",
    73: "Snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "Light rain showers",
    81: "Rain showers",
    82: "Violent rain showers",
    85: "Light snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with light hail",
    99: "Thunderstorm with heavy hail",
}


class City(BaseModel):
    """A place found by the geocoding API."""

    name: str = Field(description='The city name in English, e.g. "Tokyo".')
    country: str = Field(default="", description='The country name, e.g. "Japan". May be empty.')
    latitude: float = Field(description="Latitude in decimal degrees.")
    longitude: float = Field(description="Longitude in decimal degrees.")
    timezone: str = Field(description='The IANA time zone, e.g. "Asia/Tokyo".')


class DayForecast(BaseModel):
    """The forecast for one day at a city, in the city's local time zone."""

    date: dt.date = Field(description="The day, in YYYY-MM-DD format.")
    temp_max_c: float | None = Field(description="Highest temperature in °C, or null if unknown.")
    temp_min_c: float | None = Field(description="Lowest temperature in °C, or null if unknown.")
    rain_chance_percent: int | None = Field(
        description="Highest chance of precipitation that day, 0-100, or null if unknown."
    )
    conditions: str = Field(description='Short weather description, e.g. "Light rain", or "Unknown".')


def describe_weather_code(code: int | None) -> str:
    """Turn a WMO weather code into short English text."""
    if code is None:
        return "Unknown"
    return WMO_CODES.get(code, "Unknown")


async def find_city(http: httpx.AsyncClient, name: str) -> City:
    """Look up a city by name and return the best match."""
    data = await get_json(
        http,
        settings.geocoding_url,
        {"name": name, "count": 1, "language": "en", "format": "json"},
        "geocoding",
    )
    results = data.get("results") if isinstance(data, dict) else None
    if not results:
        raise ToolError(f'City "{name}" was not found. Try the English city name, e.g. "Munich" not "München".')
    try:
        return City.model_validate(results[0])
    except ValidationError:
        raise ToolError(f'The geocoding service sent incomplete data for "{name}".') from None


async def get_daily_forecast(http: httpx.AsyncClient, city: City, days: int) -> list[DayForecast]:
    """Get the daily forecast for a city, for the next `days` days starting today."""
    data = await get_json(
        http,
        settings.forecast_url,
        {
            "latitude": city.latitude,
            "longitude": city.longitude,
            "timezone": "auto",
            "forecast_days": days,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,weather_code",
        },
        "weather forecast",
    )
    try:
        daily = data["daily"]
        rows = zip(
            daily["time"],
            daily["temperature_2m_max"],
            daily["temperature_2m_min"],
            daily["precipitation_probability_max"],
            daily["weather_code"],
            strict=True,
        )
        return [
            DayForecast(
                date=day,
                temp_max_c=t_max,
                temp_min_c=t_min,
                rain_chance_percent=rain,
                conditions=describe_weather_code(code),
            )
            for day, t_max, t_min, rain, code in rows
        ]
    except (KeyError, TypeError, ValueError):
        logger.warning("Unexpected forecast response: %r", data)
        raise ToolError("The weather forecast service sent unexpected data.") from None
