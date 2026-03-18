"""Generate narrative insights from analytics results.

This module is designed to be a lightweight wrapper around an LLM (OpenAI).
If an API key is not present, it will fall back to simple template-based summaries.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import pandas as pd

from config import config


def _build_prompt(question: str, data: List[Dict[str, Any]], context: Dict[str, Any]) -> str:
    """Build the prompt to send to the LLM.

    This prompt is intentionally simple and directly exposes the data and question.
    It avoids any external template dependency so the LLM can reason over the raw
    dataset and business question.
    """

    # Provide a compact representation of the data (first N rows) so the prompt remains manageable.
    preview_rows = data[:10]

    return (
        "You are a data analytics assistant.\n"
        "I will provide you with a business question and a small sample of the query results.\n"
        "Provide a short, clear insight that answers the question based on the data.\n\n"
        f"Business question: {question}\n\n"
        f"Data sample (first {len(preview_rows)} rows):\n{preview_rows}\n\n"
        f"Additional context: {context}\n\n"
        "Give the insight in 2-3 sentences."
    )


def _fallback_summary(question: str, data: List[Dict[str, Any]], context: Dict[str, Any]) -> str:
    """Generate a simple, deterministic summary without an LLM."""

    df = pd.DataFrame(data)

    if question.lower().startswith("how fast") or "growth" in question.lower():
        if "year_added" not in df or "titles_added" not in df:
            return "Insufficient data to compute growth metrics."

        latest = df.sort_values("year_added").iloc[-1]
        rate = latest.get("growth_rate")
        trend = "accelerating" if rate is not None and rate > 0 else "decelerating"

        return (
            f"Library growth: {int(latest['titles_added']):,} items added in {int(latest['year_added'])}. "
            f"Growth rate was {rate if rate is not None else 'N/A'}%. Growth is {trend}."
        )

    if "emerging" in question.lower() and "genre" in question.lower():
        if "primary_genre" not in df or "current_titles" not in df or "prior_titles" not in df:
            return "Insufficient trend data to assess emerging genres."

        df = df.copy()
        df["growth_pct"] = ((df["current_titles"] - df["prior_titles"]) / df["prior_titles"].replace(0, 1)).fillna(0)
        rising = df.sort_values("growth_pct", ascending=False).head(3)
        rising_list = ", ".join(
            f"{r['primary_genre']} (+{r['growth_pct'] * 100:.1f}%)" for _, r in rising.iterrows()
        )
        return f"Top emerging genres: {rising_list}."

    if question.lower().startswith("which genres") or "genre" in question.lower():
        if "primary_genre" not in df or "titles" not in df:
            return "Insufficient genre data to summarize."

        top = df.nlargest(3, "titles")
        total = df["titles"].sum()
        top_list = ", ".join(
            f"{r['primary_genre']} ({r['titles']})" for _, r in top.iterrows()
        )
        top_pct = top["titles"].sum() / total * 100 if total > 0 else 0
        return (
            f"Top genres: {top_list}. These account for {top_pct:.1f}% of the catalog by count."
        )

    if question.lower().startswith("which countries"):
        if "primary_country" not in df or "titles" not in df:
            return "Insufficient country data to summarize."

        top = df.nlargest(3, "titles")
        total = df["titles"].sum()
        top_list = ", ".join(
            f"{r['primary_country']} ({r['titles']})" for _, r in top.iterrows()
        )
        return (
            f"Top producing countries: {top_list}. Together they represent {top['titles'].sum() / total * 100:.1f}% of the catalog."
        )

    if "older content" in question.lower() or "age" in question.lower():
        if "age" not in df or "pct_of_catalog" not in df:
            return "Insufficient age distribution data."

        older_pct = df[df["age"] >= 10]["pct_of_catalog"].sum()
        return (
            f"{older_pct:.1f}% of the catalog is 10+ years old, indicating the platform relies on a substantial amount of older content."
        )

    return f"Summary (no LLM): {len(data)} rows of data. Context: {context}."


def _llm_call(prompt: str, question: str, data: List[Dict[str, Any]], context: Dict[str, Any]) -> str:
    """Call OpenAI if configured, otherwise use a fallback summary."""

    if not config.openai_api_key:
        return _fallback_summary(question, data, context)

    try:
        import openai

        # OpenAI >= 1.0 uses `OpenAI()` client; older versions use ChatCompletion directly.
        if hasattr(openai, "OpenAI"):
            client = openai.OpenAI(api_key=config.openai_api_key)
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a data analytics assistant."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=450,
                temperature=0.2,
            )
            return resp.choices[0].message["content"].strip()

        # Fallback for openai < 1.0
        openai.api_key = config.openai_api_key
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a data analytics assistant."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=450,
            temperature=0.2,
        )
        return resp.choices[0].message.content.strip()

    except Exception as e:
        return _fallback_summary(question, data, {**context, "error": str(e)})


def generate_insights(
    *,
    question: str,
    data: List[Dict[str, Any]],
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Generate insights for a given business question and query results."""

    context = context or {}
    prompt = _build_prompt(question, data, context)
    insight_text = _llm_call(prompt, question, data, context)

    return {
        "question": question,
        "prompt": prompt,
        "insight": insight_text,
        "data": data,
        "context": context,
    }
