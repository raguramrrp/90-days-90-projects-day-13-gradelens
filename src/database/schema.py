"""
GradeLens Database Schema Initialization and Verification.
"""

from pathlib import Path
from typing import List, Dict, Any
from src.database.connection import db_manager, DatabaseManager

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SCHEMA_FILE = BASE_DIR / "sql" / "schema.sql"
VIEWS_FILE = BASE_DIR / "sql" / "views.sql"

EXPECTED_TABLES = [
    "classes",
    "faculty",
    "students",
    "subjects",
    "student_subjects",
    "topics",
    "exams",
    "questions",
    "attempts",
    "question_responses",
    "revision_sessions",
    "study_goals",
    "revision_tasks",
    "recommendations"
]

EXPECTED_VIEWS = [
    "vw_student_performance",
    "vw_subject_performance",
    "vw_topic_performance",
    "vw_question_level_analysis",
    "vw_exam_comparison",
    "vw_revision_effectiveness",
    "vw_faculty_class_analytics",
    "vw_recommendation_summary"
]


def init_database(manager: DatabaseManager = None) -> Dict[str, Any]:
    """
    Initializes all database tables and analytical views.
    Returns status report.
    """
    mgr = manager or db_manager

    # 1. Read DDL scripts
    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    with open(VIEWS_FILE, "r", encoding="utf-8") as f:
        views_sql = f.read()

    # 2. Execute schema & views
    mgr.execute_script(schema_sql)
    mgr.execute_script(views_sql)

    # 3. Verify creation
    conn = mgr.get_connection()
    cursor = conn.cursor()
    created_tables: List[str] = []
    created_views: List[str] = []

    try:
        if mgr.engine_type == "postgresql":
            cursor.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
            """)
            created_tables = [row[0] for row in cursor.fetchall()]

            cursor.execute("""
                SELECT table_name FROM information_schema.views 
                WHERE table_schema = 'public';
            """)
            created_views = [row[0] for row in cursor.fetchall()]
        else:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            created_tables = [row[0] for row in cursor.fetchall()]

            cursor.execute("SELECT name FROM sqlite_master WHERE type='view';")
            created_views = [row[0] for row in cursor.fetchall()]
    finally:
        conn.close()

    tables_ok = all(tbl in created_tables for tbl in EXPECTED_TABLES)
    views_ok = all(v in created_views for v in EXPECTED_VIEWS)

    return {
        "success": tables_ok and views_ok,
        "engine": mgr.engine_type,
        "tables_count": len(created_tables),
        "views_count": len(created_views),
        "missing_tables": [t for t in EXPECTED_TABLES if t not in created_tables],
        "missing_views": [v for v in EXPECTED_VIEWS if v not in created_views]
    }


if __name__ == "__main__":
    result = init_database()
    print("Database initialization result:", result)
