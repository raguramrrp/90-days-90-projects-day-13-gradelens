"""
GradeLens Professional Sidebar Navigation with Dedicated Buttons.
Replaces radio controls with categorized button navigation:
ACADEMIC, PLANNING, FACULTY, and DATA & REPORTS sections with role-based filtering.
Guarantees zero overlap and native Streamlit element flow.
"""

import streamlit as st
from src.database.repository import Repository, repo


def render_sidebar(repository: Repository = repo) -> str:
    """Renders the button-based sidebar navigation and returns the active page identifier."""
    with st.sidebar:
        # Wordmark & Branding Header
        st.markdown(
            """
            <div style="padding: 4px 0 12px 0; border-bottom: 1px solid #E2EAF3; margin-bottom: 4px;">
                <div style="font-size: 1.35rem; font-weight: 800; color: #102B50; letter-spacing: -0.025em; line-height: 1.15;">
                    Grade<span style="color:#2878E5;">Lens</span>
                </div>
                <div style="font-size: 0.72rem; color: #64748B; font-weight: 500; margin-top: 3px;">
                    Academic Performance & Weakness Analytics
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Role & Profile Switcher (native visible labels prevent clipping/overlap)
        active_role = st.selectbox(
            "Workspace Role",
            options=["Student", "Faculty"],
            index=0 if st.session_state.get("user_role", "Student") == "Student" else 1,
            key="role_selector_widget"
        )
        st.session_state.user_role = active_role

        if active_role == "Student":
            students_df = repository.get_students()
            if not students_df.empty:
                student_options = {
                    row["student_id"]: f"{row['name']} ({row['student_code']})"
                    for _, row in students_df.iterrows()
                }
                current_id = st.session_state.get("current_student_id", list(student_options.keys())[0])
                idx = list(student_options.keys()).index(current_id) if current_id in student_options else 0

                selected_student = st.selectbox(
                    "Active Student",
                    options=list(student_options.keys()),
                    format_func=lambda sid: student_options[sid],
                    index=idx,
                    key="student_selector_widget"
                )
                st.session_state.current_student_id = selected_student
        else:
            faculty_df = repository.get_faculty()
            if not faculty_df.empty:
                faculty_options = {
                    row["faculty_id"]: f"{row['name']} ({row['department']})"
                    for _, row in faculty_df.iterrows()
                }
                current_fid = st.session_state.get("current_faculty_id", list(faculty_options.keys())[0])
                idx = list(faculty_options.keys()).index(current_fid) if current_fid in faculty_options else 0

                selected_faculty = st.selectbox(
                    "Active Faculty",
                    options=list(faculty_options.keys()),
                    format_func=lambda fid: faculty_options[fid],
                    index=idx,
                    key="faculty_selector_widget"
                )
                st.session_state.current_faculty_id = selected_faculty

        st.markdown("<hr style='margin: 10px 0 6px 0; border: none; border-top: 1px solid #E2EAF3;'>", unsafe_allow_html=True)

        # Build Page Sections based on Role
        if active_role == "Student":
            sections = {
                "Academic": [
                    "Overview",
                    "Exam Manager",
                    "Subject Intelligence",
                    "Topic Weakness",
                    "Performance Trends"
                ],
                "Planning": [
                    "Revision Planner",
                    "Study Goals",
                    "Revision History"
                ],
                "Data": [
                    "Data Import",
                    "Settings"
                ]
            }
        else:
            sections = {
                "Academic": [
                    "Overview",
                    "Exam Manager",
                    "Subject Intelligence",
                    "Topic Weakness",
                    "Performance Trends"
                ],
                "Faculty": [
                    "Faculty Dashboard",
                    "Student Performance",
                    "Class Analytics"
                ],
                "Planning": [
                    "Revision Planner",
                    "Study Goals",
                    "Revision History"
                ],
                "Data": [
                    "Data Import",
                    "Settings"
                ]
            }

        # Flatten allowed pages for current role
        all_allowed_pages = [p for pages in sections.values() for p in pages]

        # Verify active page is valid for current role
        if "active_nav_page" not in st.session_state or st.session_state.active_nav_page not in all_allowed_pages:
            st.session_state.active_nav_page = all_allowed_pages[0]

        current_active = st.session_state.active_nav_page

        # Render Button-Based Navigation with native caption section headers
        for sec_name, pages in sections.items():
            st.caption(f"**{sec_name.upper()}**")
            for page in pages:
                is_active = (page == current_active)
                btn_type = "primary" if is_active else "secondary"
                if st.button(page, key=f"nav_btn_{page}", use_container_width=True, type=btn_type):
                    if st.session_state.active_nav_page != page:
                        st.session_state.active_nav_page = page
                        st.rerun()

    return st.session_state.active_nav_page
