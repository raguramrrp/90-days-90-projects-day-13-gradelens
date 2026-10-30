"""
GradeLens View: Revision History & Effectiveness.
Detailed logs of completed revision sessions and empirical before-and-after score changes.
Strict light design system: #F5F8FC / #FFFFFF / #102B50 / #2878E5, zero emojis.
"""

import uuid
import streamlit as st
import pandas as pd
from src.database.repository import Repository, repo
from src.analytics.revision_tracker import compute_revision_impact
from app.components.metrics import render_kpi_card, render_section_header, render_alert_box
from app.auth import get_current_user_context


def render_revision_history_view(repository: Repository = repo):
    user = get_current_user_context(repository)
    st.markdown(
        """
        <div style="margin-bottom: 20px;">
            <h1 style="font-size: 1.65rem; font-weight: 700; color: #102B50; margin: 0 0 4px 0;">
                Revision History & Effectiveness
            </h1>
            <p style="color: #64748B; font-size: 0.88rem; margin: 0;">
                Document completed study sessions and measure subsequent score gains to verify what study strategies work.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    student_id = user["id"] if user["role"] == "Student" else None
    if not student_id:
        st.info("Please select an active student from the sidebar to view personal revision logs.")
        return

    sessions_df = repository.get_revision_sessions(student_id=student_id)
    responses_df = repository.get_question_responses(student_id=student_id)

    # Calculate summary KPIs
    total_sessions = len(sessions_df) if not sessions_df.empty else 0
    total_mins = int(sessions_df["duration_minutes"].sum()) if not sessions_df.empty else 0
    total_hours = total_mins / 60.0
    topics_revised = sessions_df["topic_name"].nunique() if not sessions_df.empty else 0

    impact_df = compute_revision_impact(responses_df, sessions_df)
    effective_count = (impact_df["score_delta"] > 0).sum() if not impact_df.empty else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card("Total Sessions", str(total_sessions), "Completed revision logs")
    with c2:
        render_kpi_card("Study Time", f"{total_hours:.1f} hrs", f"{total_mins} total minutes")
    with c3:
        render_kpi_card("Topics Revised", str(topics_revised), "Unique curriculum concepts")
    with c4:
        render_kpi_card("Effective Reviews", str(effective_count), "Showed score gains")

    # 1. Before vs After Revision Score Delta (Effectiveness)
    render_section_header("Observed Revision Impact (Before vs. After)", "Empirical score comparison across assessments conducted before and after logged revision.")
    if not impact_df.empty:
        for _, imp in impact_df.iterrows():
            delta = imp["score_delta"]
            delta_prefix = "+" if delta > 0 else ""
            alert_type = "success" if delta >= 10.0 else ("info" if delta > 0 else "critical")
            status_text = imp["observed_impact"]

            header_text = f"{imp['topic_name']} ({imp['subject_name']}) — Pre: {imp['pre_revision_score']:.1f}% | Post: {imp['post_revision_score']:.1f}% | Delta: {delta_prefix}{delta:.1f}% ({status_text})"
            render_alert_box(header_text, imp["evidence_note"], alert_type=alert_type)
    else:
        st.info("No before/after assessment pairs available yet to measure revision delta for this student.")

    # 2. Log New Completed Revision Session
    render_section_header("Log Completed Revision Session", "Record study duration, review techniques, and reflections.")
    col_log, col_recent = st.columns([1, 1.8])

    with col_log:
        with st.form("log_revision_session_form"):
            topics_df = repository.get_topics()
            top_opts = {r["topic_id"]: f"{r['subject_code']} - {r['topic_name']}" for _, r in topics_df.iterrows()} if not topics_df.empty else {}
            sel_topic = st.selectbox("Revised Topic", options=list(top_opts.keys()), format_func=lambda k: top_opts[k])
            rev_date = st.date_input("Date Completed", value=pd.Timestamp.now().date())
            duration = st.number_input("Duration (Minutes)", min_value=10, max_value=300, value=45, step=5)
            rev_type = st.selectbox(
                "Revision Method",
                options=["Practice Questions", "Concept Notes Review", "Past Exam Drill", "Formula Sheet Drill", "Flashcards", "Group Study"]
            )
            notes = st.text_area("Notes & Observations", "Worked through 8 past exam problems; reviewed edge conditions.")

            if st.form_submit_button("Log Session", type="primary", use_container_width=True):
                sid = f"rev_{uuid.uuid4().hex[:8]}"
                repository.log_revision_session(
                    session_id=sid,
                    student_id=student_id,
                    topic_id=sel_topic,
                    revision_date=str(rev_date),
                    duration_minutes=int(duration),
                    revision_type=rev_type,
                    notes=notes
                )
                st.success("Revision session recorded.")
                st.rerun()

    with col_recent:
        st.markdown("<div style='font-weight:600; font-size:0.88rem; color:#102B50; margin-bottom:8px;'>Past Revision Logs</div>", unsafe_allow_html=True)
        if not sessions_df.empty:
            disp_sessions = sessions_df[["revision_date", "subject_name", "topic_name", "duration_minutes", "revision_type", "notes"]].copy()
            disp_sessions.columns = ["Date", "Subject", "Topic", "Mins", "Method", "Notes"]
            st.dataframe(disp_sessions, use_container_width=True, hide_index=True)
        else:
            st.info("No revision sessions recorded yet.")
