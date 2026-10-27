"""The one internal shape every article is converted into.

Every source returns different JSON. Everything downstream of the mappers
(dedupe, relevance filter, classifier, database) only ever sees an Article,
so none of it needs to know which API an article came from.
"""

from pydantic import AwareDatetime, BaseModel, ConfigDict


class Article(BaseModel):
    # frozen=True: an Article can't be changed after it's built.
    # Pipeline stages produce new data instead of quietly editing old data.
    model_config = ConfigDict(frozen=True)

    source: str                      # which API: "alpaca" | "finnhub" | "alphavantage"
    source_id: str                   # that API's id for the article (used to avoid re-inserting it)
    publisher: str                   # who actually wrote it: "Benzinga", "Reuters", ...
    headline: str
    summary: str | None              # some articles have no summary
    url: str
    url_is_canonical: bool           # False for Finnhub, whose URLs are redirects
    published_at: AwareDatetime      # Pydantic rejects naive datetimes
    tickers: list[str]               # every ticker the source tagged, unfiltered
    ticker_relevance: dict[str, float] | None = None   # Alpha Vantage only
    vendor_sentiment: dict[str, float] | None = None   # Alpha Vantage only; comparison, never labels
