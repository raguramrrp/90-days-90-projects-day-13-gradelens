"""
GradeLens View 6: Performance Trend Intelligence.
Longitudinal examination trajectories, difficulty calibrations, mistake shifts, and metacognitive confidence analysis.
Strict light design system: #F5F8FC / #FFFFFF / #102B50 / #2878E5, zero emojis.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.database.repository import Repository, repo
from src.analytics.trends import compute_exam_progression, compute_mistake_distribution, compute_confidence_calibration
from src.analytics.calculations import calculate_difficulty_breakdown, calculate_student_ranking
from app.components.metrics import render_kpi_card, render_section_header
from app.auth import get_current_user_context


def render_performance_trends_view(repository: Repository = repo):
    user = get_current_user_context(repository)
    st.markdown(
        """
        <div style="margin-bottom: 20px;">
            <h1 style="font-size: 1.65rem; font-weight: 700; color: #102B50; margin: 0 0 4px 0;">
                Performance Trend Intelligence
            </h1>
            <p style="color: #64748B; font-size: 0.88rem; margin: 0;">
                Assessment trajectories, cognitive confidence calibration, and class benchmark standing.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    student_id = user["id"] if user["role"] == "Student" else None
    responses_df = repository.get_question_responses(student_id=student_id)
    attempts_df = repository.get_attempts(student_id=student_id)

    if attempts_df.empty:
        st.info("Insufficient examination data to generate historical trends.")
        return

    # 1. Progression Chart
    render_section_header("Assessment Score Trajectory", "Exam-by-exam score percentage progression with trendline.")
    prog_df = compute_exam_progression(attempts_df)

    fig_prog = go.Figure()
    fig_prog.add_trace(go.Scatter(
        x=prog_df["exam_date"],
        y=prog_df["percentage"],
        mode="lines+markers+text",
        name="Score %",
        line=dict(color="#2878E5", width=2.5, shape="spline"),
        marker=dict(size=8, color="#2878E5", line=dict(color="#FFFFFF", width=1.5)),
        text=[f"{p:.1f}%" for p in prog_df["percentage"]],
        textposition="top center",
        textfont=dict(color="#102B50", size=10)
    ))
    fig_prog.add_hline(
        y=60.0,
        line_dash="dash",
        line_color="#E35D63",
        annotation_text="Weakness Benchmark (60%)",
        annotation_position="bottom right",
        annotation_font=dict(color="#E35D63", size=10)
    )
    fig_prog.update_layout(
        template="plotly_white",
        margin=dict(l=0, r=20, t=20, b=10),
        height=280,
        xaxis_title="Assessment Date",
        yaxis_title="Score %",
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(color="#102B50", family="Inter, sans-serif"),
        yaxis=dict(range=[0, 110], gridcolor="#E2EAF3", linecolor="#E2EAF3"),
        xaxis=dict(gridcolor="#E2EAF3", linecolor="#E2EAF3")
    )
    st.plotly_chart(fig_prog, use_container_width=True)

    # 2. Difficulty Breakdown & Metacognitive Calibration
    col_diff, col_conf = st.columns([1, 1])

    with col_diff:
        render_section_header("Accuracy by Question Difficulty", "Measure performance drop-off between Easy, Medium, and Hard items.")
        diff_df = calculate_difficulty_breakdown(responses_df)
        fig_diff = px.bar(
            diff_df,
            x="difficulty",
            y="accuracy_pct",
            color="difficulty",
            color_discrete_map={"Easy": "#16A58A", "Medium": "#2878E5", "Hard": "#E35D63"},
            text="accuracy_pct",
            template="plotly_white"
        )
        fig_diff.update_layout(
            margin=dict(l=0, r=10, t=10, b=10),
            height=260,
            xaxis_title="",
            yaxis_title="Accuracy %",
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            font=dict(color="#102B50", family="Inter, sans-serif"),
            showlegend=False,
            xaxis=dict(gridcolor="#E2EAF3", linecolor="#E2EAF3"),
            yaxis=dict(gridcolor="#E2EAF3", linecolor="#E2EAF3")
        )
        fig_diff.update_traces(texttemplate="%{text:.1f}%", textposition="outside", textfont=dict(color="#102B50", size=10))
        st.plotly_chart(fig_diff, use_container_width=True)

    with col_conf:
        render_section_header("Confidence vs Accuracy ('Blind Spot' Detector)", "Identifies self-assessed high confidence on incorrect answers.")
        calib_df = compute_confidence_calibration(responses_df)
        if not calib_df.empty:
            fig_calib = px.bar(
                calib_df,
                x="confidence_rating",
                y="accuracy_pct",
                color="confidence_rating",
                color_discrete_map={"Low": "#64748B", "Medium": "#2878E5", "High": "#16A58A"},
                text="accuracy_pct",
                template="plotly_white"
            )
            fig_calib.update_layout(
                margin=dict(l=0, r=10, t=10, b=10),
                height=260,
                xaxis_title="Self-Reported Confidence",
                yaxis_title="Actual Accuracy %",
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF",
                font=dict(color="#102B50", family="Inter, sans-serif"),
                showlegend=False,
                xaxis=dict(gridcolor="#E2EAF3", linecolor="#E2EAF3"),
                yaxis=dict(gridcolor="#E2EAF3", linecolor="#E2EAF3")
            )
            fig_calib.update_traces(texttemplate="%{text:.1f}%", textposition="outside", textfont=dict(color="#102B50", size=10))
            st.plotly_chart(fig_calib, use_container_width=True)
        else:
            st.info("No confidence ratings recorded.")

    # 3. Class Ranking
    render_section_header("Class Performance Benchmark", "Comparative standing across the enrolled cohort.")
    all_attempts = repository.get_attempts()
    ranking_df = calculate_student_ranking(all_attempts, anonymize=(user["role"] == "Student"))
    st.dataframe(ranking_df, use_container_width=True, hide_index=True)
