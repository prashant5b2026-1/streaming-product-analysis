"""Run the full analytics pipeline end to end.

1) Feature engineering
2) SQL analytics
3) Exported report artifacts
4) AI-generated narrative insights

The goal is to make the project runnable with a single command and to produce
outputs that reviewers can inspect without running notebooks.

Usage:
    python run_pipeline.py

Requirements:
- `DB_URL` environment variable (Postgres) for SQL analytics.
- `OPENAI_API_KEY` environment variable for AI-generated insights (optional).

This script is intentionally simple: it uses pandas + SQLAlchemy for the data
pipeline, and it uses the same SQL files under `sql/` that an analyst would
run in a BI tool.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Dict

import pandas as pd
from sqlalchemy import create_engine, text

from ai_insights.run_questions import run_insights
from config import config
from etl.data_quality import data_quality_report, save_report
from etl.feature_engineering import run_feature_engineering


# Set up logging based on config
logging.basicConfig(
    level=getattr(logging, config.log_level.upper(), logging.INFO),
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(config.output_dir / "pipeline.log", mode="w"),
    ],
)
logger = logging.getLogger(__name__)


def _ensure_directories() -> None:
    """Ensure required directories exist."""
    config.raw_data_dir.mkdir(parents=True, exist_ok=True)
    config.processed_data_dir.mkdir(parents=True, exist_ok=True)
    config.output_dir.mkdir(parents=True, exist_ok=True)


def _feature_engineer() -> Path:
    """Load raw data, run feature engineering, and save a processed CSV."""

    raw = config.raw_data_dir / "netflix_titles.csv"
    out = config.processed_data_dir / "netflix_featured.csv"

    logger.info(f"[1/5] Running feature engineering: {raw}")

    try:
        run_feature_engineering(raw, out, overwrite=config.overwrite_outputs)
        logger.info(f"    -> Feature-engineered dataset written to: {out}")
        return out
    except Exception as e:
        logger.error(f"Feature engineering failed: {e}")
        raise


def _save_data_quality_report(processed_csv: Path) -> None:
    """Generate a data-quality report and save it to outputs."""

    logger.info("[2/5] Generating data quality report...")

    try:
        df = pd.read_csv(processed_csv)
        report = data_quality_report(df)

        out_path = config.output_dir / "data_quality_report.json"
        save_report(report, out_path)
        logger.info(f"    -> Data quality report written to: {out_path}")
    except Exception as e:
        logger.error(f"Data quality report failed: {e}")
        raise


def _load_to_postgres(processed_csv: Path) -> None:
    """Load the processed CSV into Postgres (table: netflix_content)."""

    if not config.db_url:
        logger.warning("[3/5] Skipping Postgres load (DB_URL not set).")
        return

    logger.info("[3/5] Loading processed dataset into Postgres (netflix_content)...")

    try:
        engine = create_engine(config.db_url)
        df = pd.read_csv(processed_csv)

        # Replace existing table to keep analytics reproducible.
        df.to_sql("netflix_content", engine, if_exists="replace", index=False)
        logger.info("    -> Loaded table: netflix_content")
    except Exception as e:
        logger.error(f"Postgres load failed: {e}")
        raise


def _run_sql_reports() -> Dict[str, Path]:
    """Run all SQL files in sql/ and export results to CSV."""

    if not config.db_url:
        logger.warning("[4/5] Skipping SQL reports (DB_URL not set).")
        return {}

    logger.info("[4/5] Running SQL reports...")

    try:
        engine = create_engine(config.db_url)
        results: Dict[str, Path] = {}

        for sql_file in sorted(config.sql_dir.glob("*.sql")):
            name = sql_file.stem
            logger.info(f"    - Running {sql_file.name}...")

            sql_text = sql_file.read_text()

            # Check if this is a SELECT query or DDL
            if "SELECT" in sql_text.upper():
                # This contains SELECT, try to read results
                df = pd.read_sql(sql_text, engine)
                out_path = config.output_dir / f"{name}.csv"
                df.to_csv(out_path, index=False)
                results[name] = out_path
                logger.info(f"      -> Saved {out_path}")
            else:
                # This is DDL (CREATE, INSERT, etc.), just execute it
                with engine.connect() as conn:
                    conn.execute(text(sql_text))
                    conn.commit()
                logger.info(f"      -> Executed DDL statement")

        return results
    except Exception as e:
        logger.error(f"SQL reports failed: {e}")
        raise


def _generate_ai_insights() -> None:
    """Run the AI insights pipeline for all predefined business questions."""

    logger.info("[5/5] Generating AI insights (questions + narrative summaries)...")

    try:
        results = run_insights(out_dir=config.output_dir)
        logger.info("    -> AI insights generated and saved.")

        # Log a sample insight to make it easy to validate quickly
        sample = next(
            (
                data.get("insight")
                for data in results.values()
                if data.get("insight")
            ),
            None,
        )
        if sample:
            logger.info(f"    -> Sample: {sample[:140]}...")
    except Exception as e:
        logger.error(f"AI insights failed: {e}")
        raise


def main() -> None:
    logger.info("Starting analytics pipeline...")
    _ensure_directories()
    processed = _feature_engineer()
    _save_data_quality_report(processed)
    _load_to_postgres(processed)
    _run_sql_reports()
    _generate_ai_insights()
    logger.info("Pipeline completed successfully.")


if __name__ == "__main__":
    main()
