"""
Unit and integration tests for GradeLens database layer, schemas, constraints, and transactions.
"""

import pytest
import sqlite3
from src.database.connection import DatabaseManager, check_postgres_availability
from src.database.schema import init_database, EXPECTED_TABLES, EXPECTED_VIEWS


def test_schema_initialization(test_db_manager):
    """Verifies that all 14 logical tables and 8 views are created successfully."""
    status = init_database(test_db_manager)
    assert status["success"] is True
    assert status["missing_tables"] == []
    assert status["missing_views"] == []
    assert status["tables_count"] >= len(EXPECTED_TABLES)
    assert status["views_count"] >= len(EXPECTED_VIEWS)


def test_database_manager_status(test_db_manager):
    """Verifies database status report returns connected status and version info."""
    stat = test_db_manager.get_status()
    assert stat["active_engine"] == "sqlite"
    assert stat["connected"] is True
    assert "SQLite" in stat["version"]


def test_check_postgres_availability_does_not_crash():
    """Verifies that checking PostgreSQL availability returns a dictionary with diagnostics."""
    res = check_postgres_availability()
    assert isinstance(res, dict)
    assert "available" in res
    assert "port" in res
    assert "database" in res


def test_repository_students_query(test_repo):
    """Verifies repository fetches seeded students with expected attributes."""
    students = test_repo.get_students()
    assert not students.empty
    assert len(students) >= 6
    assert "student_code" in students.columns
    assert "STU101" in students["student_code"].values


def test_repository_subjects_and_topics(test_repo):
    """Verifies repository retrieves subjects and linked topics."""
    subjects = test_repo.get_subjects()
    assert not subjects.empty
    assert len(subjects) >= 4

    topics = test_repo.get_topics()
    assert not topics.empty
    assert len(topics) >= 10
    assert "unit_name" in topics.columns


def test_marks_constraint_enforcement(test_db_manager):
    """Verifies that question_responses rejects marks_obtained exceeding maximum_marks."""
    conn = test_db_manager.get_connection()
    cursor = conn.cursor()
    with pytest.raises(Exception):
        # Attempt to insert marks_obtained = 15.0 when maximum_marks = 10.0
        cursor.execute("""
            INSERT INTO question_responses (
                response_id, attempt_id, question_id, marks_obtained, maximum_marks, answer_status
            ) VALUES ('err_resp_1', 'att_stu_01_ex_ia1', 'q_ia1_1', 15.0, 10.0, 'Correct');
        """)
        conn.commit()
    conn.close()
