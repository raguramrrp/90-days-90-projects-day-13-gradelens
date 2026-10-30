"""
GradeLens View: Data Import & Ingestion.
Bulk import student examination marks and question responses from CSV/Excel with multi-tier validation.
Strict light design system: #F5F8FC / #FFFFFF / #102B50 / #2878E5, zero emojis.
"""

import io
import streamlit as st
import pandas as pd
from src.database.repository import Repository, repo
from src.imports.validator import validate_import_dataframe, commit_imported_records
from src.imports.templates import get_csv_template, get_excel_template
from app.components.metrics import render_kpi_card, render_section_header, render_alert_box
from app.auth import get_current_user_context


def render_data_import_view(repository: Repository = repo):
    user = get_current_user_context(repository)
    st.markdown(
        """
        <div style="margin-bottom: 20px;">
            <h1 style="font-size: 1.65rem; font-weight: 700; color: #102B50; margin: 0 0 4px 0;">
                Data Import
            </h1>
            <p style="color: #64748B; font-size: 0.88rem; margin: 0;">
                Import assessment marks, question responses, and mistake classifications from CSV or Excel spreadsheets.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 1. Download Blank / Sample Templates
    render_section_header("Download Import Templates", "Pre-formatted templates adhering to GradeLens relational constraints.")
    col_t_csv, col_t_xl = st.columns(2)
    with col_t_csv:
        csv_bytes = get_csv_template()
        st.download_button(
            "Download CSV Template",
            data=csv_bytes,
            file_name="gradelens_import_template.csv",
            mime="text/csv",
            use_container_width=True
        )
    with col_t_xl:
        xl_bytes = get_excel_template()
        st.download_button(
            "Download Excel Template (.xlsx)",
            data=xl_bytes,
            file_name="gradelens_import_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    # 2. File Upload & Ingestion Pipeline
    render_section_header("Upload Assessment File", "Select a populated CSV or Excel file to validate and import into the database.")
    uploaded_file = st.file_uploader("Select Assessment Spreadsheet (.csv or .xlsx)", type=["csv", "xlsx"])

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            st.markdown(f"<div style='font-size:0.84rem; color:#64748B; margin-top:4px;'>Loaded <b>{len(df)}</b> raw rows from <code>{uploaded_file.name}</code>.</div>", unsafe_allow_html=True)

            # Validate DataFrame
            valid_rows, invalid_rows, summary = validate_import_dataframe(df, repository)

            # Display Validation KPI Summary
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                render_kpi_card("Total Rows", str(summary["total_rows"]), "Rows in uploaded file")
            with c2:
                render_kpi_card("Valid Records", str(summary["valid_count"]), "Ready for insertion")
            with c3:
                render_kpi_card("Invalid Records", str(summary["invalid_count"]), "Failed validation rules")
            with c4:
                render_kpi_card("Duplicate Rows", str(summary["duplicate_count"]), "Identical items ignored")

            # Handle Invalidation / Errors
            if invalid_rows:
                err_df = pd.DataFrame(invalid_rows)
                render_alert_box(
                    f"{len(invalid_rows)} Rows Contain Validation Errors",
                    "Review the errors below before committing. You can download the error log to correct your input file.",
                    alert_type="warning"
                )
                st.dataframe(err_df, use_container_width=True, hide_index=True)

                st.download_button(
                    "Download Error Log (CSV)",
                    data=err_df.to_csv(index=False),
                    file_name="import_errors.csv",
                    mime="text/csv"
                )

            # Handle Valid Rows Preview & Commit
            if valid_rows:
                st.markdown("<div style='font-weight:600; font-size:0.88rem; color:#102B50; margin-top:16px; margin-bottom:8px;'>Validated Records Preview</div>", unsafe_allow_html=True)
                preview_df = pd.DataFrame(valid_rows).drop(columns=["student_id", "subject_id"], errors="ignore")
                st.dataframe(preview_df.head(10), use_container_width=True, hide_index=True)

                col_btn, col_blank = st.columns([1, 2])
                with col_btn:
                    if st.button("Confirm and Import Records", type="primary", use_container_width=True):
                        inserted = commit_imported_records(valid_rows, repository)
                        st.success(f"Successfully imported {inserted} question responses into GradeLens.")
                        st.rerun()

        except Exception as e:
            render_alert_box("File Ingestion Error", f"Failed to parse uploaded file: {str(e)}", alert_type="critical")
