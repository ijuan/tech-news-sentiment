"""Project-wide settings: API keys and the watchlist."""

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")   # locally: read .env. On AWS there's no .env; real env vars are used.

WATCHLIST = [
    "NVDA", "AAPL", "MSFT", "AMZN", "GOOGL", "AVGO",
    "META", "TSLA", "MU", "AMD", "PLTR", "INTC",
]


def require_env(name: str) -> str:
    """Return an environment variable, or fail loudly if it's missing."""
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing environment variable {name}. Is it set in .env?")
    return value
