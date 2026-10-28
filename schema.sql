-- Database schema. Safe to re-run: every statement uses IF NOT EXISTS.

-- One row per article, from any source.
CREATE TABLE IF NOT EXISTS articles (
    id                BIGSERIAL PRIMARY KEY,
    source            TEXT        NOT NULL CHECK (source IN ('alpaca', 'finnhub')),
    source_id         TEXT        NOT NULL,
    publisher         TEXT        NOT NULL,
    headline          TEXT        NOT NULL,
    summary           TEXT,
    url               TEXT        NOT NULL,
    url_is_canonical  BOOLEAN     NOT NULL,
    published_at      TIMESTAMPTZ NOT NULL,
    ingested_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (source, source_id)
);

CREATE INDEX IF NOT EXISTS articles_published_at_idx ON articles (published_at);

-- One row per (article, ticker) pair. An article tagged AAPL and MSFT gets two rows.
CREATE TABLE IF NOT EXISTS article_tickers (
    article_id  BIGINT NOT NULL REFERENCES articles (id) ON DELETE CASCADE,
    ticker      TEXT   NOT NULL,
    PRIMARY KEY (article_id, ticker)
);

CREATE INDEX IF NOT EXISTS article_tickers_ticker_idx ON article_tickers (ticker);
