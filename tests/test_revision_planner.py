"""
Unit tests for GradeLens Daily Revision Planner & Revision Effectiveness Tracker.
"""

import pytest
import pandas as pd
from src.analytics.revision_tracker import compute_revision_impact


def test_revision_task_lifecycle(test_repo):
    """Verifies creating, fetching, and updating a revision task."""
    task_id = "test_tsk_001"
    student_id = "stu_01"
    topic_id = "top_dsa_2"

    rows = test_repo.create_revision_task(
        task_id=task_id,
        student_id=student_id,
        topic_id=topic_id,
        task_description="Solve 5 DP problems",
        priority="High",
        scheduled_date="2026-11-01"
    )
    assert rows == 1

    tasks = test_repo.get_revision_tasks(student_id=student_id)
    assert not tasks.empty
    created = tasks[tasks["task_id"] == task_id].iloc[0]
    assert created["status"] == "Pending"
    assert created["priority"] == "High"

    # Update to Completed
    up_rows = test_repo.update_task_status(task_id, "Completed")
    assert up_rows == 1
    updated_tasks = test_repo.get_revision_tasks(student_id=student_id)
    updated = updated_tasks[updated_tasks["task_id"] == task_id].iloc[0]
    assert updated["status"] == "Completed"
    assert updated["completed_at"] is not None


def test_study_goal_lifecycle(test_repo):
    """Verifies creating, fetching, and achieving a study goal."""
    goal_id = "test_goal_001"
    student_id = "stu_01"
    subject_id = "sub_dsa"

    rows = test_repo.create_study_goal(
        goal_id=goal_id,
        student_id=student_id,
        subject_id=subject_id,
        target_type="Subject Target",
        target_value=85.0,
        deadline="2026-12-01"
    )
    assert rows == 1

    goals = test_repo.get_study_goals(student_id=student_id)
    assert not goals.empty
    created = goals[goals["goal_id"] == goal_id].iloc[0]
    assert created["status"] == "In Progress"

    up_rows = test_repo.update_goal_status(goal_id, "Completed")
    assert up_rows == 1
    updated_goals = test_repo.get_study_goals(student_id=student_id)
    assert updated_goals[updated_goals["goal_id"] == goal_id].iloc[0]["status"] == "Completed"


def test_revision_effectiveness_computation(test_repo):
    """
    Verifies that revision impact calculation shows score improvement
    for Diya Patel (stu_02) on Gradient Descent (top_ml_1).
    """
    responses = test_repo.get_question_responses(student_id="stu_02")
    revisions = test_repo.get_revision_sessions(student_id="stu_02")

    impact_df = compute_revision_impact(responses, revisions)
    assert not impact_df.empty
    gd_row = impact_df[impact_df["topic_id"] == "top_ml_1"]
    assert not gd_row.empty
    rec = gd_row.iloc[0]
    assert rec["sessions_count"] >= 2
    assert rec["score_delta"] > 0  # Demonstrates positive observed gain
    assert "Observed comparison" in rec["evidence_note"]
