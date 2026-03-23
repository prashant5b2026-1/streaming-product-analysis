"""Run the business-question-to-insight pipeline.

This script demonstrates how to turn a business question into a query, run the
query, and generate an insight response.

Usage:
    python -m ai_insights.run_questions
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import argparse

from config import config
from ai_insights.questions import answer_all_questions, answer_question, list_question_keys


OUTPUT_DIR = config.output_dir
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)


def _write_report(results: dict[str, dict], out_dir: Path) -> None:
    """Write a summary report to disk for audit and review."""

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    json_path = out_dir / f"insights_report_{timestamp}.json"
    md_path = out_dir / f"insights_report_{timestamp}.md"

    # Save raw JSON for downstream tooling
    json_path.write_text(json.dumps(results, indent=2))

    # Save readable markdown report
    lines = ["# AI Insights Report", ""]
    lines.append(f"Generated: {timestamp} UTC")
    lines.append("")

    for key, data in results.items():
        lines.append(f"## {data['description']}")
        lines.append("")
        lines.append("**Insight:**")
        lines.append("")
        lines.append(data.get("insight", "(no insight returned)"))
        lines.append("")
        lines.append("**Sample data (first 5 rows):**")
        lines.append("")
        lines.append("```")
        for row in data.get("data", [])[:5]:
            lines.append(str(row))
        lines.append("```")
        lines.append("")

    md_path.write_text("\n".join(lines))

    print(f"\nSaved insights to: {json_path}")
    print(f"Saved readable report to: {md_path}\n")


def run_insights(
    questions: list[str] | None = None,
    out_dir: Path | None = None,
) -> dict[str, dict]:
    """Run one or all business questions and write a report.

    This is the programmatic entrypoint used by the pipeline.

    Parameters
    ----------
    questions:
        List of question keys to run. If None, all questions will be executed.
    """

    out_dir = out_dir or config.output_dir
    out_dir.mkdir(exist_ok=True, parents=True)

    if questions:
        results: dict[str, dict] = {}
        for q in questions:
            results[q] = answer_question(q)
    else:
        results = answer_all_questions()

    _write_report(results, out_dir)
    return results


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run AI insights for predefined business questions."
    )
    parser.add_argument(
        "--question",
        nargs="*",
        type=str,
        help=(
            "Specific question key(s) to execute (e.g., content_age). "
            "If omitted, all questions will be executed."
        ),
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available question keys and exit.",
    )
    args = parser.parse_args()

    if args.list:
        print("Available question keys:")
        for key in sorted(list_question_keys()):
            print(f"  - {key}")
        return

    # Empty list (e.g., --question with no values) should behave like omitted.
    questions = args.question if args.question else None

    results = run_insights(questions=questions, out_dir=OUTPUT_DIR)

    for key, data in results.items():
        print("\n" + "=" * 80)
        print(f"QUESTION: {data.get('description', key)}")

        if data.get("error"):
            print("-> Error:")
            print(data["error"])
            continue

        print("-> Generated insight:\n")
        print(data.get("insight"))
        print("\n-> Sample data returned (first 5 rows):")
        for row in data.get("data", [])[:5]:
            print(row)


if __name__ == "__main__":
    main()
