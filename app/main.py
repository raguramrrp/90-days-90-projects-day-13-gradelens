"""
GradeLens: Academic Performance Analytics & Weakness Detection Platform.
Main Streamlit Application Entrypoint.
Day 13 of 90 Days — 90 Projects Challenge.
Strict light design system: #F5F8FC / #FFFFFF / #102B50 / #2878E5, zero emojis.
"""

import sys
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
from app.styles import THEME_CSS
from app.components.navigation import render_sidebar
from src.database.repository import repo
from src.database.schema import init_database
from src.data.seeder import seed_database

# Page Configuration — Clean text without emojis
st.set_page_config(
    page_title="GradeLens — Academic Intelligence",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Clean Light CSS Theme
st.markdown(THEME_CSS, unsafe_allow_html=True)


def ensure_database_ready():
    """Checks database existence and seeds baseline demo data if tables are empty."""
    try:
        students = repo.get_students()
        if students.empty:
            init_database()
            seed_database()
    except Exception:
        init_database()
        seed_database()


def main():
    ensure_database_ready()

    # Render Fixed Left Sidebar Navigation
    active_page = render_sidebar(repo)

    # Route to Selected View
    if active_page == "Overview":
        from app.views.overview import render_overview_view
        render_overview_view(repo)
    elif active_page == "Exam Manager":
        from app.views.exam_manager import render_exam_manager_view
        render_exam_manager_view(repo)
    elif active_page == "Subject Intelligence":
        from app.views.subject_intel import render_subject_intel_view
        render_subject_intel_view(repo)
    elif active_page == "Topic Weakness":
        from app.views.topic_weakness import render_topic_weakness_view
        render_topic_weakness_view(repo)
    elif active_page == "Performance Trends":
        from app.views.performance_trends import render_performance_trends_view
        render_performance_trends_view(repo)
    elif active_page == "Revision Planner":
        from app.views.revision_planner import render_revision_planner_view
        render_revision_planner_view(repo)
    elif active_page == "Study Goals":
        from app.views.study_goals import render_study_goals_view
        render_study_goals_view(repo)
    elif active_page == "Revision History":
        from app.views.revision_history import render_revision_history_view
        render_revision_history_view(repo)
    elif active_page == "Faculty Dashboard":
        from app.views.faculty_dashboard import render_faculty_dashboard_view
        render_faculty_dashboard_view(repo)
    elif active_page == "Student Performance":
        from app.views.student_performance import render_student_performance_view
        render_student_performance_view(repo)
    elif active_page == "Class Analytics":
        from app.views.class_analytics import render_class_analytics_view
        render_class_analytics_view(repo)
    elif active_page == "Reports & Exports":
        from app.views.reports_export import render_reports_export_view
        render_reports_export_view(repo)
    elif active_page == "Data Import":
        from app.views.data_import import render_data_import_view
        render_data_import_view(repo)
    elif active_page == "Settings":
        from app.views.settings import render_settings_view
        render_settings_view(repo)
    else:
        st.error(f"Unknown page: {active_page}")


if __name__ == "__main__":
    main()
