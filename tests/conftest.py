"""Shared test fixtures and sample API payloads (no network is ever hit)."""

from __future__ import annotations

import pytest

# A realistic geocoding response for "London".
GEOCODE_LONDON = {
    "results": [
        {
            "name": "London",
            "country": "United Kingdom",
            "admin1": "England",
            "latitude": 51.5085,
            "longitude": -0.1257,
            "timezone": "Europe/London",
        }
    ]
}

# An empty geocoding response (city not found).
GEOCODE_EMPTY: dict = {"generationtime_ms": 0.1}

# A realistic forecast response with current conditions and two days.
FORECAST = {
    "current": {
        "temperature_2m": 12.3,
        "relative_humidity_2m": 80,
        "apparent_temperature": 10.1,
        "precipitation": 0.0,
        "weather_code": 3,
        "wind_speed_10m": 15.0,
        "is_day": 1,
    },
    "daily": {
        "time": ["2026-05-29", "2026-05-30"],
        "weather_code": [3, 61],
        "temperature_2m_max": [15.0, 14.0],
        "temperature_2m_min": [8.0, 9.0],
        "precipitation_probability_max": [10, 60],
    },
}


@pytest.fixture(autouse=True)
def isolated_settings(tmp_path, monkeypatch):
    """Disable the cache and isolate config from any local .env for each test."""
    monkeypatch.setenv("WEATHER_CACHE_TTL", "0")
    monkeypatch.setenv("WEATHER_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("WEATHER_UNITS", "metric")
    monkeypatch.setenv("WEATHER_DEFAULT_CITY", "London")
