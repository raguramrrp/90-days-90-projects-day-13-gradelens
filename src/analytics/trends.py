"""
GradeLens Performance Trend Intelligence Layer.
Calculates historical score trajectories, mistake clustering, and assessment comparisons.
"""

import pandas as pd
from typing import Dict, Any, List, Optional
from src.analytics.calculations import safe_percentage


def compute_exam_progression(attempts_df: pd.DataFrame) -> pd.DataFrame:
    """Computes exam-to-exam score progression chronologically."""
    if attempts_df.empty:
        return pd.DataFrame(columns=["exam_date", "exam_name", "marks_obtained", "total_marks", "percentage", "delta_pct"])

    df = attempts_df.sort_values("exam_date").copy()
    df["percentage"] = df.apply(lambda r: safe_percentage(r["marks_obtained"], r["total_marks"]), axis=1)
    df["delta_pct"] = df["percentage"].diff().fillna(0.0).round(2)
    return df[["exam_date", "exam_name", "marks_obtained", "total_marks", "percentage", "delta_pct"]]


def compute_mistake_distribution(responses_df: pd.DataFrame) -> pd.DataFrame:
    """Computes the distribution and percentage contribution of each recorded mistake category."""
    if responses_df.empty:
        return pd.DataFrame(columns=["mistake_category", "occurrences", "marks_lost", "percentage_of_losses"])

    # Filter out 'None' or empty
    filtered = responses_df[
        responses_df["mistake_category"].notna() & 
        (responses_df["mistake_category"] != "None") &
        (responses_df["marks_lost"] > 0)
    ]
    if filtered.empty:
        return pd.DataFrame(columns=["mistake_category", "occurrences", "marks_lost", "percentage_of_losses"])

    grouped = filtered.groupby("mistake_category").agg(
        occurrences=("response_id", "count"),
        marks_lost=("marks_lost", "sum")
    ).reset_index()

    total_lost = grouped["marks_lost"].sum()
    grouped["percentage_of_losses"] = grouped["marks_lost"].apply(
        lambda lost: safe_percentage(lost, total_lost)
    )
    return grouped.sort_values(by="marks_lost", ascending=False)


def compute_confidence_calibration(responses_df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyzes student metacognitive accuracy by comparing confidence ratings
    against actual answer status.
    Identifies 'Blind Spots' (High Confidence + Incorrect).
    """
    if responses_df.empty or "confidence_rating" not in responses_df.columns:
        return pd.DataFrame(columns=["confidence_rating", "total_questions", "correct_count", "incorrect_count", "accuracy_pct"])

    filtered = responses_df[responses_df["confidence_rating"].notna() & (responses_df["confidence_rating"] != "None")]
    if filtered.empty:
        return pd.DataFrame(columns=["confidence_rating", "total_questions", "correct_count", "incorrect_count", "accuracy_pct"])

    grouped = filtered.groupby("confidence_rating").agg(
        total_questions=("response_id", "count"),
        correct_count=("answer_status", lambda s: (s == "Correct").sum()),
        incorrect_count=("answer_status", lambda s: (s.isin(["Incorrect", "Partially Correct", "Unanswered"])).sum())
    ).reset_index()

    grouped["accuracy_pct"] = grouped.apply(
        lambda r: safe_percentage(r["correct_count"], r["total_questions"]), axis=1
    )

    order = {"Low": 1, "Medium": 2, "High": 3}
    grouped["sort_order"] = grouped["confidence_rating"].map(order).fillna(4)
    return grouped.sort_values("sort_order").drop(columns=["sort_order"])
