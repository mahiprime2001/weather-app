"""Application configuration, loaded from environment variables and a .env file.

Uses pydantic-settings so values can come from (in order of precedence):
real environment variables, then a local ``.env`` file, then the defaults here.
"""

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All tunable settings for the weather app."""

    model_config = SettingsConfigDict(
        env_prefix="WEATHER_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Units: "metric" (°C, km/h) or "imperial" (°F, mph).
    units: str = "metric"

    # Default city to use when none is supplied on the command line.
    default_city: str = "London"

    # How long (seconds) to reuse a cached API response before refetching.
    cache_ttl: int = 600

    # Where cached responses live. Defaults to ~/.weather-app/cache.
    cache_dir: Path = Path.home() / ".weather-app" / "cache"

    # Optional API key slot. Open-Meteo needs none, but this is here so you can
    # switch to a keyed provider without restructuring anything.
    api_key: str | None = None

    @property
    def temperature_unit(self) -> str:
        return "fahrenheit" if self.units == "imperial" else "celsius"

    @property
    def wind_speed_unit(self) -> str:
        return "mph" if self.units == "imperial" else "kmh"

    @property
    def temp_symbol(self) -> str:
        return "°F" if self.units == "imperial" else "°C"

    @property
    def wind_symbol(self) -> str:
        return "mph" if self.units == "imperial" else "km/h"


def get_settings() -> Settings:
    """Return a fresh Settings instance (re-reads env each call)."""
    return Settings()
