"""
GradeLens View: Reports & Exports.
Downloadable CSV and Excel exports and printable academic summaries.
Strict light design system: #F5F8FC / #FFFFFF / #102B50 / #2878E5, zero emojis.
"""

import io
import streamlit as st
import pandas as pd
from src.database.repository import Repository, repo
from app.components.metrics import render_section_header
from app.auth import get_current_user_context


def render_reports_export_view(repository: Repository = repo):
    user = get_current_user_context(repository)
    st.markdown(
        """
        <div style="margin-bottom: 20px;">
            <h1 style="font-size: 1.65rem; font-weight: 700; color: #102B50; margin: 0 0 4px 0;">
                Reports & Exports
            </h1>
            <p style="color: #64748B; font-size: 0.88rem; margin: 0;">
                Export institutional datasets and download structured CSV/Excel academic reports.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    render_section_header("Download Academic Datasets", "Export records formatted for institutional analysis, spreadsheets, or archiving.")

    student_id = user["id"] if user["role"] == "Student" else None

    # 1. Question Responses Export
    st.markdown("<p style='font-weight:600; font-size:0.9rem; color:#102B50; margin-top:10px;'>1. Question-Level Assessment Responses</p>", unsafe_allow_html=True)
    resp_df = repository.get_question_responses(student_id=student_id)
    if not resp_df.empty:
        c_r1, c_r2 = st.columns(2)
        with c_r1:
            st.download_button(
                "Download Responses (CSV)",
                data=resp_df.to_csv(index=False),
                file_name=f"gradelens_responses_{user['code']}.csv",
                mime="text/csv",
                use_container_width=True
            )
        with c_r2:
            out_xl = io.BytesIO()
            with pd.ExcelWriter(out_xl, engine="openpyxl") as w:
                resp_df.to_excel(w, index=False, sheet_name="Responses")
            st.download_button(
                "Download Responses (Excel)",
                data=out_xl.getvalue(),
                file_name=f"gradelens_responses_{user['code']}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

    # 2. Topic Weakness Summary Export
    st.markdown("<p style='font-weight:600; font-size:0.9rem; color:#102B50; margin-top:18px;'>2. Topic Performance & Weakness Diagnostics</p>", unsafe_allow_html=True)
    from src.analytics.weakness_engine import weakness_engine
    if not resp_df.empty:
        diag_df = weakness_engine.analyze_all_topics(resp_df)
        st.download_button(
            "Download Topic Weakness Summary (CSV)",
            data=diag_df.to_csv(index=False),
            file_name=f"gradelens_topic_weakness_{user['code']}.csv",
            mime="text/csv",
            use_container_width=True
        )

    # 3. Revision Sessions Log
    st.markdown("<p style='font-weight:600; font-size:0.9rem; color:#102B50; margin-top:18px;'>3. Revision Sessions & Practice Log</p>", unsafe_allow_html=True)
    rev_df = repository.get_revision_sessions(student_id=student_id)
    if not rev_df.empty:
        st.download_button(
            "Download Revision Sessions (CSV)",
            data=rev_df.to_csv(index=False),
            file_name=f"gradelens_revisions_{user['code']}.csv",
            mime="text/csv",
            use_container_width=True
        )

    # 4. Faculty Cohort Report (Faculty Only)
    if user["role"] == "Faculty":
        st.markdown("<p style='font-weight:600; font-size:0.9rem; color:#102B50; margin-top:18px;'>4. Full Cohort Performance Summary (Faculty Access)</p>", unsafe_allow_html=True)
        attempts_all = repository.get_attempts()
        st.download_button(
            "Download Cohort Results (CSV)",
            data=attempts_all.to_csv(index=False),
            file_name="gradelens_cohort_summary.csv",
            mime="text/csv",
            use_container_width=True
        )
