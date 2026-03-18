"""Business question handler for the analytics pipeline.

This module maps high-level business questions (like "Which genres are emerging?")
into SQL queries and AI prompt templates. It is the entry point for turning a
question into an answer.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from config import config
from ai_insights.generate_insights import generate_insights
from ai_insights.query_runner import run_query


def _load_sql_file(name: str) -> str:
    """Load SQL text from the project sql/ directory."""

    sql_path = config.sql_dir / f"{name}.sql"
    if not sql_path.exists():
        raise FileNotFoundError(f"SQL file not found: {sql_path}")

    return sql_path.read_text()


BUSINESS_QUESTIONS: Dict[str, Dict[str, Any]] = {
    "library_growth": {
        "description": "How fast is the content library growing?",
        "sql_file": "03_growth_analysis",
        "prompt_key": "growth_over_time",
    },
    "dominant_genres": {
        "description": "Which genres dominate the platform catalog?",
        "sql_file": "04_genre_market_share",
        "prompt_key": "dominant_genres",
    },
    "emerging_genres": {
        "description": "Which genres are emerging trends?",
        "sql_file": "09_genre_growth_recent",
        "prompt_key": "emerging_genres",
    },
    "country_production": {
        "description": "Which countries produce the most content?",
        "sql_file": "06_country_share_analysis",
        "prompt_key": "country_production",
    },
    "content_age": {
        "description": "Is the platform relying too heavily on older content?",
        "sql_file": "08_content_age_distribution",
        "prompt_key": "content_age",
    },
}


def answer_question(question_key: str) -> Dict[str, Any]:
    """Answer a predefined business question.

    This returns a dictionary containing the query results, the generated insight,
    and the prompt used.
    """

    if question_key not in BUSINESS_QUESTIONS:
        raise KeyError(f"Unknown business question key: {question_key}")

    question_config = BUSINESS_QUESTIONS[question_key]
    sql_text = _load_sql_file(question_config["sql_file"])

    df = run_query(sql_text)
    rows = df.to_dict(orient="records")

    context = {
        "question": question_config["description"],
        "row_count": len(rows),
    }

    result = generate_insights(
        question=question_config["description"],
        data=rows,
        context=context,
    )

    return {
        "question_key": question_key,
        "description": question_config["description"],
        "data": rows,
        "insight": result["insight"],
        "prompt": result["prompt"],
        "context": result["context"],
    }


def answer_all_questions() -> Dict[str, Dict[str, Any]]:
    """Run all predefined business questions and return the results."""

    results: Dict[str, Dict[str, Any]] = {}
    for key in BUSINESS_QUESTIONS:
        results[key] = answer_question(key)
    return results
