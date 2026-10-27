"""One function per source: raw API dict in, Article out.

Mappers only translate. They don't filter, dedupe, or judge relevance --
each of those is its own pipeline stage, so each can be tested and measured
on its own.
"""

import html

from src.models import Article
from src.timestamps import (
    alpaca_timezone_normalizer,
    finnhub_timezone_normalizer,
)


def _clean_text(raw: str | None) -> str | None:
    """Decode HTML entities (&#39; -> ') and turn blank strings into None."""
    if raw is None:
        return None
    text = html.unescape(raw).strip()
    return text or None


def _clean_tickers(raw: list[str]) -> list[str]:
    """Uppercase, strip, drop empties, remove duplicates, keep order."""
    seen = []
    for t in raw:
        t = t.strip().upper()
        if t and t not in seen:
            seen.append(t)
    return seen


def from_alpaca(raw: dict) -> Article:
    return Article(
        source="alpaca",
        source_id=str(raw["id"]),
        publisher=raw["source"].capitalize(),        # "benzinga" -> "Benzinga"
        headline=_clean_text(raw["headline"]),
        summary=_clean_text(raw.get("summary")),
        url=raw["url"],
        url_is_canonical=True,
        published_at=alpaca_timezone_normalizer(raw["created_at"]),
        tickers=_clean_tickers(raw["symbols"]),
    )


def from_finnhub(raw: dict) -> Article:
    return Article(
        source="finnhub",
        source_id=str(raw["id"]),
        publisher=raw["source"],
        headline=_clean_text(raw["headline"]),
        summary=_clean_text(raw.get("summary")),
        url=raw["url"],
        url_is_canonical=False,                     # finnhub.io/api/news?id=... redirect
        published_at=finnhub_timezone_normalizer(raw["datetime"]),
        tickers=_clean_tickers(raw["related"].split(",")),   # a string, not a list
    )

