"""Simple SQL runner for the analytics pipeline.

This module is responsible for running SQL against the cleansed dataset.
It supports running against a real database (via DB_URL) or using an in-memory
SQLite database loaded from the processed CSV.

The goal is to make the `ai_insights` layer independent of whether there is a
Postgres instance available; it should work locally using the processed CSV.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd
from sqlalchemy.engine import Engine
from sqlalchemy import create_engine

from config import config


def _get_sqlite_connection(processed_csv: Optional[Path] = None) -> sqlite3.Connection:
    """Create an in-memory SQLite DB and load the processed dataset."""

    if processed_csv is None:
        processed_csv = config.processed_data_dir / "netflix_featured.csv"

    conn = sqlite3.connect(":memory:")
    df = pd.read_csv(processed_csv)
    df.to_sql("netflix_content", conn, index=False, if_exists="replace")
    return conn


def _get_engine() -> Engine:
    """Get a SQLAlchemy engine for running queries.

    If a DB_URL is configured, use it. Otherwise fall back to an in-memory
    SQLite engine loaded from the processed CSV.
    """

    if config.db_url:
        return create_engine(config.db_url)

    # Use SQLite in-memory database when DB_URL is not provided.
    # SQLAlchemy can still work with a SQLite connection string.
    return create_engine("sqlite://")


def run_query(sql: str, params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    """Run a SQL query and return the results as a DataFrame."""

    # If we have a real DB, run directly.
    if config.db_url:
        engine = _get_engine()
        return pd.read_sql_query(sql, engine, params=params)

    # Otherwise, load the processed CSV into an in-memory SQLite DB.
    conn = _get_sqlite_connection()
    try:
        df = pd.read_sql_query(sql, conn, params=params)
    finally:
        conn.close()

    return df
