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

-- One row per fetch of one source. The daily job starts from the last successful window_end.
CREATE TABLE IF NOT EXISTS ingestion_runs (
    id                 BIGSERIAL PRIMARY KEY,
    source             TEXT        NOT NULL CHECK (source IN ('alpaca', 'finnhub')),
    window_start       TIMESTAMPTZ NOT NULL,
    window_end         TIMESTAMPTZ NOT NULL,
    status             TEXT        NOT NULL CHECK (status IN ('running', 'succeeded', 'failed')),
    started_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at        TIMESTAMPTZ,
    articles_fetched   INTEGER,
    articles_inserted  INTEGER,
    error              TEXT,
    CHECK (window_start < window_end)
);

CREATE INDEX IF NOT EXISTS ingestion_runs_lookup_idx ON ingestion_runs (source, status, window_end);
