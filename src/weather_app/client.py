"""Async HTTP client for the Open-Meteo geocoding and forecast APIs.

The client only deals with transport and caching: it fetches raw JSON and
hands it back. Turning that into domain models is the service layer's job.
Open-Meteo requires no API key.
"""

from __future__ import annotations

from typing import Any, Optional

import httpx

from .cache import TTLCache
from .config import Settings

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

CURRENT_FIELDS = [
    "temperature_2m",
    "relative_humidity_2m",
    "apparent_temperature",
    "precipitation",
    "weather_code",
    "wind_speed_10m",
    "is_day",
]
DAILY_FIELDS = [
    "weather_code",
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_probability_max",
]


class WeatherError(Exception):
    """Raised when a city can't be found or the API call fails."""


class WeatherClient:
    def __init__(
        self,
        settings: Settings,
        *,
        client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        self.settings = settings
        self.cache = TTLCache(settings.cache_dir, settings.cache_ttl)
        # Allow injecting a client (handy for tests); otherwise own one.
        self._client = client
        self._owns_client = client is None

    async def __aenter__(self) -> "WeatherClient":
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=10.0)
        return self

    async def __aexit__(self, *exc: object) -> None:
        if self._owns_client and self._client is not None:
            await self._client.aclose()

    @property
    def http(self) -> httpx.AsyncClient:
        if self._client is None:
            raise RuntimeError("Use WeatherClient inside 'async with'.")
        return self._client

    async def _get_json(self, url: str, params: dict[str, Any], cache_key: str) -> Any:
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached
        try:
            response = await self.http.get(url, params=params)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise WeatherError(f"Weather service request failed: {exc}") from exc
        data = response.json()
        self.cache.set(cache_key, data)
        return data

    async def geocode(self, city: str) -> dict[str, Any]:
        """Resolve a city name to its first matching location record."""
        params = {"name": city, "count": 1, "language": "en", "format": "json"}
        data = await self._get_json(GEOCODE_URL, params, f"geocode:{city.lower()}")
        results = data.get("results") or []
        if not results:
            raise WeatherError(f"Could not find a place called {city!r}.")
        return results[0]

    async def forecast(self, latitude: float, longitude: float, days: int) -> dict[str, Any]:
        """Fetch current conditions plus a multi-day daily forecast."""
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": ",".join(CURRENT_FIELDS),
            "daily": ",".join(DAILY_FIELDS),
            "timezone": "auto",
            "forecast_days": days,
            "temperature_unit": self.settings.temperature_unit,
            "wind_speed_unit": self.settings.wind_speed_unit,
        }
        key = f"forecast:{latitude},{longitude}:{days}:{self.settings.units}"
        return await self._get_json(FORECAST_URL, params, key)
