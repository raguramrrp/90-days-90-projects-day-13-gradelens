"""
GradeLens Topic Weakness Detection Engine.
The primary analytical differentiator: transparent, deterministic topic diagnostics
with explainable reasoning, marks loss analysis, and mistake clustering.
"""

import os
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from src.analytics.calculations import safe_percentage

# Configurable thresholds
WEAKNESS_THRESHOLD = float(os.getenv("WEAKNESS_THRESHOLD", 60.0))
STRONG_THRESHOLD = float(os.getenv("STRONG_THRESHOLD", 75.0))
MIN_ATTEMPTS = int(os.getenv("MIN_ATTEMPTS_FOR_ASSESSMENT", 2))


class TopicWeaknessEngine:
    """
    Transparent, deterministic rule-based weakness detection engine.
    Analyzes student responses to classify topics and explain root causes.
    """

    def __init__(self,
                 weakness_threshold: float = WEAKNESS_THRESHOLD,
                 strong_threshold: float = STRONG_THRESHOLD,
                 min_attempts: int = MIN_ATTEMPTS):
        self.weakness_threshold = weakness_threshold
        self.strong_threshold = strong_threshold
        self.min_attempts = min_attempts

    def analyze_topic(self, topic_responses: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyzes question responses for a single topic.
        Returns a rich diagnostic profile with deterministic classification and explanation.
        """
        if topic_responses.empty:
            return {
                "topic_id": "unknown",
                "topic_name": "Unknown",
                "classification": "Insufficient Data",
                "accuracy_pct": 0.0,
                "total_obtained": 0.0,
                "total_possible": 0.0,
                "marks_lost": 0.0,
                "marks_lost_pct": 0.0,
                "attempts_count": 0,
                "assessments_count": 0,
                "incorrect_count": 0,
                "primary_mistake": "None",
                "explanation": "No question responses recorded for this topic.",
                "priority": "Low",
                "trend": "Stable"
            }

        topic_id = topic_responses["topic_id"].iloc[0]
        topic_name = topic_responses["topic_name"].iloc[0]
        subject_name = topic_responses["subject_name"].iloc[0] if "subject_name" in topic_responses.columns else ""

        total_obtained = float(topic_responses["marks_obtained"].sum())
        total_possible = float(topic_responses["maximum_marks"].sum())
        accuracy_pct = safe_percentage(total_obtained, total_possible)
        marks_lost = round(total_possible - total_obtained, 2)
        marks_lost_pct = safe_percentage(marks_lost, total_possible)

        attempts_count = len(topic_responses)
        assessments_count = topic_responses["exam_id"].nunique()

        # Mistake analysis
        incorrect_rows = topic_responses[topic_responses["answer_status"].isin(["Incorrect", "Partially Correct"])]
        incorrect_count = len(incorrect_rows)

        mistakes_series = topic_responses["mistake_category"].dropna()
        mistakes_series = mistakes_series[mistakes_series != "None"]
        primary_mistake = mistakes_series.mode()[0] if not mistakes_series.empty else "No repeated mistake pattern"
        primary_mistake_count = int((mistakes_series == primary_mistake).sum()) if not mistakes_series.empty else 0

        # Assessment-by-assessment progression to detect Repeated Weakness / Improving / Declining
        exam_scores = topic_responses.groupby(["attempt_date", "exam_id"]).apply(
            lambda g: safe_percentage(g["marks_obtained"].sum(), g["maximum_marks"].sum())
        ).reset_index(name="score_pct").sort_values("attempt_date")

        weak_exams_count = (exam_scores["score_pct"] < self.weakness_threshold).sum()
        total_exam_sessions = len(exam_scores)

        # Trend detection
        trend = "Stable"
        if total_exam_sessions >= 2:
            first_half = exam_scores["score_pct"].iloc[:len(exam_scores)//2].mean()
            second_half = exam_scores["score_pct"].iloc[len(exam_scores)//2:].mean()
            delta = second_half - first_half
            if delta >= 15.0:
                trend = "Improving"
            elif delta <= -15.0:
                trend = "Declining"

        # Classification logic
        if attempts_count < self.min_attempts or total_exam_sessions < 1:
            classification = "Insufficient Data"
            priority = "Low"
            explanation = (
                f"'{topic_name}' has only {attempts_count} recorded question(s) across {total_exam_sessions} assessment(s). "
                f"At least {self.min_attempts} attempts are required for reliable weakness classification."
            )
        elif weak_exams_count >= 2:
            classification = "Repeated Weakness"
            priority = "High"
            mistake_note = f", predominantly driven by '{primary_mistake}' ({primary_mistake_count} occurrences)" if primary_mistake_count > 0 else ""
            explanation = (
                f"'{topic_name}' is classified as a Repeated Weakness because performance remained below {self.weakness_threshold:.0f}% "
                f"across {weak_exams_count} separate assessments (Overall Accuracy: {accuracy_pct:.1f}%){mistake_note}."
            )
        elif accuracy_pct < self.weakness_threshold:
            classification = "Weak"
            priority = "High"
            explanation = (
                f"'{topic_name}' score is {accuracy_pct:.1f}%, which is below the target threshold of {self.weakness_threshold:.0f}%. "
                f"{marks_lost:.1f} marks were lost out of {total_possible:.1f} available marks."
            )
        elif trend == "Improving":
            classification = "Improving"
            priority = "Medium"
            explanation = (
                f"'{topic_name}' demonstrates recent score gains (Overall: {accuracy_pct:.1f}%). "
                f"Continued targeted practice is recommended to consolidate mastery."
            )
        elif trend == "Declining":
            classification = "Declining"
            priority = "High"
            explanation = (
                f"'{topic_name}' has shown a score decline of >= 15% in recent assessments despite earlier adequate performance. "
                f"Early refresher revision is advised."
            )
        elif accuracy_pct >= self.strong_threshold:
            classification = "Strong"
            priority = "Low"
            explanation = (
                f"'{topic_name}' exhibits strong mastery at {accuracy_pct:.1f}% across {attempts_count} questions."
            )
        else:
            classification = "Monitoring"
            priority = "Medium"
            explanation = (
                f"'{topic_name}' is in the moderate range ({accuracy_pct:.1f}%). "
                f"It requires monitoring to prevent regression below the {self.weakness_threshold:.0f}% threshold."
            )

        return {
            "topic_id": topic_id,
            "topic_name": topic_name,
            "subject_name": subject_name,
            "classification": classification,
            "accuracy_pct": accuracy_pct,
            "total_obtained": round(total_obtained, 2),
            "total_possible": round(total_possible, 2),
            "marks_lost": marks_lost,
            "marks_lost_pct": marks_lost_pct,
            "attempts_count": attempts_count,
            "assessments_count": assessments_count,
            "incorrect_count": incorrect_count,
            "primary_mistake": primary_mistake,
            "primary_mistake_count": primary_mistake_count,
            "explanation": explanation,
            "priority": priority,
            "trend": trend
        }

    def analyze_all_topics(self, responses_df: pd.DataFrame) -> pd.DataFrame:
        """
        Runs weakness detection across all topics present in responses_df.
        Returns a structured DataFrame sorted by priority (High, Medium, Low) and marks lost.
        """
        if responses_df.empty:
            return pd.DataFrame()

        topic_results = []
        for topic_id, group in responses_df.groupby("topic_id"):
            res = self.analyze_topic(group)
            topic_results.append(res)

        df = pd.DataFrame(topic_results)
        priority_map = {"High": 1, "Medium": 2, "Low": 3}
        df["priority_rank"] = df["priority"].map(priority_map).fillna(4)
        df = df.sort_values(by=["priority_rank", "marks_lost"], ascending=[True, False]).drop(columns=["priority_rank"])
        return df


# Default engine instance
weakness_engine = TopicWeaknessEngine()
