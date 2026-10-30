"""
GradeLens View 4: Topic Weakness & Repeated Mistake Detection.
The central analytical differentiator of GradeLens: transparent, rule-based weakness classifications,
explainable evidence summaries, marks-loss breakdowns, and mistake clustering.
Strict light theme (#F5F8FC / #FFFFFF / #102B50 / #2878E5), zero emojis.
"""

import uuid
import streamlit as st
import pandas as pd
import plotly.express as px
from src.database.repository import Repository, repo
from src.analytics.weakness_engine import TopicWeaknessEngine, weakness_engine
from src.analytics.trends import compute_mistake_distribution
from app.components.metrics import render_kpi_card, render_reasoning_box, render_section_header
from app.styles import get_badge_html
from app.auth import get_current_user_context


def render_topic_weakness_view(repository: Repository = repo):
    user = get_current_user_context(repository)
    st.markdown(
        """
        <div style="margin-bottom: 20px;">
            <h1 style="font-size: 1.65rem; font-weight: 700; color: #102B50; margin: 0 0 4px 0;">
                Topic Weakness & Mistake Detection
            </h1>
            <p style="color: #64748B; font-size: 0.88rem; margin: 0;">
                Deterministic root-cause diagnostics, repeated mistake clustering, and marks loss attribution.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    student_id = user["id"] if user["role"] == "Student" else None
    responses_df = repository.get_question_responses(student_id=student_id)

    if responses_df.empty:
        st.info("No question response records available to run weakness diagnostics.")
        return

    # Run Weakness Detection Engine
    analysis_df = weakness_engine.analyze_all_topics(responses_df)

    # 1. Summary Cards
    rep_weak_count = (analysis_df["classification"] == "Repeated Weakness").sum()
    weak_count = (analysis_df["classification"] == "Weak").sum()
    improving_count = (analysis_df["classification"] == "Improving").sum()
    strong_count = (analysis_df["classification"] == "Strong").sum()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card("Repeated Weakness", str(rep_weak_count), "Persistently <60% across assessments")
    with c2:
        render_kpi_card("Single Weakness", str(weak_count), "Requires immediate revision")
    with c3:
        render_kpi_card("Improving Topics", str(improving_count), "Demonstrated >= 15% score gains")
    with c4:
        render_kpi_card("Strong Topics", str(strong_count), "Mastery >= 75% verified")

    # 2. Mistake Distribution & Marks Loss Attribution
    render_section_header("Marks Loss & Mistake Category Attribution", "Analyze what curriculum concepts and specific error types cost the most marks.")
    col_loss_chart, col_mistake_chart = st.columns([1, 1])

    with col_loss_chart:
        st.markdown("<div style='font-weight:600; font-size:0.88rem; color:#102B50; margin-bottom:8px;'>Top Topics by Total Marks Lost</div>", unsafe_allow_html=True)
        top_loss = analysis_df.sort_values(by="marks_lost", ascending=False).head(7)
        fig_loss = px.bar(
            top_loss,
            x="marks_lost",
            y="topic_name",
            orientation="h",
            color="classification",
            color_discrete_map={
                "Repeated Weakness": "#E35D63",
                "Weak": "#E6A52E",
                "Declining": "#E6A52E",
                "Monitoring": "#2878E5",
                "Improving": "#16A58A",
                "Strong": "#16A58A",
                "Insufficient Data": "#94A3B8"
            },
            text="marks_lost",
            labels={"marks_lost": "Marks Lost", "topic_name": "Topic"},
            template="plotly_white"
        )
        fig_loss.update_layout(
            margin=dict(l=0, r=20, t=10, b=10),
            height=280,
            xaxis_title="Marks Lost",
            yaxis_title="",
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            font=dict(color="#102B50", family="Inter, sans-serif"),
            xaxis=dict(gridcolor="#E2EAF3", linecolor="#E2EAF3"),
            yaxis=dict(gridcolor="#E2EAF3", linecolor="#E2EAF3"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig_loss.update_traces(texttemplate="%{text:.1f} lost", textposition="outside", textfont=dict(color="#102B50", size=10))
        st.plotly_chart(fig_loss, use_container_width=True)

    with col_mistake_chart:
        st.markdown("<div style='font-weight:600; font-size:0.88rem; color:#102B50; margin-bottom:8px;'>Marks Lost by Mistake Root Cause</div>", unsafe_allow_html=True)
        mistakes_df = compute_mistake_distribution(responses_df)
        if not mistakes_df.empty:
            fig_mistakes = px.pie(
                mistakes_df,
                names="mistake_category",
                values="marks_lost",
                hole=0.45,
                color_discrete_sequence=["#E35D63", "#E6A52E", "#2878E5", "#16A58A", "#64748B"],
                template="plotly_white"
            )
            fig_mistakes.update_layout(
                margin=dict(l=10, r=10, t=10, b=10),
                height=280,
                paper_bgcolor="#FFFFFF",
                font=dict(color="#102B50", family="Inter, sans-serif"),
                legend=dict(orientation="h", yanchor="bottom", y=-0.25)
            )
            st.plotly_chart(fig_mistakes, use_container_width=True)
        else:
            st.info("No mistake categories recorded yet.")

    # 3. Transparent Explainable Topic Diagnosis Cards
    render_section_header("Explainable Diagnostic Reasoning & Recommendations", "Deterministic explanations generated from actual question outcomes and exam trends.")

    # Filter controls
    f_col1, f_col2 = st.columns([1, 1])
    with f_col1:
        classes_present = ["All Classifications"] + sorted(analysis_df["classification"].unique())
        sel_class = st.selectbox("Filter by Status", options=classes_present, index=0)
    with f_col2:
        subjects_present = ["All Subjects"] + sorted(analysis_df["subject_name"].unique())
        sel_subj = st.selectbox("Filter by Subject", options=subjects_present, index=0)

    filtered_analysis = analysis_df.copy()
    if sel_class != "All Classifications":
        filtered_analysis = filtered_analysis[filtered_analysis["classification"] == sel_class]
    if sel_subj != "All Subjects":
        filtered_analysis = filtered_analysis[filtered_analysis["subject_name"] == sel_subj]

    for _, row in filtered_analysis.iterrows():
        t_id = row["topic_id"]
        t_name = row["topic_name"]
        s_name = row["subject_name"]
        badge_html = get_badge_html(row["classification"])
        alert_style = "critical" if row["classification"] in ["Weak", "Repeated Weakness", "Declining"] else ("success" if row["classification"] == "Strong" else "info")

        with st.container():
            col_info, col_action = st.columns([4, 1])
            with col_info:
                header_card = f'<div style="display:flex; align-items:center; gap:10px; margin-bottom:6px;"><span style="font-weight:700; font-size:0.98rem; color:#102B50;">{t_name}</span><span style="color:#64748B; font-size:0.83rem;">({s_name})</span>{badge_html}</div>'
                st.markdown(header_card, unsafe_allow_html=True)
                render_reasoning_box(
                    f"Accuracy: {row['accuracy_pct']:.1f}% | Marks Lost: {row['marks_lost']:.1f} | Assessments Evaluated: {row['assessments_count']}",
                    row["explanation"],
                    alert_type=alert_style
                )
            with col_action:
                st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)
                if user["role"] == "Student" and st.button("Add to Tasks", key=f"plan_btn_{t_id}", use_container_width=True):
                    task_id = f"tsk_{uuid.uuid4().hex[:8]}"
                    repository.create_revision_task(
                        task_id=task_id,
                        student_id=student_id,
                        topic_id=t_id,
                        task_description=f"Revision & practice questions on {t_name}",
                        priority=row["priority"],
                        scheduled_date=str(pd.Timestamp.now().date())
                    )
                    st.success("Added to tasks.")
                    st.rerun()

    # 4. Top Marks-Loss Questions Table
    render_section_header("Questions Contributing Most to Marks Lost", "Specific exam questions responsible for the largest score drops.")
    loss_qs = responses_df[responses_df["marks_lost"] > 0].sort_values(by="marks_lost", ascending=False).head(10)
    if not loss_qs.empty:
        disp_qs = loss_qs[["exam_name", "subject_name", "topic_name", "question_text", "difficulty", "maximum_marks", "marks_obtained", "marks_lost", "mistake_category"]].copy()
        disp_qs.columns = ["Assessment", "Subject", "Topic", "Question", "Difficulty", "Max", "Obtained", "Lost", "Primary Error"]
        st.dataframe(disp_qs, use_container_width=True, hide_index=True)
