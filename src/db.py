"""Database connection and schema setup."""

import psycopg

from src.config import PROJECT_ROOT, require_env
from src.models import Article

SCHEMA_PATH = PROJECT_ROOT / "schema.sql"


def connect() -> psycopg.Connection:
    """Open a connection using DATABASE_URL (local Docker now, RDS later)."""
    return psycopg.connect(require_env("DATABASE_URL"))


def init_schema(conn: psycopg.Connection) -> None:
    """Create every table in schema.sql. Safe to run repeatedly (IF NOT EXISTS)."""
    conn.execute(SCHEMA_PATH.read_text())
    conn.commit()


INSERT_ARTICLE = """
    INSERT INTO articles (source, source_id, publisher, headline, summary,
                          url, url_is_canonical, published_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (source, source_id) DO NOTHING
    RETURNING id
"""

INSERT_TICKER = "INSERT INTO article_tickers (article_id, ticker) VALUES (%s, %s)"


def save_articles(conn: psycopg.Connection, articles: list[Article]) -> int:
    """Insert articles and their tickers, skipping duplicates. Returns how many were new.

    Does not commit -- the caller decides when the whole run is committed.
    """
    inserted = 0
    with conn.cursor() as cur:
        for a in articles:
            cur.execute(INSERT_ARTICLE, (
                a.source, a.source_id, a.publisher, a.headline, a.summary,
                a.url, a.url_is_canonical, a.published_at,
            ))
            row = cur.fetchone()
            if row is None:
                continue                      # already stored: ON CONFLICT skipped it
            article_id = row[0]
            cur.executemany(INSERT_TICKER, [(article_id, t) for t in a.tickers])
            inserted += 1
    return inserted
