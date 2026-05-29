"""FastAPI application exposing weather lookups over HTTP.

The single data endpoint wraps the same service layer the CLI uses, so the web
UI and the terminal always agree. A small static frontend is served at the root.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from ..client import WeatherError
from ..models import WeatherReport
from ..service import get_weather

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(title="weather-app", description="Live weather via Open-Meteo.")


@app.get("/api/weather", response_model=WeatherReport)
async def weather(
    city: str = Query(..., min_length=1, description="City name to look up."),
    days: int = Query(5, ge=1, le=16, description="Number of forecast days."),
) -> WeatherReport:
    try:
        return await get_weather(city, days=days)
    except WeatherError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def run(host: str = "127.0.0.1", port: int = 8000) -> None:
    """Launch the web server (used by the ``weather-web`` entry point)."""
    import uvicorn

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run()
