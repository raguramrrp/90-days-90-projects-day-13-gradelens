"""
GradeLens CSV/Excel Import Validator & Transaction Processor.
Implements strict multi-tier validation, duplicate detection, downloadable error reporting,
and atomic database transactions.
"""

import uuid
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional
from src.database.repository import Repository, repo

VALID_DIFFICULTIES = {"Easy", "Medium", "Hard"}
VALID_QUESTION_TYPES = {"MCQ", "Short Answer", "Numerical", "Long Answer", "Code"}
VALID_ANSWER_STATUSES = {"Correct", "Partially Correct", "Incorrect", "Unanswered"}
VALID_MISTAKE_CATEGORIES = {
    "Conceptual misunderstanding",
    "Calculation error",
    "Formula error",
    "Careless mistake",
    "Incomplete answer",
    "Time-management issue",
    "Unanswered question",
    "Other or unknown",
    "None"
}


def validate_import_dataframe(df: pd.DataFrame, repository: Repository = repo) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
    """
    Validates a raw imported DataFrame.
    Returns:
        valid_rows: list of clean dicts ready for insertion
        invalid_rows: list of failed rows with specific error messages
        summary: validation statistics
    """
    valid_rows: List[Dict[str, Any]] = []
    invalid_rows: List[Dict[str, Any]] = []
    duplicates_seen = set()
    duplicate_count = 0

    # Retrieve existing entities for foreign key validation
    students_df = repository.get_students()
    valid_student_codes = set(students_df["student_code"].dropna()) if not students_df.empty else set()
    code_to_student_id = dict(zip(students_df["student_code"], students_df["student_id"])) if not students_df.empty else {}

    subjects_df = repository.get_subjects()
    valid_subject_codes = set(subjects_df["subject_code"].dropna()) if not subjects_df.empty else set()
    code_to_subject_id = dict(zip(subjects_df["subject_code"], subjects_df["subject_id"])) if not subjects_df.empty else {}

    required_columns = ["student_code", "subject_code", "topic_name", "exam_name", "maximum_marks", "marks_obtained"]

    # Check missing header columns
    missing_cols = [c for c in required_columns if c not in df.columns]
    if missing_cols:
        return [], [{"row_number": 0, "error": f"Missing required columns in file: {', '.join(missing_cols)}"}], {
            "total_rows": len(df),
            "valid_count": 0,
            "invalid_count": len(df),
            "duplicate_count": 0
        }

    for idx, row in df.iterrows():
        row_num = idx + 2  # 1-indexed with header considered row 1
        errors = []

        # 1. Check required non-nulls
        student_code = str(row.get("student_code", "")).strip()
        subject_code = str(row.get("subject_code", "")).strip()
        topic_name = str(row.get("topic_name", "")).strip()
        exam_name = str(row.get("exam_name", "")).strip()

        if not student_code:
            errors.append("Missing student_code")
        if not subject_code:
            errors.append("Missing subject_code")
        if not topic_name:
            errors.append("Missing topic_name")
        if not exam_name:
            errors.append("Missing exam_name")

        # 2. Check student & subject existence if DB is seeded
        if valid_student_codes and student_code not in valid_student_codes:
            errors.append(f"Student code '{student_code}' does not exist in database.")
        if valid_subject_codes and subject_code not in valid_subject_codes:
            errors.append(f"Subject code '{subject_code}' does not exist in database.")

        # 3. Numeric checks
        try:
            max_marks = float(row.get("maximum_marks", 0))
            if max_marks <= 0:
                errors.append("maximum_marks must be greater than 0")
        except (ValueError, TypeError):
            max_marks = 0.0
            errors.append("maximum_marks must be a valid number")

        try:
            marks_obtained = float(row.get("marks_obtained", 0))
            if marks_obtained < 0:
                errors.append("marks_obtained cannot be negative")
            elif max_marks > 0 and marks_obtained > max_marks:
                errors.append(f"marks_obtained ({marks_obtained}) exceeds maximum_marks ({max_marks})")
        except (ValueError, TypeError):
            marks_obtained = 0.0
            errors.append("marks_obtained must be a valid number")

        # 4. Difficulty check
        difficulty = str(row.get("difficulty", "Medium")).strip().capitalize()
        if difficulty not in VALID_DIFFICULTIES:
            errors.append(f"Invalid difficulty '{difficulty}'. Allowed: {', '.join(VALID_DIFFICULTIES)}")

        # 5. Question Type check
        q_type = str(row.get("question_type", "Short Answer")).strip()
        if q_type not in VALID_QUESTION_TYPES:
            # Tolerant match
            match = next((qt for qt in VALID_QUESTION_TYPES if qt.lower() == q_type.lower()), None)
            if match:
                q_type = match
            else:
                errors.append(f"Invalid question_type '{q_type}'. Allowed: {', '.join(VALID_QUESTION_TYPES)}")

        # 6. Answer Status check
        status = str(row.get("answer_status", "Correct")).strip()
        if status not in VALID_ANSWER_STATUSES:
            match = next((st for st in VALID_ANSWER_STATUSES if st.lower() == status.lower()), None)
            if match:
                status = match
            else:
                errors.append(f"Invalid answer_status '{status}'. Allowed: {', '.join(VALID_ANSWER_STATUSES)}")

        # 7. Mistake category check
        mistake = str(row.get("mistake_category", "None")).strip()
        if mistake and mistake not in VALID_MISTAKE_CATEGORIES:
            mistake = "Other or unknown"

        # 8. Duplicate check within file
        question_text = str(row.get("question_text", f"Question on {topic_name}")).strip()
        dup_key = (student_code, exam_name, question_text)
        if dup_key in duplicates_seen:
            duplicate_count += 1
            errors.append("Duplicate response for the same student, exam, and question.")
        else:
            duplicates_seen.add(dup_key)

        if errors:
            invalid_record = row.to_dict()
            invalid_record["row_number"] = row_num
            invalid_record["error_reasons"] = "; ".join(errors)
            invalid_rows.append(invalid_record)
        else:
            valid_record = {
                "student_code": student_code,
                "student_id": code_to_student_id.get(student_code, student_code),
                "subject_code": subject_code,
                "subject_id": code_to_subject_id.get(subject_code, subject_code),
                "topic_name": topic_name,
                "unit_name": str(row.get("unit_name", "Unit 1")).strip(),
                "exam_name": exam_name,
                "exam_type": str(row.get("exam_type", "Internal Assessment")).strip(),
                "exam_date": str(row.get("exam_date", "2026-10-01")).strip(),
                "academic_period": str(row.get("academic_period", "Semester 7")).strip(),
                "question_text": question_text,
                "maximum_marks": max_marks,
                "marks_obtained": marks_obtained,
                "difficulty": difficulty,
                "question_type": q_type,
                "answer_status": status,
                "time_spent_seconds": int(row.get("time_spent_seconds", 120)) if pd.notna(row.get("time_spent_seconds")) else 120,
                "mistake_category": mistake,
                "confidence_rating": str(row.get("confidence_rating", "Medium")).strip(),
                "remarks": str(row.get("remarks", "")).strip() if pd.notna(row.get("remarks")) else ""
            }
            valid_rows.append(valid_record)

    summary = {
        "total_rows": len(df),
        "valid_count": len(valid_rows),
        "invalid_count": len(invalid_rows),
        "duplicate_count": duplicate_count
    }
    return valid_rows, invalid_rows, summary


def commit_imported_records(valid_rows: List[Dict[str, Any]], repository: Repository = repo) -> int:
    """
    Inserts validated rows into the database inside an atomic transaction.
    Creates exams, topics, questions, attempts, and question_responses as needed.
    """
    if not valid_rows:
        return 0

    conn = repository.mgr.get_connection()
    inserted_count = 0

    try:
        cursor = conn.cursor()

        # Track created topics and exams in memory to minimize redundant lookups
        created_topics = {}
        created_exams = {}

        for r in valid_rows:
            # 1. Ensure Topic exists
            subject_id = r["subject_id"]
            topic_name = r["topic_name"]
            topic_key = (subject_id, topic_name)

            if topic_key not in created_topics:
                cursor.execute("SELECT topic_id FROM topics WHERE subject_id = ? AND topic_name = ?;", (subject_id, topic_name))
                row = cursor.fetchone()
                if row:
                    topic_id = row[0]
                else:
                    topic_id = f"top_{uuid.uuid4().hex[:8]}"
                    cursor.execute(
                        "INSERT INTO topics (topic_id, subject_id, unit_name, topic_name) VALUES (?, ?, ?, ?);",
                        (topic_id, subject_id, r["unit_name"], topic_name)
                    )
                created_topics[topic_key] = topic_id
            else:
                topic_id = created_topics[topic_key]

            # 2. Ensure Exam exists
            exam_name = r["exam_name"]
            if exam_name not in created_exams:
                cursor.execute("SELECT exam_id FROM exams WHERE exam_name = ?;", (exam_name,))
                row = cursor.fetchone()
                if row:
                    exam_id = row[0]
                else:
                    exam_id = f"ex_{uuid.uuid4().hex[:8]}"
                    cursor.execute(
                        """
                        INSERT INTO exams (exam_id, exam_name, exam_type, exam_date, academic_period, maximum_marks)
                        VALUES (?, ?, ?, ?, ?, 100.0);
                        """,
                        (exam_id, exam_name, r["exam_type"], r["exam_date"], r["academic_period"])
                    )
                created_exams[exam_name] = exam_id
            else:
                exam_id = created_exams[exam_name]

            # 3. Create Question
            question_id = f"q_{uuid.uuid4().hex[:8]}"
            cursor.execute(
                """
                INSERT INTO questions (question_id, exam_id, subject_id, topic_id, question_text, maximum_marks, difficulty, question_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (question_id, exam_id, subject_id, topic_id, r["question_text"], r["maximum_marks"], r["difficulty"], r["question_type"])
            )

            # 4. Ensure Attempt exists
            student_id = r["student_id"]
            cursor.execute("SELECT attempt_id, total_marks, marks_obtained FROM attempts WHERE student_id = ? AND exam_id = ?;", (student_id, exam_id))
            att_row = cursor.fetchone()
            if att_row:
                attempt_id = att_row[0]
                new_total = float(att_row[1]) + r["maximum_marks"]
                new_obtained = float(att_row[2]) + r["marks_obtained"]
                cursor.execute(
                    "UPDATE attempts SET total_marks = ?, marks_obtained = ? WHERE attempt_id = ?;",
                    (new_total, new_obtained, attempt_id)
                )
            else:
                attempt_id = f"att_{uuid.uuid4().hex[:8]}"
                cursor.execute(
                    """
                    INSERT INTO attempts (attempt_id, student_id, exam_id, total_marks, marks_obtained, attempt_date)
                    VALUES (?, ?, ?, ?, ?, ?);
                    """,
                    (attempt_id, student_id, exam_id, r["maximum_marks"], r["marks_obtained"], r["exam_date"])
                )

            # 5. Insert Question Response
            response_id = f"resp_{uuid.uuid4().hex[:8]}"
            cursor.execute(
                """
                INSERT INTO question_responses (
                    response_id, attempt_id, question_id, marks_obtained, maximum_marks,
                    answer_status, time_spent_seconds, mistake_category, confidence_rating, remarks
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    response_id, attempt_id, question_id, r["marks_obtained"], r["maximum_marks"],
                    r["answer_status"], r["time_spent_seconds"], r["mistake_category"],
                    r["confidence_rating"], r["remarks"]
                )
            )
            inserted_count += 1

        conn.commit()
        return inserted_count
    except Exception as exc:
        conn.rollback()
        raise exc
    finally:
        conn.close()
