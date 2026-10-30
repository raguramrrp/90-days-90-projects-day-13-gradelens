"""
GradeLens Faculty View: Student Performance Profile.
Granular individual student analytics, examination trajectory, topic diagnostics, and faculty advisory logs.
Strict light design system: #F5F8FC / #FFFFFF / #102B50 / #2878E5, zero emojis.
"""

import uuid
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.database.repository import Repository, repo
from src.analytics.calculations import safe_percentage, calculate_student_ranking
from src.analytics.weakness_engine import TopicWeaknessEngine, weakness_engine
from app.components.metrics import render_kpi_card, render_section_header, render_alert_box
from app.styles import get_badge_html
from app.auth import get_current_user_context


def render_student_performance_view(repository: Repository = repo):
    user = get_current_user_context(repository)
    st.markdown(
        """
        <div style="margin-bottom: 20px;">
            <h1 style="font-size: 1.65rem; font-weight: 700; color: #102B50; margin: 0 0 4px 0;">
                Student Performance Profile
            </h1>
            <p style="color: #64748B; font-size: 0.88rem; margin: 0;">
                Granular examination history, topic-level diagnostics, and faculty academic advisory notes.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    students_df = repository.get_students()
    if students_df.empty:
        st.info("No student records found.")
        return

    stu_opts = {r["student_id"]: f"{r['name']} ({r['student_code']}) — {r['class_name']}" for _, r in students_df.iterrows()}
    sel_sid = st.selectbox("Select Student to Inspect", options=list(stu_opts.keys()), format_func=lambda k: stu_opts[k])

    sel_student = students_df[students_df["student_id"] == sel_sid].iloc[0]

    # Fetch attempts and responses for this student
    attempts_df = repository.get_attempts(student_id=sel_sid)
    responses_df = repository.get_question_responses(student_id=sel_sid)

    if attempts_df.empty or responses_df.empty:
        st.info("No assessment records found for this student.")
        return

    # Compute KPIs
    total_obtained = float(attempts_df["marks_obtained"].sum())
    total_possible = float(attempts_df["total_marks"].sum())
    overall_acc = safe_percentage(total_obtained, total_possible)
    marks_lost = total_possible - total_obtained

    all_attempts = repository.get_attempts()
    ranking_df = calculate_student_ranking(all_attempts, anonymize=False)
    stu_rank_row = ranking_df[ranking_df["student_id"] == sel_sid]
    rank_str = f"#{int(stu_rank_row['rank'].iloc[0])} of {len(ranking_df)}" if not stu_rank_row.empty else "N/A"

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card("Overall Accuracy", f"{overall_acc:.1f}%", f"{total_obtained:.1f} of {total_possible:.1f} marks")
    with c2:
        render_kpi_card("Assessments", str(len(attempts_df)), f"{len(responses_df)} question responses")
    with c3:
        render_kpi_card("Marks Lost", f"{marks_lost:.1f}", "Total marks deducted")
    with c4:
        render_kpi_card("Class Standing", rank_str, "Cohort percentile ranking")

    # Examination Trajectory Chart
    render_section_header("Assessment Score Trajectory", "Individual score percentage across completed assessments.")
    sorted_attempts = attempts_df.sort_values(by="exam_date")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=sorted_attempts["exam_date"],
        y=sorted_attempts["percentage"],
        mode="lines+markers+text",
        name="Student Score %",
        line=dict(color="#2878E5", width=2.5),
        marker=dict(size=8, color="#2878E5", line=dict(color="#FFFFFF", width=1.5)),
        text=[f"{p:.1f}%" for p in sorted_attempts["percentage"]],
        textposition="top center",
        textfont=dict(color="#102B50", size=10)
    ))
    fig.add_hline(
        y=60.0,
        line_dash="dash",
        line_color="#E35D63",
        annotation_text="Passing Benchmark (60%)",
        annotation_position="bottom right",
        annotation_font=dict(color="#E35D63", size=10)
    )
    fig.update_layout(
        template="plotly_white",
        margin=dict(l=0, r=20, t=20, b=10),
        height=260,
        xaxis_title="Assessment Date",
        yaxis_title="Score %",
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(color="#102B50", family="Inter, sans-serif"),
        yaxis=dict(range=[0, 110], gridcolor="#E2EAF3", linecolor="#E2EAF3"),
        xaxis=dict(gridcolor="#E2EAF3", linecolor="#E2EAF3")
    )
    st.plotly_chart(fig, use_container_width=True)

    # Topic Diagnosis Breakdown
    render_section_header("Topic Diagnostics & Weakness Analysis", "Automated weakness classifications generated for this student.")
    analysis_df = weakness_engine.analyze_all_topics(responses_df)
    if not analysis_df.empty:
        disp_topics = analysis_df[["topic_name", "subject_name", "classification", "accuracy_pct", "marks_lost", "explanation"]].copy()
        disp_topics.columns = ["Topic", "Subject", "Status", "Accuracy %", "Marks Lost", "Evidence Diagnostic"]
        st.dataframe(disp_topics, use_container_width=True, hide_index=True)
    else:
        st.info("No topic diagnostics generated.")

    # Faculty Academic Advisory Note Entry
    render_section_header("Academic Advisory Notes & Recommendations", "Record formal faculty intervention notes and remedial actions.")
    col_note_form, col_note_list = st.columns([1, 1.8])

    with col_note_form:
        with st.form("faculty_note_form"):
            rec_text = st.text_area("Advisory Recommendation", "Attend faculty remedial clinic on relational joins and review homework problem set.")
            prio = st.selectbox("Intervention Priority", ["High", "Medium", "Low"], index=0)

            if st.form_submit_button("Record Recommendation", type="primary", use_container_width=True):
                rec_id = f"rec_{uuid.uuid4().hex[:8]}"
                repository.create_recommendation(
                    rec_id=rec_id,
                    student_id=sel_sid,
                    topic_id=None,
                    recommendation_text=rec_text,
                    priority=prio
                )
                st.success("Advisory note saved to student record.")
                st.rerun()

    with col_note_list:
        recs_df = repository.get_recommendations(student_id=sel_sid)
        if not recs_df.empty:
            for _, r in recs_df.iterrows():
                alert_type = "critical" if r["priority"] == "High" else ("warning" if r["priority"] == "Medium" else "info")
                render_alert_box(f"Recommendation (Priority: {r['priority']}) — Status: {r['status']}", r["recommendation_text"], alert_type=alert_type)
        else:
            st.info("No prior advisory recommendations recorded for this student.")
