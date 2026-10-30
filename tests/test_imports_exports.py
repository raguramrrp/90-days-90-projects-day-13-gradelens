"""
Unit tests for GradeLens CSV/Excel import validation and Power BI dataset export.
"""

import pytest
import pandas as pd
from src.imports.validator import validate_import_dataframe, commit_imported_records
from src.imports.templates import SAMPLE_IMPORT_DATA
from src.exports.powerbi_exporter import export_powerbi_datasets


def test_import_validation_valid_data(test_repo):
    """Verifies that standard template data passes validation."""
    df = pd.DataFrame(SAMPLE_IMPORT_DATA)
    valid_rows, invalid_rows, summary = validate_import_dataframe(df, test_repo)
    assert summary["invalid_count"] == 0
    assert summary["valid_count"] == len(SAMPLE_IMPORT_DATA)
    assert len(invalid_rows) == 0


def test_import_validation_detects_errors(test_repo):
    """Verifies that invalid rows (exceeded marks, negative marks, missing fields) are caught."""
    bad_data = [
        {
            "student_code": "STU101", "subject_code": "CS701", "topic_name": "Relational Algebra",
            "exam_name": "IA 1", "maximum_marks": 10.0, "marks_obtained": 15.0  # Exceeds max marks!
        },
        {
            "student_code": "STU101", "subject_code": "CS701", "topic_name": "Relational Algebra",
            "exam_name": "IA 1", "maximum_marks": -5.0, "marks_obtained": 2.0  # Negative max marks!
        },
        {
            "student_code": "", "subject_code": "CS701", "topic_name": "Relational Algebra",
            "exam_name": "IA 1", "maximum_marks": 10.0, "marks_obtained": 5.0  # Missing student code!
        }
    ]
    bad_df = pd.DataFrame(bad_data)
    valid_rows, invalid_rows, summary = validate_import_dataframe(bad_df, test_repo)
    assert summary["invalid_count"] == 3
    assert summary["valid_count"] == 0
    assert "exceeds maximum_marks" in invalid_rows[0]["error_reasons"]
    assert "greater than 0" in invalid_rows[1]["error_reasons"]
    assert "Missing student_code" in invalid_rows[2]["error_reasons"]


def test_import_commit_transaction(test_repo):
    """Verifies atomic commit of validated rows into database."""
    sample_row = {
        "student_code": "STU101",
        "student_id": "stu_01",
        "subject_code": "CS701",
        "subject_id": "sub_dsa",
        "topic_name": "Red-Black Trees",
        "unit_name": "Unit 1: Trees",
        "exam_name": "Quiz 3 Testing",
        "exam_type": "Quiz",
        "exam_date": "2026-10-30",
        "academic_period": "Semester 7",
        "question_text": "Verify Red-Black properties on root deletion.",
        "maximum_marks": 5.0,
        "marks_obtained": 4.5,
        "difficulty": "Hard",
        "question_type": "Short Answer",
        "answer_status": "Correct",
        "time_spent_seconds": 180,
        "mistake_category": "None",
        "confidence_rating": "High",
        "remarks": "Accurate tree recoloring"
    }
    inserted = commit_imported_records([sample_row], test_repo)
    assert inserted == 1

    # Verify response is queryable
    responses = test_repo.get_question_responses(student_id="stu_01")
    assert any("Red-Black Trees" in str(t) for t in responses["topic_name"].values)


def test_powerbi_dataset_export(test_repo, tmp_path):
    """Verifies that all 8 analytical views export to non-empty CSVs."""
    export_dir = tmp_path / "powerbi_export"
    res = export_powerbi_datasets(repository=test_repo, output_dir=export_dir)
    assert len(res) == 8
    for fname, info in res.items():
        assert info["status"] == "Success"
        assert info["rows"] >= 0
        csv_file = export_dir / fname
        assert csv_file.exists()
        assert csv_file.stat().st_size > 0
