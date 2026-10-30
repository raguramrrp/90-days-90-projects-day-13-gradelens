"""
GradeLens View: Study Goals.
Manage academic target benchmarks, score goals, deadlines, and milestone completion.
Strict light design system: #F5F8FC / #FFFFFF / #102B50 / #2878E5, zero emojis.
"""

import uuid
import streamlit as st
import pandas as pd
from src.database.repository import Repository, repo
from app.components.metrics import render_kpi_card, render_section_header, render_progress_bar
from app.auth import get_current_user_context


def render_study_goals_view(repository: Repository = repo):
    user = get_current_user_context(repository)
    st.markdown(
        """
        <div style="margin-bottom: 20px;">
            <h1 style="font-size: 1.65rem; font-weight: 700; color: #102B50; margin: 0 0 4px 0;">
                Study Goals
            </h1>
            <p style="color: #64748B; font-size: 0.88rem; margin: 0;">
                Define target score benchmarks, establish deadlines, and monitor your path to academic mastery.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    student_id = user["id"] if user["role"] == "Student" else None
    if not student_id:
        st.info("Please select an active student from the sidebar to view personal study goals.")
        return

    goals_df = repository.get_study_goals(student_id=student_id)
    responses_df = repository.get_question_responses(student_id=student_id)

    # Calculate actual current scores per subject for goal progress tracking
    subj_perf = {}
    if not responses_df.empty:
        s_grp = responses_df.groupby("subject_name").agg(
            obtained=("marks_obtained", "sum"),
            maximum=("maximum_marks", "sum")
        ).reset_index()
        for _, r in s_grp.iterrows():
            subj_perf[r["subject_name"]] = (r["obtained"] / r["maximum"] * 100.0) if r["maximum"] > 0 else 0.0

    # Summary KPI row
    total_goals = len(goals_df) if not goals_df.empty else 0
    achieved_goals = (goals_df["status"] == "Achieved").sum() if not goals_df.empty else 0
    in_progress = (goals_df["status"] == "In Progress").sum() if not goals_df.empty else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card("Total Goals", str(total_goals), "Academic targets set")
    with c2:
        render_kpi_card("Achieved", str(achieved_goals), "Target verified reached")
    with c3:
        render_kpi_card("In Progress", str(in_progress), "Currently tracked")
    with c4:
        completion_rate = (achieved_goals / total_goals * 100.0) if total_goals > 0 else 0.0
        render_kpi_card("Goal Attainment", f"{completion_rate:.1f}%", "Overall success rate")

    render_section_header("Goal Tracker & Milestones", "Active benchmarks compared against current academic standing.")

    col_create, col_display = st.columns([1, 2])

    with col_create:
        st.markdown("<div style='font-weight:600; font-size:0.88rem; color:#102B50; margin-bottom:8px;'>Set New Study Goal</div>", unsafe_allow_html=True)
        with st.form("create_goal_form"):
            subjects_df = repository.get_subjects()
            s_opts = {r["subject_id"]: f"{r['subject_code']} - {r['subject_name']}" for _, r in subjects_df.iterrows()} if not subjects_df.empty else {}
            sel_subject = st.selectbox("Target Subject", options=list(s_opts.keys()), format_func=lambda k: s_opts[k])

            # Optional topic
            topics_df = repository.get_topics(subject_id=sel_subject)
            t_opts = {"all": "Entire Subject Curriculum"}
            if not topics_df.empty:
                for _, r in topics_df.iterrows():
                    t_opts[r["topic_id"]] = r["topic_name"]
            sel_topic = st.selectbox("Curriculum Scope", options=list(t_opts.keys()), format_func=lambda k: t_opts[k])

            target_pct = st.slider("Target Score Percentage", min_value=50.0, max_value=100.0, value=85.0, step=1.0)
            target_date = st.date_input("Target Completion Date", value=pd.Timestamp.now().date() + pd.Timedelta(days=30))

            if st.form_submit_button("Save Goal", type="primary", use_container_width=True):
                gid = f"goal_{uuid.uuid4().hex[:8]}"
                chosen_topic_id = None if sel_topic == "all" else sel_topic
                repository.create_study_goal(
                    goal_id=gid,
                    student_id=student_id,
                    subject_id=sel_subject,
                    target_type="Subject Target",
                    target_value=target_pct,
                    deadline=str(target_date),
                    topic_id=chosen_topic_id
                )
                st.success("Study goal saved.")
                st.rerun()

    with col_display:
        st.markdown("<div style='font-weight:600; font-size:0.88rem; color:#102B50; margin-bottom:8px;'>Active Study Targets</div>", unsafe_allow_html=True)
        if not goals_df.empty:
            for _, row in goals_df.iterrows():
                gid = row["goal_id"]
                s_name = row.get("subject_name", "Curriculum Subject")
                t_name = row.get("topic_name") or "Entire Curriculum"
                tgt_pct = float(row.get("target_value", row.get("target_percentage", 85.0)))
                deadline_str = str(row.get("deadline", row.get("target_date", "Ongoing")))
                status = row.get("status", "In Progress")
                curr_pct = subj_perf.get(s_name, 0.0)

                status_color = "#16A58A" if status == "Achieved" or status == "Completed" else ("#2878E5" if status == "In Progress" else "#64748B")

                with st.container():
                    c_info, c_action = st.columns([3.5, 1.2])
                    with c_info:
                        card_html = (
                            f'<div style="background-color:#FFFFFF; border:1px solid #E2EAF3; border-radius:4px; padding:12px 14px; margin-bottom:8px;">'
                            f'<div style="display:flex; justify-content:space-between; align-items:center;">'
                            f'<span style="font-weight:600; font-size:0.92rem; color:#102B50;">{s_name}</span>'
                            f'<span style="font-size:0.75rem; font-weight:600; color:{status_color}; background-color:#F5F8FC; padding:2px 8px; border-radius:3px; border:1px solid #E2EAF3;">{status}</span>'
                            f'</div>'
                            f'<div style="font-size:0.8rem; color:#64748B; margin-top:2px; margin-bottom:8px;">Scope: {t_name} &bull; Deadline: {deadline_str}</div>'
                        )
                        st.markdown(card_html, unsafe_allow_html=True)
                        render_progress_bar(f"Current {curr_pct:.1f}% vs Target {tgt_pct:.1f}%", (curr_pct / tgt_pct * 100.0) if tgt_pct > 0 else 0, color="#2878E5" if curr_pct < tgt_pct else "#16A58A")
                        st.markdown('</div>', unsafe_allow_html=True)

                    with c_action:
                        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
                        if status == "In Progress":
                            if st.button("Mark Achieved", key=f"btn_achieve_{gid}", use_container_width=True):
                                repository.update_goal_status(gid, "Completed")
                                st.rerun()
                        else:
                            if st.button("Reactivate", key=f"btn_reactivate_{gid}", use_container_width=True):
                                repository.update_goal_status(gid, "In Progress")
                                st.rerun()

                        if st.button("Delete Goal", key=f"btn_del_goal_{gid}", use_container_width=True):
                            repository.delete_study_goal(gid)
                            st.rerun()
        else:
            st.info("No study goals established yet. Use the form on the left to set your first benchmark.")
