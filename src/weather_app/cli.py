"""Command-line interface for weather-app, built with Typer + Rich."""

from __future__ import annotations

import asyncio
import sys
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .client import WeatherError

# Prefer UTF-8 so weather emojis don't crash legacy Windows consoles (cp1252).
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except (AttributeError, ValueError):
        pass
from .config import get_settings
from .models import WeatherReport
from .service import get_weather

app = typer.Typer(
    help="Live weather from the free Open-Meteo API.",
    no_args_is_help=True,
    add_completion=False,
)
console = Console()
err_console = Console(stderr=True)


def _fetch(city: Optional[str], days: int) -> WeatherReport:
    """Resolve the city (falling back to config) and fetch weather, or exit."""
    settings = get_settings()
    target = city or settings.default_city
    try:
        return asyncio.run(get_weather(target, days=days, settings=settings))
    except WeatherError as exc:
        err_console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1)


def _current_panel(report: WeatherReport) -> Panel:
    c = report.current
    lines = [
        f"{c.emoji}  [bold]{c.description}[/bold]",
        "",
        f"Temperature : [bold]{c.temperature:.0f}{report.temp_symbol}[/bold] "
        f"(feels like {c.apparent_temperature:.0f}{report.temp_symbol})",
        f"Humidity    : {c.humidity}%",
        f"Wind        : {c.wind_speed:.0f} {report.wind_symbol}",
        f"Precip.     : {c.precipitation} mm",
    ]
    return Panel(
        "\n".join(lines),
        title=f"Now in {report.location.label}",
        border_style="cyan",
        expand=False,
    )


@app.command()
def now(
    city: Optional[str] = typer.Argument(None, help="City name (defaults to config)."),
) -> None:
    """Show current conditions for a city."""
    report = _fetch(city, days=1)
    console.print(_current_panel(report))


@app.command()
def forecast(
    city: Optional[str] = typer.Argument(None, help="City name (defaults to config)."),
    days: int = typer.Option(5, "--days", "-d", min=1, max=16, help="Days to show."),
) -> None:
    """Show current conditions plus a multi-day forecast."""
    report = _fetch(city, days=days)
    console.print(_current_panel(report))

    table = Table(title=f"{days}-day forecast · {report.location.label}")
    table.add_column("Date", style="cyan")
    table.add_column("", justify="center")
    table.add_column("Conditions")
    table.add_column(f"High ({report.temp_symbol})", justify="right", style="red")
    table.add_column(f"Low ({report.temp_symbol})", justify="right", style="blue")
    table.add_column("Rain %", justify="right")
    for d in report.daily:
        prob = "" if d.precipitation_probability is None else f"{d.precipitation_probability}%"
        table.add_row(
            d.date,
            d.emoji,
            d.description,
            f"{d.temp_max:.0f}",
            f"{d.temp_min:.0f}",
            prob,
        )
    console.print(table)


@app.command()
def config() -> None:
    """Show the current configuration (units, default city, cache settings)."""
    s = get_settings()
    table = Table(title="Configuration", show_header=False)
    table.add_column("Setting", style="cyan")
    table.add_column("Value")
    table.add_row("Units", s.units)
    table.add_row("Default city", s.default_city)
    table.add_row("Cache TTL (s)", str(s.cache_ttl))
    table.add_row("Cache dir", str(s.cache_dir))
    table.add_row("API key set", "yes" if s.api_key else "no")
    console.print(table)


@app.command()
def serve(
    host: str = typer.Option("127.0.0.1", "--host", help="Address to bind."),
    port: int = typer.Option(8000, "--port", help="Port to listen on."),
) -> None:
    """Launch the web UI."""
    from .web.app import run

    console.print(f"[green]Serving the weather web UI at[/green] http://{host}:{port}")
    console.print("[dim]Press Ctrl+C to stop.[/dim]")
    run(host=host, port=port)


if __name__ == "__main__":
    app()
