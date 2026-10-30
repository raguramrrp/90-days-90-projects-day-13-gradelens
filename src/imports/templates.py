"""
GradeLens CSV/Excel Import Templates Generator.
Generates clean sample CSV and Excel templates for question-level marks import.
"""

import io
import pandas as pd

SAMPLE_IMPORT_DATA = [
    {
        "student_code": "STU101",
        "exam_name": "Internal Assessment 1",
        "exam_type": "Internal Assessment",
        "exam_date": "2026-09-15",
        "academic_period": "Semester 7",
        "subject_code": "CS701",
        "unit_name": "Unit 1: Data Models",
        "topic_name": "Relational Algebra",
        "question_text": "Compute Cartesian product and Theta Join on relations R and S.",
        "maximum_marks": 10.0,
        "marks_obtained": 6.5,
        "difficulty": "Medium",
        "question_type": "Long Answer",
        "answer_status": "Partially Correct",
        "time_spent_seconds": 420,
        "mistake_category": "Conceptual misunderstanding",
        "confidence_rating": "Medium",
        "remarks": "Missed condition on theta join"
    },
    {
        "student_code": "STU101",
        "exam_name": "Internal Assessment 1",
        "exam_type": "Internal Assessment",
        "exam_date": "2026-09-15",
        "academic_period": "Semester 7",
        "subject_code": "CS701",
        "unit_name": "Unit 2: SQL Mastery",
        "topic_name": "Window Functions",
        "question_text": "Write a query to calculate 3-day rolling average using OVER clause.",
        "maximum_marks": 10.0,
        "marks_obtained": 10.0,
        "difficulty": "Hard",
        "question_type": "Code",
        "answer_status": "Correct",
        "time_spent_seconds": 360,
        "mistake_category": "None",
        "confidence_rating": "High",
        "remarks": "Accurate partition and order by specification"
    },
    {
        "student_code": "STU102",
        "exam_name": "Internal Assessment 1",
        "exam_type": "Internal Assessment",
        "exam_date": "2026-09-15",
        "academic_period": "Semester 7",
        "subject_code": "CS701",
        "unit_name": "Unit 1: Data Models",
        "topic_name": "Relational Algebra",
        "question_text": "Compute Cartesian product and Theta Join on relations R and S.",
        "maximum_marks": 10.0,
        "marks_obtained": 2.0,
        "difficulty": "Medium",
        "question_type": "Long Answer",
        "answer_status": "Incorrect",
        "time_spent_seconds": 250,
        "mistake_category": "Calculation error",
        "confidence_rating": "Low",
        "remarks": "Confused projection with selection"
    }
]


def generate_sample_csv() -> str:
    """Returns sample import data as CSV string."""
    df = pd.DataFrame(SAMPLE_IMPORT_DATA)
    return df.to_csv(index=False)


def generate_sample_excel_bytes() -> bytes:
    """Returns sample import data as Excel binary bytes."""
    df = pd.DataFrame(SAMPLE_IMPORT_DATA)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Question_Marks_Template")
    return output.getvalue()


# Convenient aliases
get_csv_template = generate_sample_csv
get_excel_template = generate_sample_excel_bytes
