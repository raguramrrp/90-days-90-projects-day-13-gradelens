"""
Unit tests for GradeLens mathematical, percentage, difficulty, ranking, and trend calculations.
"""

import pytest
import pandas as pd
from src.analytics.calculations import (
    safe_percentage,
    calculate_subject_metrics,
    calculate_difficulty_breakdown,
    calculate_student_ranking
)
from src.analytics.trends import (
    compute_exam_progression,
    compute_mistake_distribution,
    compute_confidence_calibration
)


def test_safe_percentage_edge_cases():
    """Tests percentage computation with zero, negative, and normal values."""
    assert safe_percentage(50.0, 100.0) == 50.0
    assert safe_percentage(0.0, 100.0) == 0.0
    assert safe_percentage(10.0, 0.0) == 0.0
    assert safe_percentage(10.0, -5.0) == 0.0
    assert safe_percentage(-10.0, 100.0) == 0.0
    assert safe_percentage(105.0, 100.0) == 100.0  # Clips to 100
    assert safe_percentage(1.0, 3.0) == 33.33


def test_calculate_subject_metrics_empty():
    """Verifies subject metrics handle empty dataframes gracefully."""
    empty_df = pd.DataFrame()
    metrics = calculate_subject_metrics(empty_df)
    assert metrics["total_assessments"] == 0
    assert metrics["overall_percentage"] == 0.0
    assert metrics["consistency_rating"] == "Insufficient Data"


def test_calculate_subject_metrics_valid(test_repo):
    """Verifies subject metrics computation on real seeded question responses."""
    responses = test_repo.get_question_responses(student_id="stu_03")  # Rohan (top student)
    metrics = calculate_subject_metrics(responses)
    assert metrics["total_assessments"] >= 3
    assert metrics["overall_percentage"] >= 80.0
    assert metrics["total_marks_lost"] >= 0.0
    assert metrics["highest_pct"] >= metrics["lowest_pct"]


def test_calculate_difficulty_breakdown():
    """Verifies accuracy calculation grouped across Easy, Medium, Hard questions."""
    data = [
        {"response_id": "r1", "difficulty": "Easy", "marks_obtained": 10.0, "maximum_marks": 10.0},
        {"response_id": "r2", "difficulty": "Easy", "marks_obtained": 8.0, "maximum_marks": 10.0},
        {"response_id": "r3", "difficulty": "Hard", "marks_obtained": 5.0, "maximum_marks": 10.0},
    ]
    df = pd.DataFrame(data)
    res = calculate_difficulty_breakdown(df)
    assert len(res) == 2
    easy_row = res[res["difficulty"] == "Easy"].iloc[0]
    hard_row = res[res["difficulty"] == "Hard"].iloc[0]
    assert easy_row["accuracy_pct"] == 90.0
    assert hard_row["accuracy_pct"] == 50.0


def test_calculate_student_ranking_ties_and_anonymization():
    """Verifies that ties in student rankings are correctly handled and anonymized."""
    data = [
        {"student_id": "s1", "student_name": "Alice", "exam_id": "e1", "marks_obtained": 90.0, "total_marks": 100.0},
        {"student_id": "s2", "student_name": "Bob", "exam_id": "e1", "marks_obtained": 90.0, "total_marks": 100.0},
        {"student_id": "s3", "student_name": "Charlie", "exam_id": "e1", "marks_obtained": 70.0, "total_marks": 100.0},
    ]
    df = pd.DataFrame(data)
    ranking = calculate_student_ranking(df, anonymize=False)
    assert ranking.iloc[0]["rank"] == 1
    assert ranking.iloc[1]["rank"] == 1  # Tie
    assert ranking.iloc[2]["rank"] == 3  # Next rank is 3

    anon_ranking = calculate_student_ranking(df, anonymize=True)
    assert "Alice" not in anon_ranking["display_name"].values
    assert "Student #1" in anon_ranking["display_name"].values


def test_compute_exam_progression():
    """Verifies chronological score progression and delta calculations."""
    data = [
        {"exam_date": "2026-08-01", "exam_name": "Quiz 1", "marks_obtained": 15.0, "total_marks": 20.0},
        {"exam_date": "2026-09-01", "exam_name": "IA 1", "marks_obtained": 40.0, "total_marks": 50.0},
        {"exam_date": "2026-10-01", "exam_name": "Model", "marks_obtained": 90.0, "total_marks": 100.0},
    ]
    df = pd.DataFrame(data)
    res = compute_exam_progression(df)
    assert len(res) == 3
    assert res.iloc[0]["percentage"] == 75.0
    assert res.iloc[1]["percentage"] == 80.0
    assert res.iloc[1]["delta_pct"] == 5.0
    assert res.iloc[2]["percentage"] == 90.0
    assert res.iloc[2]["delta_pct"] == 10.0


def test_compute_mistake_distribution():
    """Verifies aggregation of marks lost per mistake category."""
    data = [
        {"response_id": "r1", "mistake_category": "Calculation error", "marks_lost": 4.0},
        {"response_id": "r2", "mistake_category": "Calculation error", "marks_lost": 2.0},
        {"response_id": "r3", "mistake_category": "Conceptual misunderstanding", "marks_lost": 6.0},
        {"response_id": "r4", "mistake_category": "None", "marks_lost": 0.0},
    ]
    df = pd.DataFrame(data)
    dist = compute_mistake_distribution(df)
    assert len(dist) == 2
    assert "Calculation error" in dist["mistake_category"].values
    assert "Conceptual misunderstanding" in dist["mistake_category"].values
    assert dist[dist["mistake_category"] == "Conceptual misunderstanding"].iloc[0]["marks_lost"] == 6.0


def test_compute_confidence_calibration():
    """Verifies metacognitive accuracy comparison across confidence levels."""
    data = [
        {"response_id": "r1", "confidence_rating": "High", "answer_status": "Correct"},
        {"response_id": "r2", "confidence_rating": "High", "answer_status": "Incorrect"},  # Blind spot
        {"response_id": "r3", "confidence_rating": "Low", "answer_status": "Incorrect"},
    ]
    df = pd.DataFrame(data)
    calib = compute_confidence_calibration(df)
    assert len(calib) == 2
    high_row = calib[calib["confidence_rating"] == "High"].iloc[0]
    assert high_row["accuracy_pct"] == 50.0
    assert high_row["total_questions"] == 2
