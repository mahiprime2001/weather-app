"""Convenience entry point so you can run the app directly.

Examples:
    python main.py now London
    python main.py forecast "New York" --days 7
    uv run main.py serve

It hands control to the Typer app defined in src/weather_app/cli.py.
"""

from __future__ import annotations

import os
import sys

# Make `src/` importable when running this file directly, without installing.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from weather_app.cli import app  # noqa: E402

if __name__ == "__main__":
    app()
