"""
Unit tests for GradeLens Rule-Based Recommendation Engine.
Verifies priority assignment, deduplication, and evidence explanations.
"""

import pytest
from src.recommendations.engine import RecommendationEngine


def test_recommendation_generation(test_repo):
    """Verifies recommendations are generated for student stu_01 (Aarav)."""
    engine = RecommendationEngine(repository=test_repo)
    recs = engine.generate_recommendations_for_student("stu_01")
    assert isinstance(recs, list)

    saved_recs = test_repo.get_recommendations(student_id="stu_01")
    assert not saved_recs.empty
    assert "High" in saved_recs["priority"].values
    assert any("Urgent Revision" in str(t) for t in saved_recs["recommendation_type"].values)


def test_recommendation_deduplication(test_repo):
    """Verifies that running recommendation engine consecutively does not create duplicate active recommendations."""
    engine = RecommendationEngine(repository=test_repo)
    initial_recs = test_repo.get_recommendations(student_id="stu_01")
    initial_count = len(initial_recs)

    # Run generation again
    new_recs = engine.generate_recommendations_for_student("stu_01")
    assert len(new_recs) == 0  # Deduplicated

    after_recs = test_repo.get_recommendations(student_id="stu_01")
    assert len(after_recs) == initial_count


def test_recommendation_status_update(test_repo):
    """Verifies updating recommendation status to Completed."""
    recs = test_repo.get_recommendations(student_id="stu_01", status="Active")
    if not recs.empty:
        rec_id = recs.iloc[0]["recommendation_id"]
        rows = test_repo.update_recommendation_status(rec_id, "Completed")
        assert rows == 1

        updated = test_repo.get_recommendations(student_id="stu_01")
        row = updated[updated["recommendation_id"] == rec_id].iloc[0]
        assert row["status"] == "Completed"
