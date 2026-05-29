"""Service layer: orchestrate geocoding + forecast into a WeatherReport.

This is the single entry point used by both the CLI and the web API, so the
two interfaces always behave identically.
"""

from __future__ import annotations

from typing import Any, Optional

import httpx

from .client import WeatherClient
from .config import Settings, get_settings
from .models import (
    CurrentWeather,
    DailyForecast,
    Location,
    WeatherReport,
)


def _build_location(raw: dict[str, Any]) -> Location:
    return Location(
        name=raw["name"],
        country=raw.get("country"),
        admin1=raw.get("admin1"),
        latitude=raw["latitude"],
        longitude=raw["longitude"],
        timezone=raw.get("timezone"),
    )


def _build_current(raw: dict[str, Any]) -> CurrentWeather:
    cur = raw["current"]
    return CurrentWeather(
        temperature=cur["temperature_2m"],
        apparent_temperature=cur["apparent_temperature"],
        humidity=cur["relative_humidity_2m"],
        precipitation=cur["precipitation"],
        wind_speed=cur["wind_speed_10m"],
        is_day=bool(cur["is_day"]),
        weather_code=cur["weather_code"],
    )


def _build_daily(raw: dict[str, Any]) -> list[DailyForecast]:
    daily = raw["daily"]
    days = []
    for i, date in enumerate(daily["time"]):
        probs = daily.get("precipitation_probability_max") or []
        days.append(
            DailyForecast(
                date=date,
                weather_code=daily["weather_code"][i],
                temp_max=daily["temperature_2m_max"][i],
                temp_min=daily["temperature_2m_min"][i],
                precipitation_probability=probs[i] if i < len(probs) else None,
            )
        )
    return days


async def get_weather(
    city: str,
    *,
    days: int = 5,
    settings: Optional[Settings] = None,
    http_client: Optional[httpx.AsyncClient] = None,
) -> WeatherReport:
    """Resolve ``city`` and return its current weather plus a daily forecast."""
    settings = settings or get_settings()
    async with WeatherClient(settings, client=http_client) as client:
        place = await client.geocode(city)
        location = _build_location(place)
        raw = await client.forecast(location.latitude, location.longitude, days)

    return WeatherReport(
        location=location,
        current=_build_current(raw),
        daily=_build_daily(raw),
        units=settings.units,
        temp_symbol=settings.temp_symbol,
        wind_symbol=settings.wind_symbol,
    )
