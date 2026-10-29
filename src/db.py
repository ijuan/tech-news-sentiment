"""Database connection and schema setup."""

import psycopg

from src.config import PROJECT_ROOT, require_env

SCHEMA_PATH = PROJECT_ROOT / "schema.sql"


def connect() -> psycopg.Connection:
    """Open a connection using DATABASE_URL (local Docker now, RDS later)."""
    return psycopg.connect(require_env("DATABASE_URL"))


def init_schema(conn: psycopg.Connection) -> None:
    """Create every table in schema.sql. Safe to run repeatedly (IF NOT EXISTS)."""
    conn.execute(SCHEMA_PATH.read_text())
    conn.commit()
