"""
GradeLens Authentication & Role-Based Session State Management.
Provides safe demonstration authentication and role authorization without hardcoded credentials.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional
from src.database.repository import Repository, repo


def init_session_state(repository: Repository = repo):
    """Initializes GradeLens session state variables."""
    if "user_role" not in st.session_state:
        st.session_state.user_role = "Student"

    if "current_student_id" not in st.session_state:
        students = repository.get_students()
        if not students.empty:
            st.session_state.current_student_id = students.iloc[0]["student_id"]
        else:
            st.session_state.current_student_id = "stu_01"

    if "current_faculty_id" not in st.session_state:
        faculty = repository.get_faculty()
        if not faculty.empty:
            st.session_state.current_faculty_id = faculty.iloc[0]["faculty_id"]
        else:
            st.session_state.current_faculty_id = "fac_01"


def get_current_user_context(repository: Repository = repo) -> Dict[str, Any]:
    """Retrieves current authenticated profile based on active role."""
    init_session_state(repository)
    role = st.session_state.user_role

    if role == "Student":
        student_id = st.session_state.current_student_id
        student = repository.get_student_by_id(student_id)
        return {
            "role": "Student",
            "id": student_id,
            "name": student.get("name", "Student") if student else "Student",
            "code": student.get("student_code", "") if student else "",
            "department": student.get("department", "") if student else "",
            "class_id": student.get("class_id", "") if student else ""
        }
    else:
        faculty_id = st.session_state.current_faculty_id
        faculty_df = repository.get_faculty()
        f_row = faculty_df[faculty_df["faculty_id"] == faculty_id]
        name = f_row.iloc[0]["name"] if not f_row.empty else "Faculty Member"
        dept = f_row.iloc[0]["department"] if not f_row.empty else "AI & DS"
        return {
            "role": "Faculty",
            "id": faculty_id,
            "name": name,
            "code": "FACULTY",
            "department": dept,
            "class_id": "cls_ai_a"
        }
