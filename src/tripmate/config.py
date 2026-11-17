"""TripMate settings, read from environment variables prefixed with TRIPMATE_.

Example: TRIPMATE_HTTP_TIMEOUT=5 overrides http_timeout.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Base URLs and HTTP options for the public web APIs TripMate calls."""

    model_config = SettingsConfigDict(env_prefix="TRIPMATE_")

    geocoding_url: str = "https://geocoding-api.open-meteo.com/v1/search"
    forecast_url: str = "https://api.open-meteo.com/v1/forecast"
    currency_url: str = "https://api.frankfurter.dev/v1"
    http_timeout: float = 10.0  # seconds


settings = Settings()
