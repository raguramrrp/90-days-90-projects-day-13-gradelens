"""
GradeLens Core Academic Calculations Layer.
Implements robust mathematical, statistical, and ranking functions.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional


def safe_percentage(obtained: float, maximum: float) -> float:
    """Calculates percentage with zero-division safety and precision rounding."""
    if maximum is None or maximum <= 0 or obtained is None or obtained < 0:
        return 0.0
    val = (obtained * 100.0) / maximum
    return round(float(np.clip(val, 0.0, 100.0)), 2)


def calculate_subject_metrics(responses_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes comprehensive subject performance metrics from question responses:
    - total assessments
    - total marks obtained vs maximum marks
    - overall percentage
    - total marks lost
    - highest & lowest score
    - score consistency (standard deviation)
    """
    if responses_df.empty:
        return {
            "total_assessments": 0,
            "total_questions": 0,
            "total_obtained": 0.0,
            "total_possible": 0.0,
            "overall_percentage": 0.0,
            "total_marks_lost": 0.0,
            "highest_pct": 0.0,
            "lowest_pct": 0.0,
            "score_std_dev": 0.0,
            "consistency_rating": "Insufficient Data"
        }

    total_obtained = float(responses_df["marks_obtained"].sum())
    total_possible = float(responses_df["maximum_marks"].sum())
    overall_pct = safe_percentage(total_obtained, total_possible)
    marks_lost = round(total_possible - total_obtained, 2)

    # Group by exam to measure exam-level consistency
    exam_groups = responses_df.groupby("exam_id").apply(
        lambda g: safe_percentage(g["marks_obtained"].sum(), g["maximum_marks"].sum())
    )

    std_dev = round(float(exam_groups.std()), 2) if len(exam_groups) > 1 else 0.0
    highest = round(float(exam_groups.max()), 2) if not exam_groups.empty else 0.0
    lowest = round(float(exam_groups.min()), 2) if not exam_groups.empty else 0.0

    if len(exam_groups) < 2:
        consistency = "Insufficient History"
    elif std_dev <= 7.0:
        consistency = "High Consistency"
    elif std_dev <= 15.0:
        consistency = "Moderate Consistency"
    else:
        consistency = "High Fluctuation"

    return {
        "total_assessments": int(responses_df["exam_id"].nunique()),
        "total_questions": len(responses_df),
        "total_obtained": round(total_obtained, 2),
        "total_possible": round(total_possible, 2),
        "overall_percentage": overall_pct,
        "total_marks_lost": marks_lost,
        "highest_pct": highest,
        "lowest_pct": lowest,
        "score_std_dev": std_dev,
        "consistency_rating": consistency
    }


def calculate_difficulty_breakdown(responses_df: pd.DataFrame) -> pd.DataFrame:
    """Computes obtained marks, total marks, and accuracy percentage by difficulty level."""
    if responses_df.empty:
        return pd.DataFrame(columns=["difficulty", "obtained", "maximum", "marks_lost", "accuracy_pct"])

    grouped = responses_df.groupby("difficulty").agg(
        obtained=("marks_obtained", "sum"),
        maximum=("maximum_marks", "sum"),
        questions_count=("response_id", "count")
    ).reset_index()

    grouped["marks_lost"] = grouped["maximum"] - grouped["obtained"]
    grouped["accuracy_pct"] = grouped.apply(
        lambda row: safe_percentage(row["obtained"], row["maximum"]), axis=1
    )
    # Ensure standard order: Easy, Medium, Hard
    order = {"Easy": 1, "Medium": 2, "Hard": 3}
    grouped["sort_key"] = grouped["difficulty"].map(order).fillna(4)
    grouped = grouped.sort_values("sort_key").drop(columns=["sort_key"])
    return grouped


def calculate_student_ranking(attempts_df: pd.DataFrame, anonymize: bool = False) -> pd.DataFrame:
    """
    Computes class ranking using aggregate weighted percentage.
    Correctly handles ties using standard dense ranking.
    """
    if attempts_df.empty:
        return pd.DataFrame(columns=["rank", "student_id", "student_name", "total_obtained", "total_marks", "percentage"])

    grouped = attempts_df.groupby(["student_id", "student_name"]).agg(
        total_obtained=("marks_obtained", "sum"),
        total_marks=("total_marks", "sum"),
        exams_count=("exam_id", "count")
    ).reset_index()

    grouped["percentage"] = grouped.apply(
        lambda r: safe_percentage(r["total_obtained"], r["total_marks"]), axis=1
    )

    # Sort descending by percentage, then by total_obtained
    grouped = grouped.sort_values(by=["percentage", "total_obtained"], ascending=[False, False]).reset_index(drop=True)
    grouped["rank"] = grouped["percentage"].rank(method="min", ascending=False).astype(int)

    if anonymize:
        grouped["display_name"] = grouped.apply(lambda r: f"Student #{r['rank']}", axis=1)
    else:
        grouped["display_name"] = grouped["student_name"]

    return grouped[["rank", "student_id", "student_name", "display_name", "exams_count", "total_obtained", "total_marks", "percentage"]]
