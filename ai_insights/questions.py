"""Business question handler for the analytics pipeline.

This module maps high-level business questions (like "Which genres are emerging?")
into SQL queries and AI prompt templates. It is the entry point for turning a
question into an answer.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import json
import pandas as pd

from config import config
from ai_insights.generate_insights import generate_insights
from ai_insights.query_runner import run_query


QUESTION_CATALOG_PATH = Path(__file__).parent / "questions.json"


@dataclass(frozen=True)
class BusinessQuestion:
    key: str
    description: str
    sql_file: str
    prompt_key: str


def _load_question_catalog() -> List[BusinessQuestion]:
    """Load business questions from the catalog file."""

    if not QUESTION_CATALOG_PATH.exists():
        raise FileNotFoundError(f"Question catalog not found: {QUESTION_CATALOG_PATH}")

    raw = json.loads(QUESTION_CATALOG_PATH.read_text())
    return [BusinessQuestion(**q) for q in raw]


def _find_question(key: str, questions: List[BusinessQuestion]) -> BusinessQuestion:
    for q in questions:
        if q.key == key:
            return q
    raise KeyError(f"Unknown business question key: {key}")


def _load_sql_file(name: str) -> str:
    """Load SQL text from the project sql/ directory."""

    sql_path = config.sql_dir / f"{name}.sql"
    if not sql_path.exists():
        raise FileNotFoundError(f"SQL file not found: {sql_path}")

    return sql_path.read_text()


def _clean_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Make query results JSON-safe by converting NaN/NA values to None."""

    def clean_value(value: Any) -> Any:
        if pd.isna(value):
            return None
        return value

    return [{k: clean_value(v) for k, v in row.items()} for row in rows]


def list_question_keys() -> List[str]:
    """Return available question keys in the catalog."""

    return [q.key for q in _load_question_catalog()]


def answer_question(question_key: str) -> Dict[str, Any]:
    """Answer a predefined business question.

    This returns a dictionary containing the query results, the generated insight,
    and the prompt used.
    """

    question = _find_question(question_key, _load_question_catalog())
    sql_text = _load_sql_file(question.sql_file)

    df = run_query(sql_text)
    rows = _clean_rows(df.to_dict(orient="records"))

    context = {
        "question": question.description,
        "row_count": len(rows),
    }

    result = generate_insights(
        question=question.description,
        data=rows,
        context=context,
        prompt_key=question.prompt_key,
    )

    return {
        "question_key": question.key,
        "description": question.description,
        "data": rows,
        "insight": result["insight"],
        "prompt": result["prompt"],
        "context": result["context"],
    }


def answer_all_questions() -> Dict[str, Dict[str, Any]]:
    """Run all predefined business questions and return the results."""

    results: Dict[str, Dict[str, Any]] = {}
    for q in _load_question_catalog():
        try:
            results[q.key] = answer_question(q.key)
        except Exception as e:
            # Fail-safe: store the error and continue with remaining questions
            results[q.key] = {
                "question_key": q.key,
                "description": q.description,
                "error": str(e),
                "data": [],
                "insight": None,
                "prompt": None,
                "context": {},
            }
    return results


