"""Example pipeline: Pareto genre report + AI insight generation."""

from __future__ import annotations

from typing import Any, Dict

from ai_insights.generate_insights import generate_insights
from ai_insights.query_runner import run_query


PARETO_GENRE_SQL = """\
SELECT primary_genre,
       COUNT(*) AS content_count,
       AVG(release_year) AS avg_release_year
FROM netflix_content
GROUP BY primary_genre
ORDER BY content_count DESC
LIMIT 50;
"""


def run() -> Dict[str, Any]:
    """Run the Pareto-genre pipeline and return insight output."""

    df = run_query(PARETO_GENRE_SQL)

    result = generate_insights(
        data=df.head(20).to_dict(orient="records"),
        prompt_key="pareto_genre",
        context={
            "row_count": len(df),
            "sample_genres": ", ".join(str(g) for g in df["primary_genre"].head(5)),
        },
    )

    return result


if __name__ == "__main__":
    output = run()
    print(output["insight"])
