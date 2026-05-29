"""API tests for the FastAPI web layer, with upstream HTTP mocked via respx."""

from __future__ import annotations

import httpx
import respx
from fastapi.testclient import TestClient

from weather_app.client import FORECAST_URL, GEOCODE_URL
from weather_app.web.app import app

from conftest import FORECAST, GEOCODE_EMPTY, GEOCODE_LONDON

client = TestClient(app)


def test_index_served():
    res = client.get("/")
    assert res.status_code == 200
    assert "weather" in res.text.lower()


@respx.mock
def test_weather_endpoint_returns_report():
    respx.get(GEOCODE_URL).mock(return_value=httpx.Response(200, json=GEOCODE_LONDON))
    respx.get(FORECAST_URL).mock(return_value=httpx.Response(200, json=FORECAST))

    res = client.get("/api/weather", params={"city": "London", "days": 2})
    assert res.status_code == 200
    body = res.json()
    assert body["location"]["name"] == "London"
    assert body["current"]["temperature"] == 12.3
    assert len(body["daily"]) == 2


@respx.mock
def test_weather_endpoint_unknown_city_404():
    respx.get(GEOCODE_URL).mock(return_value=httpx.Response(200, json=GEOCODE_EMPTY))
    res = client.get("/api/weather", params={"city": "Nowhere"})
    assert res.status_code == 404


def test_weather_endpoint_requires_city():
    res = client.get("/api/weather")
    assert res.status_code == 422  # missing required query param
