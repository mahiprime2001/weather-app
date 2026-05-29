"""Domain models and the WMO weather-code lookup.

These are plain pydantic models that the client builds from raw API JSON, so
the rest of the app (CLI, web, tests) works with tidy typed objects instead of
loosely-shaped dicts.
"""

from __future__ import annotations

from pydantic import BaseModel

# Open-Meteo reports conditions as WMO weather interpretation codes. Map each
# to a human description and an emoji for nicer output.
# https://open-meteo.com/en/docs (WMO Weather interpretation codes)
WMO_CODES: dict[int, tuple[str, str]] = {
    0: ("Clear sky", "☀️"),
    1: ("Mainly clear", "🌤️"),
    2: ("Partly cloudy", "⛅"),
    3: ("Overcast", "☁️"),
    45: ("Fog", "🌫️"),
    48: ("Depositing rime fog", "🌫️"),
    51: ("Light drizzle", "🌦️"),
    53: ("Moderate drizzle", "🌦️"),
    55: ("Dense drizzle", "🌧️"),
    56: ("Light freezing drizzle", "🌧️"),
    57: ("Dense freezing drizzle", "🌧️"),
    61: ("Slight rain", "🌦️"),
    63: ("Moderate rain", "🌧️"),
    65: ("Heavy rain", "🌧️"),
    66: ("Light freezing rain", "🌧️"),
    67: ("Heavy freezing rain", "🌧️"),
    71: ("Slight snow", "🌨️"),
    73: ("Moderate snow", "🌨️"),
    75: ("Heavy snow", "❄️"),
    77: ("Snow grains", "🌨️"),
    80: ("Slight rain showers", "🌦️"),
    81: ("Moderate rain showers", "🌧️"),
    82: ("Violent rain showers", "⛈️"),
    85: ("Slight snow showers", "🌨️"),
    86: ("Heavy snow showers", "❄️"),
    95: ("Thunderstorm", "⛈️"),
    96: ("Thunderstorm with slight hail", "⛈️"),
    99: ("Thunderstorm with heavy hail", "⛈️"),
}


def describe_code(code: int) -> tuple[str, str]:
    """Return (description, emoji) for a WMO weather code."""
    return WMO_CODES.get(code, ("Unknown", "❓"))


class Location(BaseModel):
    """A resolved place from the geocoding API."""

    name: str
    country: str | None = None
    admin1: str | None = None  # state/region
    latitude: float
    longitude: float
    timezone: str | None = None

    @property
    def label(self) -> str:
        parts = [self.name]
        if self.admin1:
            parts.append(self.admin1)
        if self.country:
            parts.append(self.country)
        return ", ".join(parts)


class CurrentWeather(BaseModel):
    temperature: float
    apparent_temperature: float
    humidity: int
    precipitation: float
    wind_speed: float
    is_day: bool
    weather_code: int

    @property
    def description(self) -> str:
        return describe_code(self.weather_code)[0]

    @property
    def emoji(self) -> str:
        return describe_code(self.weather_code)[1]


class DailyForecast(BaseModel):
    date: str  # ISO date
    weather_code: int
    temp_max: float
    temp_min: float
    precipitation_probability: int | None = None

    @property
    def description(self) -> str:
        return describe_code(self.weather_code)[0]

    @property
    def emoji(self) -> str:
        return describe_code(self.weather_code)[1]


class WeatherReport(BaseModel):
    """The full result returned by the service layer."""

    location: Location
    current: CurrentWeather
    daily: list[DailyForecast]
    units: str  # "metric" | "imperial"
    temp_symbol: str
    wind_symbol: str
