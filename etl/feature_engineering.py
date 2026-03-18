"""Feature engineering utilities for analytics."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd


def feature_engineer(df: pd.DataFrame) -> pd.DataFrame:
    """Apply feature engineering transformations to the input dataframe."""

    df = df.copy()

    # Standardize columns
    if "cast" in df.columns and "casts" not in df.columns:
        df = df.rename(columns={"cast": "casts"})

    # Missing categorical values are common in streaming metadata
    df = df.fillna({"director": "Unknown", "casts": "Unknown", "country": "Unknown"})

    # Convert dates and fill missing
    if "date_added" in df.columns:
        df["date_added"] = pd.to_datetime(df["date_added"], errors="coerce")
        df["date_added"] = df["date_added"].fillna(df["date_added"].median())
        df["year_added"] = df["date_added"].dt.year.astype("Int64")
        df["month_added"] = df["date_added"].dt.month.astype("Int64")

    # Content age is useful for trend analysis
    if "release_year" in df.columns:
        current_year = pd.Timestamp.now().year
        df["content_age"] = current_year - df["release_year"]

    # Extract primary genre and country for easier grouping
    if "listed_in" in df.columns:
        df["primary_genre"] = df["listed_in"].str.split(",").str[0]

    if "country" in df.columns:
        df["primary_country"] = df["country"].str.split(",").str[0]

    # Duration parsing (movie runtime or TV seasons)
    if "duration" in df.columns:
        df["duration_minutes"] = df["duration"].str.extract(r"(\d+)")
        df["duration_minutes"] = pd.to_numeric(df["duration_minutes"], errors="coerce").astype("Int64")

    # Binary indicator for movies
    if "type" in df.columns:
        df["is_movie"] = (df["type"] == "Movie")

    # Additional columns as per test expectations
    if "listed_in" in df.columns:
        df["genre_list"] = df["listed_in"].str.split(",").str.strip()
        df["main_genre"] = df["primary_genre"]  # alias

    if "country" in df.columns:
        df["country_list"] = df["country"].str.split(",").str.strip()
        df["main_country"] = df["primary_country"]  # alias

    if "type" in df.columns:
        df["is_tv_show"] = (df["type"] == "TV Show")

    if "duration" in df.columns and "type" in df.columns:
        # seasons_count for TV shows
        df["seasons_count"] = df.apply(lambda row: int(row["duration_minutes"]) if row["type"] == "TV Show" else None, axis=1).astype("Int64")

    if "date_added" in df.columns:
        df["date_added_parsed"] = df["date_added"]
        df["days_since_added"] = (pd.Timestamp.now() - df["date_added"]).dt.days.astype("Int64")

    return df


def run_feature_engineering(
    input_path: Path, output_path: Path, overwrite: bool = True
) -> pd.DataFrame:
    """Run feature engineering from a CSV file and write the result.

    This function is intended to be used by production scripts.
    """

    df = pd.read_csv(input_path)
    df = feature_engineer(df)

    if overwrite or not output_path.exists():
        df.to_csv(output_path, index=False)

    return df
