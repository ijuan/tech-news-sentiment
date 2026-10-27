"""Live check: fetch the last 24 hours from each source and map it into Articles.

Run from the repo root:  python -m scripts.smoke_test
"""

from collections import Counter
from datetime import datetime, timedelta, timezone

from src.fetchers import fetch_alpaca, fetch_finnhub
from src.http_client import build_session
from src.mappers import from_alpaca, from_finnhub

SOURCES = [
    ("alpaca", fetch_alpaca, from_alpaca),
    ("finnhub", fetch_finnhub, from_finnhub),
]


def main() -> None:
    session = build_session()
    end = datetime.now(timezone.utc)
    start = end - timedelta(hours=24)

    for name, fetch, to_article in SOURCES:
        raw = fetch(session, start, end)
        articles = [to_article(item) for item in raw]
        publishers = Counter(a.publisher for a in articles).most_common(3)
        print(f"{name:13} {len(articles):4} articles   top publishers: {publishers}")
        if articles:
            print(f"{'':13} newest: {articles[0].published_at:%Y-%m-%d %H:%M} UTC  {articles[0].headline[:70]}")


if __name__ == "__main__":
    main()
