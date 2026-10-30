"""
Unit tests for GradeLens Topic Weakness Detection Engine.
Verifies deterministic rules, multi-exam repeated weakness, and explainable output.
"""

import pytest
import pandas as pd
from src.analytics.weakness_engine import TopicWeaknessEngine


@pytest.fixture
def engine():
    return TopicWeaknessEngine(weakness_threshold=60.0, strong_threshold=75.0, min_attempts=2)


def test_insufficient_data_classification(engine):
    """Verifies that fewer than min_attempts yields Insufficient Data."""
    single_q = pd.DataFrame([{
        "topic_id": "top_1",
        "topic_name": "Recursion",
        "subject_name": "DSA",
        "exam_id": "ex_1",
        "attempt_date": "2026-10-01",
        "marks_obtained": 3.0,
        "maximum_marks": 10.0,
        "answer_status": "Incorrect",
        "mistake_category": "Conceptual misunderstanding"
    }])
    res = engine.analyze_topic(single_q)
    assert res["classification"] == "Insufficient Data"
    assert "At least 2 attempts are required" in res["explanation"]


def test_strong_topic_classification(engine):
    """Verifies topic with >= 75% accuracy is classified as Strong."""
    data = [
        {
            "topic_id": "top_tree", "topic_name": "Binary Trees", "subject_name": "DSA",
            "exam_id": "ex_1", "attempt_date": "2026-09-01", "marks_obtained": 9.0, "maximum_marks": 10.0,
            "answer_status": "Correct", "mistake_category": "None"
        },
        {
            "topic_id": "top_tree", "topic_name": "Binary Trees", "subject_name": "DSA",
            "exam_id": "ex_2", "attempt_date": "2026-10-01", "marks_obtained": 10.0, "maximum_marks": 10.0,
            "answer_status": "Correct", "mistake_category": "None"
        }
    ]
    df = pd.DataFrame(data)
    res = engine.analyze_topic(df)
    assert res["classification"] == "Strong"
    assert res["accuracy_pct"] == 95.0
    assert "strong mastery" in res["explanation"].lower()


def test_repeated_weakness_classification(engine):
    """Verifies that topic scoring < 60% across 2 assessments is flagged as Repeated Weakness."""
    data = [
        {
            "topic_id": "top_dp", "topic_name": "Dynamic Programming", "subject_name": "DSA",
            "exam_id": "ex_1", "attempt_date": "2026-09-01", "marks_obtained": 4.0, "maximum_marks": 10.0,
            "answer_status": "Incorrect", "mistake_category": "Calculation error"
        },
        {
            "topic_id": "top_dp", "topic_name": "Dynamic Programming", "subject_name": "DSA",
            "exam_id": "ex_2", "attempt_date": "2026-10-01", "marks_obtained": 5.0, "maximum_marks": 10.0,
            "answer_status": "Partially Correct", "mistake_category": "Calculation error"
        }
    ]
    df = pd.DataFrame(data)
    res = engine.analyze_topic(df)
    assert res["classification"] == "Repeated Weakness"
    assert res["priority"] == "High"
    assert res["primary_mistake"] == "Calculation error"
    assert "Repeated Weakness" in res["explanation"]
    assert "Calculation error" in res["explanation"]


def test_improving_topic_classification(engine):
    """Verifies that significant score gain between assessments is flagged as Improving."""
    data = [
        {
            "topic_id": "top_gd", "topic_name": "Gradient Descent", "subject_name": "ML",
            "exam_id": "ex_1", "attempt_date": "2026-09-01", "marks_obtained": 4.0, "maximum_marks": 10.0,
            "answer_status": "Incorrect", "mistake_category": "Formula error"
        },
        {
            "topic_id": "top_gd", "topic_name": "Gradient Descent", "subject_name": "ML",
            "exam_id": "ex_2", "attempt_date": "2026-10-01", "marks_obtained": 9.5, "maximum_marks": 10.0,
            "answer_status": "Correct", "mistake_category": "None"
        }
    ]
    df = pd.DataFrame(data)
    res = engine.analyze_topic(df)
    assert res["classification"] == "Improving"
    assert "recent score gains" in res["explanation"]


def test_seeded_student_weakness_detection(test_repo, engine):
    """Verifies engine on seeded student STU101 (Aarav), expecting Dynamic Programming as Repeated Weakness."""
    responses = test_repo.get_question_responses(student_id="stu_01")
    analysis = engine.analyze_all_topics(responses)
    assert not analysis.empty
    dp_row = analysis[analysis["topic_id"] == "top_dsa_2"]
    assert not dp_row.empty
    assert dp_row.iloc[0]["classification"] == "Repeated Weakness"
