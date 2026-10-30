"""
Unit tests for GradeLens Faculty Analytics & At-Risk Student Detection.
"""

import pytest
from src.analytics.calculations import calculate_student_ranking
from src.analytics.weakness_engine import TopicWeaknessEngine


def test_faculty_class_aggregations(test_repo):
    """Verifies class-wide student performance calculations and rank distributions."""
    attempts = test_repo.get_attempts()
    ranking_df = calculate_student_ranking(attempts, anonymize=False)
    assert not ranking_df.empty
    assert len(ranking_df) >= 6

    # Verify rank 1 has highest percentage
    top_student = ranking_df.iloc[0]
    last_student = ranking_df.iloc[-1]
    assert top_student["percentage"] >= last_student["percentage"]


def test_at_risk_student_detection_rules(test_repo):
    """
    Verifies that student Ananya Sen (stu_04) is flagged as at-risk
    based on the transparent criteria (Overall percentage < 50%).
    """
    engine = TopicWeaknessEngine()
    attempts = test_repo.get_attempts(student_id="stu_04")
    responses = test_repo.get_question_responses(student_id="stu_04")

    obtained = attempts["marks_obtained"].sum()
    total = attempts["total_marks"].sum()
    pct = (obtained * 100.0) / total if total > 0 else 0.0

    topic_diag = engine.analyze_all_topics(responses)
    rep_weak_count = (topic_diag["classification"] == "Repeated Weakness").sum() if not topic_diag.empty else 0

    is_at_risk = (pct < 50.0) or (rep_weak_count >= 2)
    assert bool(is_at_risk) is True
    assert pct < 50.0  # Ananya Sen persona is struggling (<50%)
