# weather-app

Live weather and forecasts from the free [Open-Meteo](https://open-meteo.com/) API — with both a **CLI** ([Typer](https://typer.tiangolo.com/) + [Rich](https://rich.readthedocs.io/)) and a **web UI** ([FastAPI](https://fastapi.tiangolo.com/) + a vanilla HTML/CSS/JS frontend). Managed with [uv](https://docs.astral.sh/uv/).

This is project #2 in a series of Python projects, progressing from basic to advanced. **No API key or signup required.**

## What this project demonstrates

- **Async HTTP** with `httpx` against real external REST APIs
- Geocoding a city name, then fetching its forecast
- Mapping [WMO weather codes](https://open-meteo.com/en/docs) to descriptions + emoji
- A **TTL response cache** so repeated lookups are instant and kind to the API
- **Configuration via `.env`** using `pydantic-settings`
- **Mocking HTTP in tests** with `respx` — the suite runs fully offline
- A clean layering (`config → cache → client → service → cli/web`) reused by both interfaces

## Install & run

Requires [uv](https://docs.astral.sh/uv/getting-started/installation/).

```bash
git clone https://github.com/mahiprime2001/weather-app.git
cd weather-app
uv sync
uv run weather now London
```

## CLI usage

```bash
weather now                       # current weather for the default city
weather now "New York"            # current weather for a city
weather forecast Tokyo            # current + 5-day forecast
weather forecast Berlin -d 10     # 10-day forecast
weather config                    # show active settings
weather serve                     # launch the web UI
```

## Web UI

```bash
uv run weather serve              # via the CLI (--host / --port)
uv run weather-web                # standalone entry point
```

Then open <http://127.0.0.1:8000>, type a city, and pick how many forecast days
to show. Interactive API docs are at <http://127.0.0.1:8000/docs>.

The web layer exposes one endpoint:

| Method | Path | Query |
|--------|------|-------|
| `GET`  | `/api/weather` | `city` (required), `days` (1–16, default 5) |

## Configuration

Copy `.env.example` to `.env` and adjust (all values optional):

| Variable | Default | Meaning |
|----------|---------|---------|
| `WEATHER_UNITS` | `metric` | `metric` (°C, km/h) or `imperial` (°F, mph) |
| `WEATHER_DEFAULT_CITY` | `London` | City used when none is given |
| `WEATHER_CACHE_TTL` | `600` | Seconds to reuse a cached response (`0` disables) |
| `WEATHER_CACHE_DIR` | `~/.weather-app/cache` | Where cached responses live |
| `WEATHER_API_KEY` | — | Unused by Open-Meteo; slot for a keyed provider |

## Development

```bash
uv sync                  # install runtime + dev dependencies
uv run pytest            # run the test suite (14 tests, no network needed)
```

## Project layout

```
weather-app/
├── pyproject.toml           # metadata, deps, entry points
├── main.py                  # run the CLI without installing
├── .env.example             # copy to .env to configure
├── src/weather_app/
│   ├── config.py            # pydantic-settings (.env / env vars)
│   ├── models.py            # typed models + WMO code mapping
│   ├── cache.py             # file-based TTL cache
│   ├── client.py            # async httpx client (geocoding + forecast)
│   ├── service.py           # orchestration: city -> WeatherReport
│   ├── cli.py               # Typer commands
│   └── web/
│       ├── app.py           # FastAPI app
│       └── static/          # index.html, style.css, app.js
└── tests/                   # respx-mocked tests (models, cache, service, web)
```

## License

MIT

Weather data by [Open-Meteo](https://open-meteo.com/) (CC BY 4.0).
