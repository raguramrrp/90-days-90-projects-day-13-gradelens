"""
GradeLens Faculty View: Faculty Dashboard.
High-level cohort intelligence, performance distributions, class averages, and curriculum difficulty patterns.
Strict light design system: #F5F8FC / #FFFFFF / #102B50 / #2878E5, zero emojis.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from src.database.repository import Repository, repo
from src.analytics.calculations import safe_percentage, calculate_student_ranking
from src.analytics.weakness_engine import TopicWeaknessEngine, weakness_engine
from app.components.metrics import render_kpi_card, render_section_header
from app.auth import get_current_user_context


def render_faculty_dashboard_view(repository: Repository = repo):
    user = get_current_user_context(repository)
    st.markdown(
        """
        <div style="margin-bottom: 20px;">
            <h1 style="font-size: 1.65rem; font-weight: 700; color: #102B50; margin: 0 0 4px 0;">
                Faculty Dashboard
            </h1>
            <p style="color: #64748B; font-size: 0.88rem; margin: 0;">
                Cohort-wide performance benchmarks, score distributions, and curriculum difficulty patterns.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    all_attempts = repository.get_attempts()
    all_responses = repository.get_question_responses()
    all_students = repository.get_students()

    if all_attempts.empty or all_responses.empty:
        st.info("No cohort records available for faculty analytics.")
        return

    # 1. Class-Level KPIs
    class_obtained = float(all_attempts["marks_obtained"].sum())
    class_total = float(all_attempts["total_marks"].sum())
    class_avg_pct = safe_percentage(class_obtained, class_total)
    total_students = all_students["student_id"].nunique()
    total_exams = all_attempts["exam_id"].nunique()

    # Identify at-risk count
    student_rankings = calculate_student_ranking(all_attempts, anonymize=False)
    at_risk_count = 0
    for _, stu_row in student_rankings.iterrows():
        sid = stu_row["student_id"]
        pct = stu_row["percentage"]
        stu_resps = all_responses[all_responses["student_id"] == sid]
        t_diag = weakness_engine.analyze_all_topics(stu_resps)
        rep_weak_count = (t_diag["classification"] == "Repeated Weakness").sum() if not t_diag.empty else 0
        if pct < 50.0 or rep_weak_count >= 2:
            at_risk_count += 1

    pass_rate = safe_percentage((student_rankings["percentage"] >= 50.0).sum(), total_students)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card("Class Average", f"{class_avg_pct:.1f}%", f"{total_students} enrolled students")
    with c2:
        render_kpi_card("Assessments", str(total_exams), f"{len(all_responses)} question attempts")
    with c3:
        render_kpi_card("Academic Support Needed", str(at_risk_count), f"{safe_percentage(at_risk_count, total_students):.1f}% of cohort flagged")
    with c4:
        render_kpi_card("Cohort Pass Rate", f"{pass_rate:.1f}%", "Passing threshold: >= 50%")

    # 2. Charts Row: Grade Distribution & Cohort Hardest Topics
    render_section_header("Cohort Distribution & Curriculum Difficulty", "Score spread across the class and topics causing the highest marks lost.")
    col_hist, col_hard = st.columns([1, 1])

    with col_hist:
        st.markdown("<div style='font-weight:600; font-size:0.88rem; color:#102B50; margin-bottom:8px;'>Grade Distribution Histogram</div>", unsafe_allow_html=True)
        fig_hist = px.histogram(
            student_rankings,
            x="percentage",
            nbins=8,
            color_discrete_sequence=["#2878E5"],
            labels={"percentage": "Overall Score %"},
            template="plotly_white"
        )
        fig_hist.update_layout(
            margin=dict(l=0, r=20, t=10, b=10),
            height=260,
            yaxis_title="Students",
            xaxis_title="Overall Score %",
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            font=dict(color="#102B50", family="Inter, sans-serif"),
            xaxis=dict(gridcolor="#E2EAF3", linecolor="#E2EAF3"),
            yaxis=dict(gridcolor="#E2EAF3", linecolor="#E2EAF3")
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    with col_hard:
        st.markdown("<div style='font-weight:600; font-size:0.88rem; color:#102B50; margin-bottom:8px;'>Cohort-Wide Hardest Topics</div>", unsafe_allow_html=True)
        topic_grp = all_responses.groupby(["subject_name", "topic_name"]).agg(
            obtained=("marks_obtained", "sum"),
            maximum=("maximum_marks", "sum")
        ).reset_index()
        topic_grp["marks_lost"] = (topic_grp["maximum"] - topic_grp["obtained"]).round(1)
        topic_grp["accuracy_pct"] = topic_grp.apply(lambda r: safe_percentage(r["obtained"], r["maximum"]), axis=1)

        hardest_topics = topic_grp.sort_values(by="marks_lost", ascending=False).head(7)

        fig_hard = px.bar(
            hardest_topics,
            x="marks_lost",
            y="topic_name",
            orientation="h",
            color_discrete_sequence=["#E35D63"],
            text="marks_lost",
            labels={"marks_lost": "Cohort Marks Lost", "topic_name": "Topic"},
            template="plotly_white"
        )
        fig_hard.update_layout(
            margin=dict(l=0, r=20, t=10, b=10),
            height=260,
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            font=dict(color="#102B50", family="Inter, sans-serif"),
            xaxis=dict(gridcolor="#E2EAF3", linecolor="#E2EAF3"),
            yaxis=dict(gridcolor="#E2EAF3", linecolor="#E2EAF3")
        )
        fig_hard.update_traces(texttemplate="%{text:.1f} lost", textposition="outside", textfont=dict(color="#102B50", size=10))
        st.plotly_chart(fig_hard, use_container_width=True)

    # 3. Assessment-by-Assessment Performance Summary Table
    render_section_header("Assessment Cohort Summary", "Average scores and participation rates across examinations.")
    exam_summary = all_attempts.groupby(["exam_name", "exam_type", "exam_date"]).agg(
        students=("student_id", "nunique"),
        avg_score=("percentage", "mean"),
        min_score=("percentage", "min"),
        max_score=("percentage", "max")
    ).reset_index().round(1)
    exam_summary.columns = ["Assessment", "Type", "Date", "Students", "Class Average %", "Min %", "Max %"]
    st.dataframe(exam_summary.sort_values(by="Date", ascending=False), use_container_width=True, hide_index=True)
