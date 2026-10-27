"""Mappers are tested against real API responses saved during source testing."""

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
from pydantic import ValidationError

from src.mappers import from_alpaca, from_finnhub
from src.models import Article

FIXTURES = Path(__file__).parent / "fixtures"


def load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


# --- Alpaca ---

def test_alpaca_maps_core_fields():
    a = from_alpaca(load("alpaca_article.json"))
    assert a.source == "alpaca"
    assert a.publisher == "Benzinga"
    assert a.url_is_canonical is True
    assert a.published_at == datetime(2025, 8, 9, 5, 4, 8, tzinfo=timezone.utc)
    assert a.tickers == ["AAPL", "GOOG", "GOOGL", "MSFT", "NVDA"]


def test_alpaca_decodes_html_entities():
    a = from_alpaca(load("alpaca_article.json"))
    assert "&#39;" not in a.summary
    assert "Apple's" in a.summary


def test_alpaca_blank_summary_becomes_none():
    raw = load("alpaca_article.json") | {"summary": " "}
    assert from_alpaca(raw).summary is None


# --- Finnhub ---

def test_finnhub_maps_core_fields():
    a = from_finnhub(load("finnhub_article.json"))
    assert a.source == "finnhub"
    assert a.publisher == "Yahoo"
    assert a.url_is_canonical is False
    assert a.tickers == ["AAPL"]
    assert a.published_at.tzinfo is not None


def test_finnhub_splits_comma_separated_related():
    raw = load("finnhub_article.json") | {"related": "AAPL,msft, NVDA"}
    assert from_finnhub(raw).tickers == ["AAPL", "MSFT", "NVDA"]


# --- Contract shared by all sources ---

@pytest.mark.parametrize(
    "mapper, fixture",
    [
        (from_alpaca, "alpaca_article.json"),
        (from_finnhub, "finnhub_article.json"),
    ],
)
def test_every_mapper_returns_aware_utc_article(mapper, fixture):
    a = mapper(load(fixture))
    assert isinstance(a, Article)
    assert a.published_at.utcoffset().total_seconds() == 0


def test_article_rejects_naive_datetime():
    with pytest.raises(ValidationError):
        Article(
            source="x", source_id="1", publisher="p", headline="h", summary=None,
            url="u", url_is_canonical=True, tickers=[],
            published_at=datetime(2025, 1, 1),   # no timezone
        )


def test_missing_required_key_raises():
    raw = load("alpaca_article.json")
    del raw["headline"]
    with pytest.raises(KeyError):
        from_alpaca(raw)
