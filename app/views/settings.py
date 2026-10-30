"""
GradeLens View: System Settings & Database Diagnostics.
Displays live PostgreSQL / SQLite connection health, weakness engine threshold tuning, and demo data reset.
Strict light design system: #F5F8FC / #FFFFFF / #102B50 / #2878E5, zero emojis.
"""

import streamlit as st
from src.database.connection import db_manager, check_postgres_availability, get_db_config
from src.database.repository import Repository, repo
from src.data.seeder import seed_database
from app.components.metrics import render_kpi_card, render_section_header, render_alert_box


def render_settings_view(repository: Repository = repo):
    st.markdown(
        """
        <div style="margin-bottom: 20px;">
            <h1 style="font-size: 1.65rem; font-weight: 700; color: #102B50; margin: 0 0 4px 0;">
                Settings & Database Diagnostics
            </h1>
            <p style="color: #64748B; font-size: 0.88rem; margin: 0;">
                Verify PostgreSQL connectivity, calibrate weakness detection thresholds, and manage demonstration datasets.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    tab_db, tab_engine, tab_data = st.tabs(["Database Health", "Detection Thresholds", "Demo Data Management"])

    # -------------------------------------------------------------------------
    # TAB 1: DATABASE HEALTH
    # -------------------------------------------------------------------------
    with tab_db:
        render_section_header("Active Database Engine Status")
        status = db_manager.get_status()
        cfg = get_db_config()

        c1, c2, c3 = st.columns(3)
        with c1:
            render_kpi_card("Engine", status["active_engine"].upper(), "Configured in environment")
        with c2:
            status_text = "Connected" if status["connected"] else "Disconnected"
            render_kpi_card("Status", status_text, status["version"])
        with c3:
            render_kpi_card("Port", str(cfg["pg_port"]) if cfg["engine_type"] == "postgresql" else "Local File", cfg["pg_database"])

        if status["connected"]:
            render_alert_box(
                "Database Connection Active",
                f"Currently using {status['details']}. Relational constraints, foreign keys, and SQL views are functional.",
                alert_type="success"
            )
        else:
            render_alert_box(
                "PostgreSQL Unreachable",
                f"Connection message: {status['error']}. Ensure the PostgreSQL service is running or switch to SQLite mode for local development.",
                alert_type="warning"
            )

        st.markdown("<p style='font-weight:600; font-size:0.88rem; color:#102B50; margin-top:16px;'>PostgreSQL Service Diagnostics:</p>", unsafe_allow_html=True)
        if st.button("Test PostgreSQL Handshake (localhost:5432)"):
            pg_test = check_postgres_availability()
            if pg_test["available"]:
                st.success(f"PostgreSQL 18 is running. Version: {pg_test['version']}")
            else:
                st.error(f"PostgreSQL is not responding: {pg_test['error']}")
                st.info("Tip: Start the PostgreSQL Windows Service using: net start postgresql-x64-18 or run in SQLite mode.")

    # -------------------------------------------------------------------------
    # TAB 2: WEAKNESS ENGINE CALIBRATION
    # -------------------------------------------------------------------------
    with tab_engine:
        render_section_header("Weakness Engine Parameters", "Tune the deterministic thresholds used by GradeLens to classify topic mastery.")

        c_w, c_s, c_m = st.columns(3)
        with c_w:
            w_val = st.slider("Weakness Threshold (%)", min_value=40.0, max_value=70.0, value=60.0, step=5.0)
        with c_s:
            s_val = st.slider("Strong Threshold (%)", min_value=70.0, max_value=90.0, value=75.0, step=5.0)
        with c_m:
            m_val = st.number_input("Minimum Attempts Required", min_value=1, max_value=10, value=2, step=1)

        render_alert_box(
            "Current Rule Logic",
            f"Strong: Score >= {s_val:.1f}%\n"
            f"Monitoring: {w_val:.1f}% <= Score < {s_val:.1f}%\n"
            f"Weak: Score < {w_val:.1f}%\n"
            f"Repeated Weakness: Score < {w_val:.1f}% across 2 or more assessments\n"
            f"Insufficient Data: Fewer than {m_val} questions attempted",
            alert_type="info"
        )

    # -------------------------------------------------------------------------
    # TAB 3: DEMO DATA MANAGEMENT
    # -------------------------------------------------------------------------
    with tab_data:
        render_section_header("Reset Demonstration Data", "Re-generate synthetic student personas, exams, and question-level responses.")

        st.info("Resetting demo data will rebuild the database tables and populate fresh synthetic student personas (Aarav, Diya, Rohan, Ananya, Vikram, Pooja).")
        if st.button("Reset & Re-seed Demo Database", type="secondary"):
            with st.spinner("Rebuilding database schema and seeding personas..."):
                res = seed_database(force_reset=True)
                st.success(f"Database reset complete. Seeded {res['students']} students, {res['exams']} exams, and {res['responses']} question responses.")
                st.rerun()
