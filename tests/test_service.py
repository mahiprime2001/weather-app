"""Tests for the async client + service layer, with HTTP mocked via respx."""

from __future__ import annotations

import httpx
import pytest
import respx

from weather_app.client import FORECAST_URL, GEOCODE_URL, WeatherError
from weather_app.service import get_weather

from conftest import FORECAST, GEOCODE_EMPTY, GEOCODE_LONDON


@respx.mock
async def test_get_weather_builds_report():
    respx.get(GEOCODE_URL).mock(return_value=httpx.Response(200, json=GEOCODE_LONDON))
    respx.get(FORECAST_URL).mock(return_value=httpx.Response(200, json=FORECAST))

    report = await get_weather("London", days=2)

    assert report.location.name == "London"
    assert report.location.label == "London, England, United Kingdom"
    assert report.current.temperature == 12.3
    assert report.current.description == "Overcast"  # code 3
    assert len(report.daily) == 2
    assert report.daily[1].weather_code == 61
    assert report.daily[0].precipitation_probability == 10
    assert report.units == "metric"
    assert report.temp_symbol == "°C"


@respx.mock
async def test_unknown_city_raises():
    respx.get(GEOCODE_URL).mock(return_value=httpx.Response(200, json=GEOCODE_EMPTY))
    with pytest.raises(WeatherError, match="Could not find"):
        await get_weather("Nowheresville")


@respx.mock
async def test_http_error_raises_weather_error():
    respx.get(GEOCODE_URL).mock(return_value=httpx.Response(500))
    with pytest.raises(WeatherError, match="request failed"):
        await get_weather("London")


@respx.mock
async def test_forecast_request_uses_resolved_coordinates():
    geo_route = respx.get(GEOCODE_URL).mock(
        return_value=httpx.Response(200, json=GEOCODE_LONDON)
    )
    fc_route = respx.get(FORECAST_URL).mock(
        return_value=httpx.Response(200, json=FORECAST)
    )

    await get_weather("London", days=5)

    assert geo_route.called and fc_route.called
    sent = fc_route.calls.last.request
    assert sent.url.params["latitude"] == "51.5085"
    assert sent.url.params["forecast_days"] == "5"
    assert sent.url.params["temperature_unit"] == "celsius"


@respx.mock
async def test_imperial_units(monkeypatch):
    monkeypatch.setenv("WEATHER_UNITS", "imperial")
    respx.get(GEOCODE_URL).mock(return_value=httpx.Response(200, json=GEOCODE_LONDON))
    fc_route = respx.get(FORECAST_URL).mock(
        return_value=httpx.Response(200, json=FORECAST)
    )

    report = await get_weather("London", days=1)

    assert report.temp_symbol == "°F"
    assert fc_route.calls.last.request.url.params["temperature_unit"] == "fahrenheit"
