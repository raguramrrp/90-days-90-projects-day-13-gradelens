"""
GradeLens View: Faculty Analytics Forwarder.
Routes to the specialized Faculty Dashboard view.
Strict light design system: #F5F8FC / #FFFFFF / #102B50 / #2878E5, zero emojis.
"""

from src.database.repository import Repository, repo
from app.views.faculty_dashboard import render_faculty_dashboard_view


def render_faculty_analytics_view(repository: Repository = repo):
    """Forwarder to the specialized Faculty Dashboard view."""
    render_faculty_dashboard_view(repository)
