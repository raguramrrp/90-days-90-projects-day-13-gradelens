"""
GradeLens View: Exam Manager.
Full examination lifecycle management: list, add, edit, delete with confirmation,
and individual question-level result entry.
"""

import uuid
import streamlit as st
import pandas as pd
from src.database.repository import Repository, repo
from app.components.metrics import render_section_header, render_alert_box


def render_exam_manager_view(repository: Repository = repo):
    st.markdown(
        """
        <div style="margin-bottom: 16px;">
            <div style="font-size: 1.45rem; font-weight: 800; color: #102B50; letter-spacing: -0.02em;">
                Exam Manager
            </div>
            <div style="color: #64748B; font-size: 0.86rem; margin-top: 2px;">
                Configure assessments, manage syllabi schedules, and record question-level marks.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    tab_list, tab_add, tab_record = st.tabs([
        "Examinations List",
        "Add / Edit Examination",
        "Record Question Marks"
    ])

    # -------------------------------------------------------------------------
    # TAB 1: EXAMINATIONS LIST
    # -------------------------------------------------------------------------
    with tab_list:
        render_section_header("Active & Completed Assessments")

        col_search, col_filter = st.columns([3, 2])
        with col_search:
            search_query = st.text_input("Search Examination", placeholder="Search by exam name...", label_visibility="collapsed")
        with col_filter:
            filter_type = st.selectbox("Filter Type", options=["All Types", "Internal Assessment", "Model Examination", "Quiz", "Semester Examination"], label_visibility="collapsed")

        exams_df = repository.get_exams()
        if not exams_df.empty:
            filtered = exams_df.copy()
            if search_query:
                filtered = filtered[filtered["exam_name"].str.contains(search_query, case=False, na=False)]
            if filter_type != "All Types":
                filtered = filtered[filtered["exam_type"] == filter_type]

            for _, ex_row in filtered.iterrows():
                ex_id = ex_row["exam_id"]
                with st.container():
                    c_info, c_act = st.columns([5, 2])
                    with c_info:
                        st.markdown(
                            f"""
                            <div style="background:#FFFFFF; border:1px solid #E2EAF3; border-radius:6px; padding:12px 16px; margin-bottom:8px;">
                                <div style="display:flex; justify-content:space-between; align-items:center;">
                                    <span style="font-weight:700; font-size:0.95rem; color:#102B50;">{ex_row['exam_name']}</span>
                                    <span style="background:#EAF3FF; color:#2878E5; padding:2px 8px; border-radius:4px; font-size:0.75rem; font-weight:600;">{ex_row['exam_type']}</span>
                                </div>
                                <div style="font-size:0.8rem; color:#64748B; margin-top:4px;">
                                    Date: <strong>{ex_row['exam_date']}</strong> &bull; Period: {ex_row['academic_period']} &bull; Max Marks: <strong>{ex_row['maximum_marks']}</strong> &bull; Class: {ex_row.get('class_name', 'All Classes')}
                                </div>
                                <div style="font-size:0.78rem; color:#94A3B8; margin-top:3px;">
                                    Scope: {ex_row.get('description', 'Standard Syllabus')}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    with c_act:
                        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
                        c_btn1, c_btn2 = st.columns(2)
                        with c_btn1:
                            if st.button("Edit", key=f"edit_ex_{ex_id}", use_container_width=True):
                                st.session_state["edit_exam_target"] = ex_id
                        with c_btn2:
                            if st.button("Delete", key=f"del_ex_{ex_id}", use_container_width=True):
                                st.session_state["confirm_del_exam"] = ex_id

                    # Delete Confirmation Dialog
                    if st.session_state.get("confirm_del_exam") == ex_id:
                        st.warning(f"Are you sure you want to delete '{ex_row['exam_name']}'? All associated attempts and questions will be removed.")
                        c_conf1, c_conf2 = st.columns(2)
                        with c_conf1:
                            if st.button("Confirm Delete", key=f"conf_del_{ex_id}", type="primary"):
                                repository.delete_exam(ex_id)
                                del st.session_state["confirm_del_exam"]
                                st.success("Examination deleted.")
                                st.rerun()
                        with c_conf2:
                            if st.button("Cancel", key=f"canc_del_{ex_id}"):
                                del st.session_state["confirm_del_exam"]
                                st.rerun()
        else:
            st.info("No examinations registered yet.")

    # -------------------------------------------------------------------------
    # TAB 2: ADD / EDIT EXAMINATION
    # -------------------------------------------------------------------------
    with tab_add:
        edit_target = st.session_state.get("edit_exam_target")
        existing_data = repository.get_exam_by_id(edit_target) if edit_target else None

        title_text = f"Edit Examination: {existing_data['exam_name']}" if existing_data else "Create New Examination"
        render_section_header(title_text)

        with st.form("exam_form"):
            name_val = existing_data["exam_name"] if existing_data else ""
            type_val = existing_data["exam_type"] if existing_data else "Internal Assessment"
            type_idx = ["Internal Assessment", "Model Examination", "Semester Examination", "Quiz", "Assignment", "Practice Test"].index(type_val) if type_val in ["Internal Assessment", "Model Examination", "Semester Examination", "Quiz", "Assignment", "Practice Test"] else 0

            max_val = float(existing_data["maximum_marks"]) if existing_data else 50.0
            period_val = existing_data["academic_period"] if existing_data else "Semester 7"
            desc_val = existing_data["description"] if existing_data and existing_data["description"] else ""

            ex_name = st.text_input("Examination Name", value=name_val)
            c1, c2, c3 = st.columns(3)
            with c1:
                ex_type = st.selectbox("Assessment Type", options=["Internal Assessment", "Model Examination", "Semester Examination", "Quiz", "Assignment", "Practice Test"], index=type_idx)
            with c2:
                ex_date = st.date_input("Examination Date")
            with c3:
                ex_max = st.number_input("Maximum Possible Marks", min_value=5.0, max_value=500.0, value=max_val, step=5.0)

            ex_period = st.text_input("Academic Period / Semester", value=period_val)
            ex_desc = st.text_area("Syllabus & Units Covered", value=desc_val)

            btn_label = "Update Examination" if existing_data else "Save Examination"
            if st.form_submit_button(btn_label, type="primary"):
                if not ex_name.strip():
                    st.error("Examination name is required.")
                else:
                    if existing_data:
                        repository.update_exam(
                            exam_id=edit_target,
                            exam_name=ex_name,
                            exam_type=ex_type,
                            exam_date=str(ex_date),
                            academic_period=ex_period,
                            maximum_marks=ex_max,
                            description=ex_desc
                        )
                        del st.session_state["edit_exam_target"]
                        st.success("Examination updated successfully!")
                    else:
                        new_id = f"ex_{uuid.uuid4().hex[:8]}"
                        repository.create_exam(
                            exam_id=new_id,
                            exam_name=ex_name,
                            exam_type=ex_type,
                            exam_date=str(ex_date),
                            academic_period=ex_period,
                            maximum_marks=ex_max,
                            description=ex_desc
                        )
                        st.success("Examination created successfully!")
                    st.rerun()

    # -------------------------------------------------------------------------
    # TAB 3: RECORD QUESTION MARKS
    # -------------------------------------------------------------------------
    with tab_record:
        render_section_header("Question-Level Performance Entry", "Record individual student question outcomes with cognitive mistake attribution.")

        students_df = repository.get_students()
        exams_df = repository.get_exams()
        subjects_df = repository.get_subjects()

        if students_df.empty or exams_df.empty or subjects_df.empty:
            st.warning("Ensure students, exams, and subjects exist before recording marks.")
        else:
            with st.form("manual_entry_form_clean"):
                c_s1, c_s2 = st.columns(2)
                with c_s1:
                    stu_opts = {r["student_id"]: f"{r['name']} ({r['student_code']})" for _, r in students_df.iterrows()}
                    sel_stu = st.selectbox("Student Candidate", options=list(stu_opts.keys()), format_func=lambda k: stu_opts[k])

                    sub_opts = {r["subject_id"]: f"{r['subject_code']} - {r['subject_name']}" for _, r in subjects_df.iterrows()}
                    sel_sub = st.selectbox("Curriculum Subject", options=list(sub_opts.keys()), format_func=lambda k: sub_opts[k])

                    topics_df = repository.get_topics(subject_id=sel_sub)
                    top_opts = {r["topic_id"]: f"{r['unit_name']} - {r['topic_name']}" for _, r in topics_df.iterrows()} if not topics_df.empty else {}
                    sel_top = st.selectbox("Topic Concept", options=list(top_opts.keys()), format_func=lambda k: top_opts[k]) if top_opts else None

                with c_s2:
                    ex_opts = {r["exam_id"]: f"{r['exam_name']} ({r['exam_date']})" for _, r in exams_df.iterrows()}
                    sel_ex = st.selectbox("Examination", options=list(ex_opts.keys()), format_func=lambda k: ex_opts[k])

                    q_text = st.text_input("Question Reference or Prompt", value="Question 1")
                    diff = st.selectbox("Question Difficulty", options=["Easy", "Medium", "Hard"], index=1)
                    q_type = st.selectbox("Question Type", options=["Short Answer", "MCQ", "Numerical", "Long Answer", "Code"])

                c_m1, c_m2, c_st = st.columns(3)
                with c_m1:
                    max_m = st.number_input("Maximum Marks", min_value=1.0, max_value=100.0, value=10.0, step=1.0)
                with c_m2:
                    obt_m = st.number_input("Marks Awarded", min_value=0.0, max_value=100.0, value=7.5, step=0.5)
                with c_st:
                    status = st.selectbox("Answer Status", options=["Correct", "Partially Correct", "Incorrect", "Unanswered"])

                c_diag1, c_diag2, c_diag3 = st.columns(3)
                with c_diag1:
                    mistake = st.selectbox("Mistake Category (if mark deducted)", options=[
                        "None",
                        "Conceptual misunderstanding",
                        "Calculation error",
                        "Formula error",
                        "Careless mistake",
                        "Incomplete answer",
                        "Time-management issue",
                        "Unanswered question",
                        "Other or unknown"
                    ])
                with c_diag2:
                    conf = st.selectbox("Self-Reported Confidence", options=["High", "Medium", "Low"], index=1)
                with c_diag3:
                    time_s = st.number_input("Time Spent (Seconds)", min_value=10, max_value=7200, value=180, step=10)

                remarks = st.text_input("Examiner Notes / Feedback", "")

                if st.form_submit_button("Save Question Result", type="primary"):
                    if obt_m > max_m:
                        st.error("Marks awarded cannot exceed maximum marks.")
                    elif not sel_top:
                        st.error("Please select a topic.")
                    else:
                        q_id = f"q_{uuid.uuid4().hex[:8]}"
                        repository.create_question(
                            question_id=q_id,
                            exam_id=sel_ex,
                            subject_id=sel_sub,
                            topic_id=sel_top,
                            question_text=q_text,
                            maximum_marks=max_m,
                            difficulty=diff,
                            question_type=q_type
                        )
                        att_id = f"att_{sel_stu}_{sel_ex}"
                        repository.record_attempt(
                            attempt_id=att_id,
                            student_id=sel_stu,
                            exam_id=sel_ex,
                            total_marks=max_m,
                            marks_obtained=obt_m,
                            attempt_date=str(pd.Timestamp.now().date())
                        )
                        resp_id = f"resp_{uuid.uuid4().hex[:8]}"
                        repository.record_question_response(
                            response_id=resp_id,
                            attempt_id=att_id,
                            question_id=q_id,
                            marks_obtained=obt_m,
                            maximum_marks=max_m,
                            answer_status=status,
                            time_spent_seconds=time_s,
                            mistake_category=mistake,
                            confidence_rating=conf,
                            remarks=remarks
                        )
                        st.success("Question marks recorded successfully!")
                        st.rerun()
