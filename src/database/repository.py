"""
GradeLens Database Repository Layer.
Provides type-safe, parameterized queries and transactions for all academic entities.
"""

import uuid
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from src.database.connection import db_manager, DatabaseManager


class Repository:
    """Repository pattern implementation for GradeLens database operations."""

    def __init__(self, manager: DatabaseManager = None):
        self.mgr = manager or db_manager

    def query_df(self, sql: str, params: Optional[tuple] = None) -> pd.DataFrame:
        """Executes a SELECT query and returns a pandas DataFrame."""
        conn = self.mgr.get_connection()
        try:
            return pd.read_sql_query(sql, conn, params=params or ())
        finally:
            conn.close()

    def execute_write(self, sql: str, params: Optional[tuple] = None) -> int:
        """Executes an INSERT, UPDATE, or DELETE query and returns rows affected."""
        conn = self.mgr.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, params or ())
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()

    # -------------------------------------------------------------------------
    # Students, Faculty & Classes
    # -------------------------------------------------------------------------
    def get_classes(self) -> pd.DataFrame:
        return self.query_df("SELECT * FROM classes ORDER BY class_name ASC;")

    def get_faculty(self) -> pd.DataFrame:
        return self.query_df("SELECT * FROM faculty ORDER BY name ASC;")

    def get_students(self, class_id: Optional[str] = None) -> pd.DataFrame:
        sql = """
            SELECT s.*, c.class_name 
            FROM students s
            LEFT JOIN classes c ON s.class_id = c.class_id
        """
        params = []
        if class_id:
            sql += " WHERE s.class_id = ?"
            params.append(class_id)
        sql += " ORDER BY s.name ASC;"
        return self.query_df(sql, tuple(params))

    def get_student_by_id(self, student_id: str) -> Optional[Dict[str, Any]]:
        df = self.query_df("SELECT * FROM students WHERE student_id = ?;", (student_id,))
        if not df.empty:
            return df.iloc[0].to_dict()
        return None

    def create_student(self, student_id: str, student_code: str, name: str, email: str,
                       class_id: str, department: str, academic_year: str) -> int:
        sql = """
            INSERT INTO students (student_id, student_code, name, email, class_id, department, academic_year)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """
        return self.execute_write(sql, (student_id, student_code, name, email, class_id, department, academic_year))

    # -------------------------------------------------------------------------
    # Subjects & Topics
    # -------------------------------------------------------------------------
    def get_subjects(self, student_id: Optional[str] = None) -> pd.DataFrame:
        if student_id:
            sql = """
                SELECT sub.* 
                FROM subjects sub
                JOIN student_subjects ss ON sub.subject_id = ss.subject_id
                WHERE ss.student_id = ?
                ORDER BY sub.subject_name ASC;
            """
            return self.query_df(sql, (student_id,))
        return self.query_df("SELECT * FROM subjects ORDER BY subject_name ASC;")

    def get_topics(self, subject_id: Optional[str] = None) -> pd.DataFrame:
        sql = """
            SELECT t.*, s.subject_name, s.subject_code 
            FROM topics t
            JOIN subjects s ON t.subject_id = s.subject_id
        """
        params = []
        if subject_id:
            sql += " WHERE t.subject_id = ?"
            params.append(subject_id)
        sql += " ORDER BY t.unit_name ASC, t.topic_name ASC;"
        return self.query_df(sql, tuple(params))

    def create_subject(self, subject_id: str, subject_code: str, subject_name: str, department: str) -> int:
        sql = """
            INSERT INTO subjects (subject_id, subject_code, subject_name, department)
            VALUES (?, ?, ?, ?);
        """
        return self.execute_write(sql, (subject_id, subject_code, subject_name, department))

    def create_topic(self, topic_id: str, subject_id: str, unit_name: str, topic_name: str,
                     subtopic_name: Optional[str] = None) -> int:
        sql = """
            INSERT INTO topics (topic_id, subject_id, unit_name, topic_name, subtopic_name)
            VALUES (?, ?, ?, ?, ?);
        """
        return self.execute_write(sql, (topic_id, subject_id, unit_name, topic_name, subtopic_name))

    # -------------------------------------------------------------------------
    # Exams & Questions
    # -------------------------------------------------------------------------
    def get_exams(self, class_id: Optional[str] = None, exam_type: Optional[str] = None) -> pd.DataFrame:
        sql = "SELECT e.*, c.class_name FROM exams e LEFT JOIN classes c ON e.class_id = c.class_id WHERE 1=1"
        params = []
        if class_id:
            sql += " AND e.class_id = ?"
            params.append(class_id)
        if exam_type:
            sql += " AND e.exam_type = ?"
            params.append(exam_type)
        sql += " ORDER BY e.exam_date DESC;"
        return self.query_df(sql, tuple(params))

    def get_exam_by_id(self, exam_id: str) -> Optional[Dict[str, Any]]:
        df = self.query_df("SELECT * FROM exams WHERE exam_id = ?;", (exam_id,))
        if not df.empty:
            return df.iloc[0].to_dict()
        return None

    def create_exam(self, exam_id: str, exam_name: str, exam_type: str, exam_date: str,
                    academic_period: str, maximum_marks: float, class_id: Optional[str] = None,
                    description: Optional[str] = None) -> int:
        sql = """
            INSERT INTO exams (exam_id, exam_name, exam_type, exam_date, academic_period, maximum_marks, class_id, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """
        return self.execute_write(sql, (exam_id, exam_name, exam_type, exam_date, academic_period, maximum_marks, class_id, description))

    def update_exam(self, exam_id: str, exam_name: str, exam_type: str, exam_date: str,
                    academic_period: str, maximum_marks: float, description: Optional[str] = None) -> int:
        sql = """
            UPDATE exams 
            SET exam_name = ?, exam_type = ?, exam_date = ?, academic_period = ?, maximum_marks = ?, description = ?
            WHERE exam_id = ?;
        """
        return self.execute_write(sql, (exam_name, exam_type, exam_date, academic_period, maximum_marks, description, exam_id))

    def delete_exam(self, exam_id: str) -> int:
        return self.execute_write("DELETE FROM exams WHERE exam_id = ?;", (exam_id,))

    def get_questions(self, exam_id: Optional[str] = None, subject_id: Optional[str] = None,
                      topic_id: Optional[str] = None) -> pd.DataFrame:
        sql = """
            SELECT q.*, e.exam_name, s.subject_name, t.topic_name, t.unit_name
            FROM questions q
            JOIN exams e ON q.exam_id = e.exam_id
            JOIN subjects s ON q.subject_id = s.subject_id
            JOIN topics t ON q.topic_id = t.topic_id
            WHERE 1=1
        """
        params = []
        if exam_id:
            sql += " AND q.exam_id = ?"
            params.append(exam_id)
        if subject_id:
            sql += " AND q.subject_id = ?"
            params.append(subject_id)
        if topic_id:
            sql += " AND q.topic_id = ?"
            params.append(topic_id)
        sql += " ORDER BY q.question_id ASC;"
        return self.query_df(sql, tuple(params))

    def create_question(self, question_id: str, exam_id: str, subject_id: str, topic_id: str,
                        question_text: str, maximum_marks: float, difficulty: str, question_type: str) -> int:
        sql = """
            INSERT INTO questions (question_id, exam_id, subject_id, topic_id, question_text, maximum_marks, difficulty, question_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """
        return self.execute_write(sql, (question_id, exam_id, subject_id, topic_id, question_text, maximum_marks, difficulty, question_type))

    # -------------------------------------------------------------------------
    # Attempts & Question Responses
    # -------------------------------------------------------------------------
    def get_attempts(self, student_id: Optional[str] = None, exam_id: Optional[str] = None) -> pd.DataFrame:
        sql = """
            SELECT a.*, s.name AS student_name, s.student_code, e.exam_name, e.exam_type, e.exam_date,
                   ROUND((a.marks_obtained * 100.0 / NULLIF(a.total_marks, 0)), 2) AS percentage
            FROM attempts a
            JOIN students s ON a.student_id = s.student_id
            JOIN exams e ON a.exam_id = e.exam_id
            WHERE 1=1
        """
        params = []
        if student_id:
            sql += " AND a.student_id = ?"
            params.append(student_id)
        if exam_id:
            sql += " AND a.exam_id = ?"
            params.append(exam_id)
        sql += " ORDER BY e.exam_date DESC;"
        return self.query_df(sql, tuple(params))

    def record_attempt(self, attempt_id: str, student_id: str, exam_id: str,
                       total_marks: float, marks_obtained: float, attempt_date: str,
                       duration_minutes: Optional[int] = None) -> int:
        sql = """
            INSERT INTO attempts (attempt_id, student_id, exam_id, total_marks, marks_obtained, attempt_date, duration_minutes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(student_id, exam_id) DO UPDATE SET
                total_marks = excluded.total_marks,
                marks_obtained = excluded.marks_obtained,
                attempt_date = excluded.attempt_date,
                duration_minutes = excluded.duration_minutes;
        """
        return self.execute_write(sql, (attempt_id, student_id, exam_id, total_marks, marks_obtained, attempt_date, duration_minutes))

    def get_question_responses(self, student_id: Optional[str] = None,
                               subject_id: Optional[str] = None,
                               topic_id: Optional[str] = None,
                               exam_id: Optional[str] = None) -> pd.DataFrame:
        sql = """
            SELECT qr.*, a.student_id, a.attempt_date, s.name AS student_name,
                   q.question_text, q.difficulty, q.question_type,
                   sub.subject_id, sub.subject_name, sub.subject_code,
                   t.topic_id, t.topic_name, t.unit_name,
                   e.exam_id, e.exam_name, e.exam_type,
                   (qr.maximum_marks - qr.marks_obtained) AS marks_lost,
                   ROUND((qr.marks_obtained * 100.0 / NULLIF(qr.maximum_marks, 0)), 2) AS percentage
            FROM question_responses qr
            JOIN attempts a ON qr.attempt_id = a.attempt_id
            JOIN students s ON a.student_id = s.student_id
            JOIN questions q ON qr.question_id = q.question_id
            JOIN exams e ON q.exam_id = e.exam_id
            JOIN subjects sub ON q.subject_id = sub.subject_id
            JOIN topics t ON q.topic_id = t.topic_id
            WHERE 1=1
        """
        params = []
        if student_id:
            sql += " AND a.student_id = ?"
            params.append(student_id)
        if subject_id:
            sql += " AND sub.subject_id = ?"
            params.append(subject_id)
        if topic_id:
            sql += " AND t.topic_id = ?"
            params.append(topic_id)
        if exam_id:
            sql += " AND e.exam_id = ?"
            params.append(exam_id)
        sql += " ORDER BY a.attempt_date ASC, q.question_id ASC;"
        return self.query_df(sql, tuple(params))

    def record_question_response(self, response_id: str, attempt_id: str, question_id: str,
                                 marks_obtained: float, maximum_marks: float, answer_status: str,
                                 time_spent_seconds: Optional[int] = None,
                                 mistake_category: Optional[str] = None,
                                 confidence_rating: Optional[str] = None,
                                 remarks: Optional[str] = None) -> int:
        sql = """
            INSERT INTO question_responses (response_id, attempt_id, question_id, marks_obtained, maximum_marks,
                                            answer_status, time_spent_seconds, mistake_category, confidence_rating, remarks)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        return self.execute_write(sql, (response_id, attempt_id, question_id, marks_obtained, maximum_marks,
                                        answer_status, time_spent_seconds, mistake_category, confidence_rating, remarks))

    # -------------------------------------------------------------------------
    # Revision Sessions, Tasks & Goals
    # -------------------------------------------------------------------------
    def get_revision_sessions(self, student_id: Optional[str] = None, topic_id: Optional[str] = None) -> pd.DataFrame:
        sql = """
            SELECT rs.*, s.name AS student_name, sub.subject_name, t.topic_name, t.unit_name
            FROM revision_sessions rs
            JOIN students s ON rs.student_id = s.student_id
            JOIN subjects sub ON rs.subject_id = sub.subject_id
            JOIN topics t ON rs.topic_id = t.topic_id
            WHERE 1=1
        """
        params = []
        if student_id:
            sql += " AND rs.student_id = ?"
            params.append(student_id)
        if topic_id:
            sql += " AND rs.topic_id = ?"
            params.append(topic_id)
        sql += " ORDER BY rs.revision_date DESC;"
        return self.query_df(sql, tuple(params))

    def log_revision_session(self, session_id: str, student_id: str, subject_id: str,
                             topic_id: str, revision_date: str, duration_minutes: int,
                             revision_type: str, notes: Optional[str] = None) -> int:
        sql = """
            INSERT INTO revision_sessions (session_id, student_id, subject_id, topic_id, revision_date, duration_minutes, revision_type, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """
        return self.execute_write(sql, (session_id, student_id, subject_id, topic_id, revision_date, duration_minutes, revision_type, notes))

    def get_revision_tasks(self, student_id: Optional[str] = None, status: Optional[str] = None) -> pd.DataFrame:
        sql = """
            SELECT rt.*, t.topic_name, t.unit_name, sub.subject_name, sub.subject_code
            FROM revision_tasks rt
            JOIN topics t ON rt.topic_id = t.topic_id
            JOIN subjects sub ON t.subject_id = sub.subject_id
            WHERE 1=1
        """
        params = []
        if student_id:
            sql += " AND rt.student_id = ?"
            params.append(student_id)
        if status:
            sql += " AND rt.status = ?"
            params.append(status)
        sql += " ORDER BY rt.scheduled_date ASC, rt.priority DESC;"
        return self.query_df(sql, tuple(params))

    def create_revision_task(self, task_id: Optional[str] = None, student_id: str = "", topic_id: str = "",
                             task_description: str = "", priority: str = "Medium", scheduled_date: str = "") -> int:
        if not task_id:
            task_id = f"tsk_{uuid.uuid4().hex[:8]}"
        sql = """
            INSERT INTO revision_tasks (task_id, student_id, topic_id, task_description, priority, scheduled_date, status)
            VALUES (?, ?, ?, ?, ?, ?, 'Pending');
        """
        try:
            return self.execute_write(sql, (task_id, student_id, topic_id, task_description, priority, scheduled_date))
        except Exception:
            fresh_id = f"tsk_{uuid.uuid4().hex[:8]}"
            return self.execute_write(sql, (fresh_id, student_id, topic_id, task_description, priority, scheduled_date))

    def update_task_status(self, task_id: str, status: str) -> int:
        completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S") if status == "Completed" else None
        sql = "UPDATE revision_tasks SET status = ?, completed_at = ? WHERE task_id = ?;"
        return self.execute_write(sql, (status, completed_at, task_id))

    def update_revision_task(self, task_id: str, task_description: str, priority: str, scheduled_date: str) -> int:
        sql = "UPDATE revision_tasks SET task_description = ?, priority = ?, scheduled_date = ? WHERE task_id = ?;"
        return self.execute_write(sql, (task_description, priority, scheduled_date, task_id))

    def delete_revision_task(self, task_id: str) -> int:
        return self.execute_write("DELETE FROM revision_tasks WHERE task_id = ?;", (task_id,))

    def get_study_goals(self, student_id: Optional[str] = None, status: Optional[str] = None) -> pd.DataFrame:
        sql = """
            SELECT sg.*, sub.subject_name, t.topic_name
            FROM study_goals sg
            JOIN subjects sub ON sg.subject_id = sub.subject_id
            LEFT JOIN topics t ON sg.topic_id = t.topic_id
            WHERE 1=1
        """
        params = []
        if student_id:
            sql += " AND sg.student_id = ?"
            params.append(student_id)
        if status:
            sql += " AND sg.status = ?"
            params.append(status)
        sql += " ORDER BY sg.deadline ASC;"
        return self.query_df(sql, tuple(params))

    def create_study_goal(self, goal_id: str, student_id: str, subject_id: str,
                          target_type: str, target_value: float, deadline: str,
                          topic_id: Optional[str] = None) -> int:
        sql = """
            INSERT INTO study_goals (goal_id, student_id, subject_id, topic_id, target_type, target_value, deadline, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'In Progress');
        """
        return self.execute_write(sql, (goal_id, student_id, subject_id, topic_id, target_type, target_value, deadline))

    def update_goal_status(self, goal_id: str, status: str) -> int:
        sql = "UPDATE study_goals SET status = ? WHERE goal_id = ?;"
        return self.execute_write(sql, (status, goal_id))

    def update_study_goal_details(self, goal_id: str, target_type: str, target_value: float, deadline: str) -> int:
        sql = "UPDATE study_goals SET target_type = ?, target_value = ?, deadline = ? WHERE goal_id = ?;"
        return self.execute_write(sql, (target_type, target_value, deadline, goal_id))

    def delete_study_goal(self, goal_id: str) -> int:
        return self.execute_write("DELETE FROM study_goals WHERE goal_id = ?;", (goal_id,))

    # -------------------------------------------------------------------------
    # Recommendations
    # -------------------------------------------------------------------------
    def get_recommendations(self, student_id: Optional[str] = None, status: Optional[str] = None) -> pd.DataFrame:
        sql = """
            SELECT r.*, t.topic_name, t.unit_name, sub.subject_name, sub.subject_code
            FROM recommendations r
            JOIN topics t ON r.topic_id = t.topic_id
            JOIN subjects sub ON t.subject_id = sub.subject_id
            WHERE 1=1
        """
        params = []
        if student_id:
            sql += " AND r.student_id = ?"
            params.append(student_id)
        if status:
            sql += " AND r.status = ?"
            params.append(status)
        sql += " ORDER BY CASE r.priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END, r.generated_at DESC;"
        return self.query_df(sql, tuple(params))

    def create_recommendation(self, recommendation_id: str, student_id: str, topic_id: str,
                              recommendation_type: str, explanation: str, priority: str) -> int:
        # Check if an active recommendation already exists for this student & topic to avoid duplicates
        existing = self.query_df(
            "SELECT recommendation_id FROM recommendations WHERE student_id = ? AND topic_id = ? AND recommendation_type = ? AND status = 'Active';",
            (student_id, topic_id, recommendation_type)
        )
        if not existing.empty:
            return 0  # Deduplicated

        sql = """
            INSERT INTO recommendations (recommendation_id, student_id, topic_id, recommendation_type, explanation, priority, status)
            VALUES (?, ?, ?, ?, ?, ?, 'Active');
        """
        return self.execute_write(sql, (recommendation_id, student_id, topic_id, recommendation_type, explanation, priority))

    def update_recommendation_status(self, recommendation_id: str, status: str) -> int:
        sql = "UPDATE recommendations SET status = ? WHERE recommendation_id = ?;"
        return self.execute_write(sql, (status, recommendation_id))


# Default repository instance
repo = Repository()
