"""Prompt templates used for generating AI insights."""

from __future__ import annotations

from typing import Dict

PROMPT_TEMPLATES: Dict[str, str] = {
    "growth_over_time": (
        "You are an analytics assistant.\n"
        "Given the following yearly growth metrics for the content library (year and total_count), "
        "provide a short summary of how quickly the library is growing and whether growth is accelerating.\n"
        "Data:\n{data}\n"
        "Context: {context}\n"
    ),

    "dominant_genres": (
        "You are an analytics assistant.\n"
        "Given the following genre market share data (genre and count), "
        "provide a short summary of which genres dominate the catalog and any notable patterns.\n"
        "Data:\n{data}\n"
        "Context: {context}\n"
    ),

    "emerging_genres": (
        "You are an analytics assistant.\n"
        "Given the following recent growth metrics for genres (genre, current_period_count, previous_period_count), "
        "provide a short summary identifying emerging genres and their growth rates.\n"
        "Data:\n{data}\n"
        "Context: {context}\n"
    ),

    "country_production": (
        "You are an analytics assistant.\n"
        "Given the following content production data by country (country and count), "
        "provide a short summary of which countries produce the most content and any regional patterns.\n"
        "Data:\n{data}\n"
        "Context: {context}\n"
    ),

    "content_age": (
        "You are an analytics assistant.\n"
        "Given the following distribution of content age (age, count, percentage), "
        "provide a short summary of whether the platform relies heavily on older content.\n"
        "Data:\n{data}\n"
        "Context: {context}\n"
    ),

    # A generic fallback template
    "generic": (
        "You are an analytics assistant.\n"
        "Here is the data you need to summarize:\n{data}\n"
        "Context: {context}\n"
    ),
}
