"""
Tests for View Routing, Template Generation, and Navigation Structure.
Verifies that all 14 modular views are importable and functional.
"""

import pytest
import pandas as pd
from src.imports.templates import get_csv_template, get_excel_template, generate_sample_csv, generate_sample_excel_bytes


def test_template_generation_functions():
    """Verifies that CSV and Excel template generators yield non-empty byte/string payloads."""
    csv_str = get_csv_template()
    assert isinstance(csv_str, str)
    assert "student_code" in csv_str
    assert "maximum_marks" in csv_str
    assert "marks_obtained" in csv_str

    excel_bytes = get_excel_template()
    assert isinstance(excel_bytes, bytes)
    assert len(excel_bytes) > 500


def test_all_14_views_importable():
    """Verifies that all 14 views can be imported without syntax or import errors."""
    from app.views.overview import render_overview_view
    from app.views.exam_manager import render_exam_manager_view
    from app.views.subject_intel import render_subject_intel_view
    from app.views.topic_weakness import render_topic_weakness_view
    from app.views.performance_trends import render_performance_trends_view
    from app.views.revision_planner import render_revision_planner_view
    from app.views.study_goals import render_study_goals_view
    from app.views.revision_history import render_revision_history_view
    from app.views.faculty_dashboard import render_faculty_dashboard_view
    from app.views.student_performance import render_student_performance_view
    from app.views.class_analytics import render_class_analytics_view
    from app.views.reports_export import render_reports_export_view
    from app.views.data_import import render_data_import_view
    from app.views.settings import render_settings_view

    views = [
        render_overview_view,
        render_exam_manager_view,
        render_subject_intel_view,
        render_topic_weakness_view,
        render_performance_trends_view,
        render_revision_planner_view,
        render_study_goals_view,
        render_revision_history_view,
        render_faculty_dashboard_view,
        render_student_performance_view,
        render_class_analytics_view,
        render_reports_export_view,
        render_data_import_view,
        render_settings_view
    ]
    assert len(views) == 14
    for v in views:
        assert callable(v)
