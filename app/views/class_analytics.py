"""
GradeLens Faculty View: Class Analytics & Early Warning Matrix.
Subject comparisons, hardest questions across assessments, and rule-based at-risk student intervention flagging.
Strict light design system: #F5F8FC / #FFFFFF / #102B50 / #2878E5, zero emojis.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from src.database.repository import Repository, repo
from src.analytics.calculations import safe_percentage, calculate_student_ranking
from src.analytics.weakness_engine import TopicWeaknessEngine, weakness_engine
from app.components.metrics import render_kpi_card, render_section_header, render_alert_box
from app.auth import get_current_user_context


def render_class_analytics_view(repository: Repository = repo):
    user = get_current_user_context(repository)
    st.markdown(
        """
        <div style="margin-bottom: 20px;">
            <h1 style="font-size: 1.65rem; font-weight: 700; color: #102B50; margin: 0 0 4px 0;">
                Class Analytics & Early Warning Matrix
            </h1>
            <p style="color: #64748B; font-size: 0.88rem; margin: 0;">
                Subject benchmarks, question-level failure analysis, and rule-based academic intervention alerts.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    all_attempts = repository.get_attempts()
    all_responses = repository.get_question_responses()
    all_students = repository.get_students()

    if all_attempts.empty or all_responses.empty:
        st.info("No cohort records available for class analytics.")
        return

    # Identify at-risk students
    student_rankings = calculate_student_ranking(all_attempts, anonymize=False)
    at_risk_list = []

    for _, stu_row in student_rankings.iterrows():
        sid = stu_row["student_id"]
        sname = stu_row.get("display_name", stu_row.get("student_name", f"Student {sid}"))
        pct = float(stu_row["percentage"])

        stu_resps = all_responses[all_responses["student_id"] == sid]
        t_diag = weakness_engine.analyze_all_topics(stu_resps)
        rep_weak_count = (t_diag["classification"] == "Repeated Weakness").sum() if not t_diag.empty else 0

        triggers = []
        if pct < 50.0:
            triggers.append(f"Overall average score ({pct:.1f}%) is below the 50% passing threshold")
        if rep_weak_count >= 2:
            triggers.append(f"{rep_weak_count} topics identified with repeated weakness across assessments")

        if triggers:
            at_risk_list.append({
                "Student ID": sid,
                "Student Name": sname,
                "Overall Score %": round(pct, 1),
                "Repeated Weak Topics": rep_weak_count,
                "Diagnostic Triggers": "; ".join(triggers)
            })

    at_risk_df = pd.DataFrame(at_risk_list)

    # 1. KPI Row
    total_students = all_students["student_id"].nunique()
    total_subjects = all_responses["subject_name"].nunique()

    # Question with lowest accuracy
    q_perf = all_responses.groupby(["question_id", "question_text", "difficulty", "subject_name"]).agg(
        obtained=("marks_obtained", "sum"),
        maximum=("maximum_marks", "sum")
    ).reset_index()
    q_perf["accuracy_pct"] = q_perf.apply(lambda r: safe_percentage(r["obtained"], r["maximum"]), axis=1)
    lowest_q_acc = q_perf["accuracy_pct"].min() if not q_perf.empty else 0.0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card("Cohort Size", str(total_students), "Enrolled students")
    with c2:
        render_kpi_card("Subjects Evaluated", str(total_subjects), "Curriculum modules")
    with c3:
        render_kpi_card("Lowest Question Accuracy", f"{lowest_q_acc:.1f}%", "Hardest question cohort score")
    with c4:
        render_kpi_card("At-Risk Flagged", str(len(at_risk_df)), "Meeting intervention criteria")

    # 2. Subject-by-Subject Benchmark Comparison
    render_section_header("Subject Benchmark Comparison", "Class average percentage across curriculum subjects.")
    subj_grp = all_responses.groupby("subject_name").agg(
        obtained=("marks_obtained", "sum"),
        maximum=("maximum_marks", "sum")
    ).reset_index()
    subj_grp["accuracy_pct"] = subj_grp.apply(lambda r: safe_percentage(r["obtained"], r["maximum"]), axis=1)

    fig_subj = px.bar(
        subj_grp,
        x="subject_name",
        y="accuracy_pct",
        color="accuracy_pct",
        color_continuous_scale=["#E35D63", "#E6A52E", "#16A58A"],
        text="accuracy_pct",
        range_y=[0, 105],
        labels={"subject_name": "Subject", "accuracy_pct": "Class Average %"},
        template="plotly_white"
    )
    fig_subj.update_layout(
        margin=dict(l=0, r=20, t=10, b=10),
        height=260,
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(color="#102B50", family="Inter, sans-serif"),
        xaxis=dict(gridcolor="#E2EAF3", linecolor="#E2EAF3"),
        yaxis=dict(gridcolor="#E2EAF3", linecolor="#E2EAF3"),
        coloraxis_showscale=False
    )
    fig_subj.update_traces(texttemplate="%{text:.1f}%", textposition="outside", textfont=dict(color="#102B50", size=10))
    st.plotly_chart(fig_subj, use_container_width=True)

    # 3. Early Warning At-Risk Student Matrix
    render_section_header("Early Warning At-Risk Intervention Matrix", "Transparent rule-based detection of students requiring immediate academic support.")
    if not at_risk_df.empty:
        st.dataframe(at_risk_df, use_container_width=True, hide_index=True)

        for _, r in at_risk_df.iterrows():
            render_alert_box(
                f"{r['Student Name']} — Overall Score: {r['Overall Score %']}%",
                f"Intervention Trigger: {r['Diagnostic Triggers']}. Action: Schedule dedicated remedial session and review conceptual fundamentals.",
                alert_type="critical"
            )
    else:
        render_alert_box("Cohort In Good Standing", "No students currently trigger the at-risk criteria (<50% score or 2+ repeated weak topics).", alert_type="success")

    # 4. Hardest Questions in the Curriculum
    render_section_header("Hardest Questions Across Assessments", "Questions where the cohort scored the lowest accuracy percentage.")
    hardest_qs = q_perf.sort_values(by="accuracy_pct", ascending=True).head(8)
    disp_hardest = hardest_qs[["subject_name", "question_text", "difficulty", "maximum", "obtained", "accuracy_pct"]].copy()
    disp_hardest.columns = ["Subject", "Question Text", "Difficulty", "Total Max Marks", "Cohort Marks Obtained", "Cohort Accuracy %"]
    st.dataframe(disp_hardest, use_container_width=True, hide_index=True)
