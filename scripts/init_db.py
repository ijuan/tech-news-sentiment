"""Create the database tables.  Run from the repo root:  python -m scripts.init_db"""

from src.db import connect, init_schema


def main() -> None:
    with connect() as conn:
        init_schema(conn)
        tables = conn.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public' ORDER BY table_name"
        ).fetchall()
    print("Tables:", [t[0] for t in tables])


if __name__ == "__main__":
    main()
