"""Configuration for the analytics pipeline.

This file centralizes settings that can vary between environments (dev, prod, etc.).
In production, this might be managed by a tool like AWS Parameter Store or Kubernetes ConfigMaps.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Any

from dotenv import load_dotenv
from pydantic import BaseModel, Field


# Load environment variables from .env file
load_dotenv()


class PipelineConfig(BaseModel):
    """Configuration for the analytics pipeline."""

    # Data paths
    raw_data_dir: Path = Field(default_factory=lambda: Path(__file__).parent / "data" / "raw")
    processed_data_dir: Path = Field(default_factory=lambda: Path(__file__).parent / "data" / "processed")
    output_dir: Path = Field(default_factory=lambda: Path(__file__).parent / "ai_insights" / "outputs")
    sql_dir: Path = Field(default_factory=lambda: Path(__file__).parent / "sql")

    # Database and API settings
    db_url: str | None = Field(default_factory=lambda: os.environ.get("DB_URL"))
    openai_api_key: str | None = Field(default_factory=lambda: os.environ.get("OPENAI_API_KEY"))

    # Feature engineering options
    overwrite_outputs: bool = True

    # Logging level (DEBUG, INFO, WARNING, ERROR)
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> PipelineConfig:
        """Load config from environment variables."""
        return cls()


# Global config instance
config = PipelineConfig.from_env()
