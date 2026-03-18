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

from ai_insights.questions import answer_all_questions


OUTPUT_DIR = Path(__file__).parent / "outputs"
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
        lines.append(data["insight"])
        lines.append("")
        lines.append("**Sample data (first 5 rows):**")
        lines.append("")
        lines.append("```")
        for row in data["data"][:5]:
            lines.append(str(row))
        lines.append("```")
        lines.append("")

    md_path.write_text("\n".join(lines))

    print(f"\nSaved insights to: {json_path}")
    print(f"Saved readable report to: {md_path}\n")


def main() -> None:
    results = answer_all_questions()

    for key, data in results.items():
        print("\n" + "=" * 80)
        print(f"QUESTION: {data['description']}")
        print("-> Generated insight:\n")
        print(data["insight"])
        print("\n-> Sample data returned (first 5 rows):")
        for row in data["data"][:5]:
            print(row)

    _write_report(results, OUTPUT_DIR)


if __name__ == "__main__":
    main()
