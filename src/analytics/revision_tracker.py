"""
GradeLens Revision Effectiveness Tracker.
Correlates recorded revision sessions with subsequent examination performance.
Maintains clear scientific integrity: presents observed comparisons without claiming causation.
"""

import pandas as pd
from typing import Dict, Any, List, Optional
from src.analytics.calculations import safe_percentage


def compute_revision_impact(responses_df: pd.DataFrame, revision_sessions_df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes before vs. after revision metrics for topics where both
    exam responses and revision sessions exist.
    """
    if responses_df.empty or revision_sessions_df.empty:
        return pd.DataFrame(columns=[
            "topic_id", "topic_name", "subject_name", "sessions_count", "total_revision_mins",
            "pre_revision_score", "post_revision_score", "score_delta", "observed_impact", "evidence_note"
        ])

    results = []

    # Filter to topics present in both datasets
    common_topics = set(responses_df["topic_id"]).intersection(set(revision_sessions_df["topic_id"]))

    for topic_id in common_topics:
        t_responses = responses_df[responses_df["topic_id"] == topic_id].sort_values("attempt_date")
        t_revisions = revision_sessions_df[revision_sessions_df["topic_id"] == topic_id].sort_values("revision_date")

        if t_responses.empty or t_revisions.empty:
            continue

        topic_name = t_responses["topic_name"].iloc[0]
        subject_name = t_responses["subject_name"].iloc[0] if "subject_name" in t_responses.columns else ""

        first_rev_date = t_revisions["revision_date"].min()
        last_rev_date = t_revisions["revision_date"].max()
        sessions_count = len(t_revisions)
        total_mins = int(t_revisions["duration_minutes"].sum())

        pre_responses = t_responses[t_responses["attempt_date"] <= first_rev_date]
        post_responses = t_responses[t_responses["attempt_date"] > first_rev_date]

        pre_score = (
            safe_percentage(pre_responses["marks_obtained"].sum(), pre_responses["maximum_marks"].sum())
            if not pre_responses.empty else None
        )
        post_score = (
            safe_percentage(post_responses["marks_obtained"].sum(), post_responses["maximum_marks"].sum())
            if not post_responses.empty else None
        )

        if pre_score is not None and post_score is not None:
            delta = round(post_score - pre_score, 2)
            if delta >= 10.0:
                impact = "Significant Gain"
            elif delta > 0.0:
                impact = "Moderate Gain"
            elif delta == 0.0:
                impact = "Neutral"
            else:
                impact = "Score Decline"

            note = (
                f"Across {sessions_count} revision session(s) ({total_mins} mins total), "
                f"observed score changed from {pre_score:.1f}% ({len(pre_responses)} Qs) to {post_score:.1f}% ({len(post_responses)} Qs). "
                f"Observed comparison; individual results may depend on assessment difficulty."
            )
        elif pre_score is None and post_score is not None:
            delta = 0.0
            impact = "Post-Revision Baseline"
            note = f"Initial assessment occurred after {sessions_count} revision session(s) ({total_mins} mins) with a score of {post_score:.1f}%."
        else:
            delta = 0.0
            impact = "Awaiting Assessment"
            note = f"{sessions_count} revision session(s) recorded ({total_mins} mins). Subsequent assessment results pending."

        results.append({
            "topic_id": topic_id,
            "topic_name": topic_name,
            "subject_name": subject_name,
            "sessions_count": sessions_count,
            "total_revision_mins": total_mins,
            "pre_revision_score": pre_score if pre_score is not None else 0.0,
            "post_revision_score": post_score if post_score is not None else 0.0,
            "score_delta": delta,
            "observed_impact": impact,
            "evidence_note": note
        })

    df = pd.DataFrame(results)
    if not df.empty:
        df = df.sort_values(by="score_delta", ascending=False)
    return df
