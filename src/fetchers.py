"""One function per source: call the API, return the raw article dicts.

Fetchers return raw JSON, not Articles. Mapping is a separate step, so the
raw responses can also be archived untouched (S3, later).
"""

import time
from datetime import datetime, timezone

import requests

from src.config import WATCHLIST, require_env
from src.http_client import get_json

MAX_PAGES = 100   # safety cap so a pagination bug can't loop forever


def _utc_rfc3339(dt: datetime) -> str:
    """2025-08-09T12:00:00Z -- the format Alpaca expects."""
    if dt.tzinfo is None:
        raise ValueError("datetime must be timezone-aware")
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# --- Alpaca ---

ALPACA_URL = "https://data.alpaca.markets/v1beta1/news"
ALPACA_PAGE_SIZE = 50   # Alpaca's maximum per request


def fetch_alpaca(session: requests.Session, start: datetime, end: datetime) -> list[dict]:
    headers = {
        "APCA-API-KEY-ID": require_env("ALPACA_KEY_ID"),
        "APCA-API-SECRET-KEY": require_env("ALPACA_SECRET_KEY"),
    }
    params = {
        "symbols": ",".join(WATCHLIST),   # all 12 tickers in one request
        "start": _utc_rfc3339(start),
        "end": _utc_rfc3339(end),
        "limit": ALPACA_PAGE_SIZE,
        "sort": "desc",
    }

    articles = []
    for _ in range(MAX_PAGES):
        data = get_json(session, ALPACA_URL, params=params, headers=headers)
        articles.extend(data["news"])
        token = data.get("next_page_token")
        if not token:
            return articles
        params["page_token"] = token   # ask for the next page

    raise RuntimeError(f"Alpaca returned more than {MAX_PAGES} pages; check the date range")


# --- Finnhub ---

FINNHUB_URL = "https://finnhub.io/api/v1/company-news"
FINNHUB_SECONDS_BETWEEN_CALLS = 1.1   # free tier: 60 calls/min


def fetch_finnhub(session: requests.Session, start: datetime, end: datetime) -> list[dict]:
    headers = {"X-Finnhub-Token": require_env("FINNHUB_KEY")}
    params = {
        "from": start.astimezone(timezone.utc).strftime("%Y-%m-%d"),   # Finnhub only takes dates
        "to": end.astimezone(timezone.utc).strftime("%Y-%m-%d"),
    }
    start_ts, end_ts = start.timestamp(), end.timestamp()

    by_id: dict[int, dict] = {}
    for ticker in WATCHLIST:                 # Finnhub: one ticker per request
        params["symbol"] = ticker
        for item in get_json(session, FINNHUB_URL, params=params, headers=headers):
            if not (start_ts <= item["datetime"] < end_ts):
                continue                     # dates are whole days; trim to the exact window
            existing = by_id.get(item["id"])
            if existing is None:
                by_id[item["id"]] = {**item, "related": ticker}
            elif ticker not in existing["related"].split(","):
                existing["related"] += f",{ticker}"   # same article, found under another ticker
        time.sleep(FINNHUB_SECONDS_BETWEEN_CALLS)

    return list(by_id.values())

