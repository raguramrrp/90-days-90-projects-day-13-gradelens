"""
GradeLens View 3: Subject Intelligence.
Deep-dive subject-level analytics, topic distribution, marks loss, and consistency metrics.
High-contrast light design system: #F5F8FC / #FFFFFF / #102B50 / #2878E5, no emojis.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.database.repository import Repository, repo
from src.analytics.calculations import calculate_subject_metrics, calculate_difficulty_breakdown, safe_percentage
from app.components.metrics import render_kpi_card, render_section_header
from app.auth import get_current_user_context


def render_subject_intel_view(repository: Repository = repo):
    user = get_current_user_context(repository)
    st.markdown(
        """
        <div style="margin-bottom: 20px;">
            <h1 style="font-size: 1.65rem; font-weight: 700; color: #102B50; margin: 0 0 4px 0;">
                Subject Intelligence
            </h1>
            <p style="color: #64748B; font-size: 0.88rem; margin: 0;">
                Curriculum analysis, syllabus coverage, assessment consistency, and difficulty-wise accuracy.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    student_id = user["id"] if user["role"] == "Student" else None
    responses_df = repository.get_question_responses(student_id=student_id)

    if responses_df.empty:
        st.info("No assessment records available for subject analysis.")
        return

    # Subject Selector Filter
    subjects = sorted(responses_df["subject_name"].unique())
    selected_subject = st.selectbox("Subject Filter", options=["All Subjects"] + subjects, index=0)

    filtered_df = responses_df if selected_subject == "All Subjects" else responses_df[responses_df["subject_name"] == selected_subject]

    # Metrics calculation
    metrics = calculate_subject_metrics(filtered_df)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card("Subject Accuracy", f"{metrics['overall_percentage']:.1f}%", f"{metrics['total_obtained']} of {metrics['total_possible']} marks")
    with c2:
        render_kpi_card("Assessments", str(metrics["total_assessments"]), f"{metrics['total_questions']} questions evaluated")
    with c3:
        render_kpi_card("Marks Lost", f"{metrics['total_marks_lost']:.1f}", f"Range: {metrics['lowest_pct']}% to {metrics['highest_pct']}%")
    with c4:
        render_kpi_card("Consistency", metrics["consistency_rating"], f"Score Std Dev: {metrics['score_std_dev']}%")

    render_section_header("Curriculum & Topic Breakdown", "Inspect marks obtained vs lost across topics and accuracy by difficulty.")

    col_topics, col_diff = st.columns([3, 2])

    with col_topics:
        st.markdown("<div style='font-weight:600; font-size:0.88rem; color:#102B50; margin-bottom:8px;'>Topic Marks Obtained vs Lost</div>", unsafe_allow_html=True)
        top_grp = filtered_df.groupby("topic_name").agg(
            obtained=("marks_obtained", "sum"),
            maximum=("maximum_marks", "sum")
        ).reset_index()
        top_grp["lost"] = top_grp["maximum"] - top_grp["obtained"]

        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            name="Marks Obtained",
            y=top_grp["topic_name"],
            x=top_grp["obtained"],
            orientation="h",
            marker_color="#16A58A"
        ))
        fig_bar.add_trace(go.Bar(
            name="Marks Lost",
            y=top_grp["topic_name"],
            x=top_grp["lost"],
            orientation="h",
            marker_color="#E35D63"
        ))
        fig_bar.update_layout(
            barmode="stack",
            template="plotly_white",
            margin=dict(l=0, r=20, t=10, b=10),
            height=280,
            xaxis_title="Marks",
            yaxis_title="",
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            font=dict(color="#102B50", family="Inter, sans-serif"),
            xaxis=dict(gridcolor="#E2EAF3", linecolor="#E2EAF3"),
            yaxis=dict(gridcolor="#E2EAF3", linecolor="#E2EAF3"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_diff:
        st.markdown("<div style='font-weight:600; font-size:0.88rem; color:#102B50; margin-bottom:8px;'>Accuracy by Question Difficulty</div>", unsafe_allow_html=True)
        diff_df = calculate_difficulty_breakdown(filtered_df)
        fig_diff = px.bar(
            diff_df,
            x="difficulty",
            y="accuracy_pct",
            color="difficulty",
            color_discrete_map={"Easy": "#16A58A", "Medium": "#2878E5", "Hard": "#E35D63"},
            text="accuracy_pct",
            range_y=[0, 105],
            labels={"difficulty": "Difficulty", "accuracy_pct": "Accuracy %"},
            template="plotly_white"
        )
        fig_diff.update_layout(
            margin=dict(l=0, r=20, t=10, b=10),
            height=280,
            xaxis_title="",
            yaxis_title="Accuracy %",
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            font=dict(color="#102B50", family="Inter, sans-serif"),
            showlegend=False,
            xaxis=dict(gridcolor="#E2EAF3", linecolor="#E2EAF3"),
            yaxis=dict(gridcolor="#E2EAF3", linecolor="#E2EAF3")
        )
        fig_diff.update_traces(texttemplate="%{text:.1f}%", textposition="outside", textfont=dict(color="#102B50", size=11))
        st.plotly_chart(fig_diff, use_container_width=True)

    # Detailed Topic Performance Table
    render_section_header("Granular Topic Analytics", "Detailed marks accounting for each unit and concept.")
    topic_table = filtered_df.groupby(["subject_name", "unit_name", "topic_name"]).agg(
        questions=("response_id", "count"),
        obtained=("marks_obtained", "sum"),
        maximum=("maximum_marks", "sum")
    ).reset_index()
    topic_table["lost"] = (topic_table["maximum"] - topic_table["obtained"]).round(1)
    topic_table["accuracy_pct"] = topic_table.apply(lambda r: safe_percentage(r["obtained"], r["maximum"]), axis=1)
    topic_table.columns = ["Subject", "Unit", "Topic", "Questions", "Obtained", "Maximum", "Marks Lost", "Accuracy %"]
    st.dataframe(topic_table.sort_values(by="Marks Lost", ascending=False), use_container_width=True, hide_index=True)
