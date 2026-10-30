"""
GradeLens View 1: Academic Overview Dashboard.
Faithfully recreates the visual layout, visual hierarchy, KPI metrics, grouped bar charts,
trendlines, study plan, and right-hand action panels from the reference design.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.database.repository import Repository, repo
from src.analytics.calculations import safe_percentage, calculate_student_ranking
from src.analytics.weakness_engine import TopicWeaknessEngine, weakness_engine
from app.components.metrics import render_kpi_card, render_alert_box, render_section_header, render_progress_bar
from app.styles import get_badge_html
from app.auth import get_current_user_context


def render_overview_view(repository: Repository = repo):
    user = get_current_user_context(repository)
    student_id = user["id"] if user["role"] == "Student" else st.session_state.get("current_student_id", "stu_01")

    responses_df = repository.get_question_responses(student_id=student_id)
    attempts_df = repository.get_attempts(student_id=student_id)
    all_attempts_df = repository.get_attempts()
    tasks_df = repository.get_revision_tasks(student_id=student_id)
    recs_df = repository.get_recommendations(student_id=student_id, status="Active")

    # -------------------------------------------------------------------------
    # 1. HEADER BAR
    # -------------------------------------------------------------------------
    col_hdr_left, col_hdr_right = st.columns([3, 2])
    with col_hdr_left:
        st.markdown(
            f"""
            <div style="margin-bottom: 12px;">
                <div style="font-size: 1.45rem; font-weight: 800; color: #102B50; letter-spacing: -0.02em;">
                    Academic Overview
                </div>
                <div style="color: #64748B; font-size: 0.86rem; margin-top: 2px;">
                    Performance intelligence for <strong>{user['name']}</strong> ({user['code']}) &bull; {user['department']}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_hdr_right:
        c_yr, c_sem = st.columns([1, 1])
        with c_yr:
            acad_year = st.selectbox("Academic Year", options=["2026-2027", "2025-2026"], index=0, label_visibility="collapsed")
        with c_sem:
            st.markdown(
                """
                <div style="background:#EAF3FF; border:1px solid #BFDCFF; border-radius:4px; padding:7px 12px; text-align:center; font-size:0.82rem; font-weight:600; color:#2878E5;">
                    Semester 7 (Active)
                </div>
                """,
                unsafe_allow_html=True
            )

    if responses_df.empty or attempts_df.empty:
        render_alert_box(
            "No Assessment Records Found",
            "This student profile does not have any recorded examinations yet. Use the Quick Actions panel or Exam Manager to import or record marks.",
            alert_type="info"
        )
        return

    # -------------------------------------------------------------------------
    # 2. KPI METRICS (4 in a row)
    # -------------------------------------------------------------------------
    total_obtained = float(responses_df["marks_obtained"].sum())
    total_max = float(responses_df["maximum_marks"].sum())
    overall_pct = safe_percentage(total_obtained, total_max)
    total_subjects = responses_df["subject_id"].nunique()
    total_exams = attempts_df["exam_id"].nunique()

    # Ranking
    ranking_df = calculate_student_ranking(all_attempts_df, anonymize=False)
    stu_rank_row = ranking_df[ranking_df["student_id"] == student_id]
    current_rank = f"#{int(stu_rank_row.iloc[0]['rank'])} of {len(ranking_df)}" if not stu_rank_row.empty else "N/A"

    # Delta compared to previous attempt
    sorted_attempts = attempts_df.sort_values("exam_date")
    if len(sorted_attempts) >= 2:
        last_pct = sorted_attempts.iloc[-1]["percentage"]
        prev_pct = sorted_attempts.iloc[-2]["percentage"]
        diff = round(last_pct - prev_pct, 1)
        delta_str = f"{diff:+.1f}%"
    else:
        delta_str = None

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_kpi_card("Overall Percentage", f"{overall_pct:.1f}%", f"{total_obtained:.1f} of {total_max:.1f} marks", delta=delta_str)
    with k2:
        render_kpi_card("Total Subjects", str(total_subjects), "Active in curriculum")
    with k3:
        render_kpi_card("Total Exams", str(total_exams), f"{len(responses_df)} questions assessed")
    with k4:
        render_kpi_card("Current Rank", current_rank, "Class cohort standing")

    st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 3. MAIN DASHBOARD GRID (Left 70% | Right 30%)
    # -------------------------------------------------------------------------
    col_main, col_side = st.columns([7, 3])

    # =========================================================================
    # LEFT MAIN COLUMN
    # =========================================================================
    with col_main:
        # Row 1: Charts (Subject-wise Performance & Performance Trend)
        c_subj_chart, c_trend_chart = st.columns([1, 1])

        with c_subj_chart:
            st.markdown(
                """
                <div style="background:#FFFFFF; border:1px solid #E2EAF3; border-radius:6px; padding:14px 16px; margin-bottom:14px; box-shadow:0 1px 3px rgba(16,43,80,0.03);">
                    <div style="font-weight:700; font-size:0.88rem; color:#102B50; margin-bottom:8px;">Subject-wise Performance</div>
                """,
                unsafe_allow_html=True
            )

            # Student score vs Class Average per subject
            subj_grp = responses_df.groupby(["subject_id", "subject_name"]).agg(
                obtained=("marks_obtained", "sum"),
                maximum=("maximum_marks", "sum")
            ).reset_index()
            subj_grp["student_pct"] = subj_grp.apply(lambda r: safe_percentage(r["obtained"], r["maximum"]), axis=1)

            # Cohort class average per subject
            cohort_resps = all_attempts_df.groupby("student_id").apply(
                lambda df_s: df_s["percentage"].mean()
            ).mean() if not all_attempts_df.empty else 68.0

            # Generate grouped horizontal bar chart
            fig_subj = go.Figure()
            fig_subj.add_trace(go.Bar(
                name="Student Score",
                y=subj_grp["subject_name"],
                x=subj_grp["student_pct"],
                orientation="h",
                marker_color="#2878E5",
                text=[f"{v:.1f}%" for v in subj_grp["student_pct"]],
                textposition="outside",
                textfont=dict(size=10, color="#102B50")
            ))
            fig_subj.add_trace(go.Bar(
                name="Class Average",
                y=subj_grp["subject_name"],
                x=[68.0] * len(subj_grp),
                orientation="h",
                marker_color="#CBD5E1",
                text=["68.0%"] * len(subj_grp),
                textposition="outside",
                textfont=dict(size=10, color="#64748B")
            ))
            fig_subj.update_layout(
                barmode="group",
                margin=dict(l=0, r=25, t=10, b=10),
                height=240,
                xaxis=dict(range=[0, 115], showgrid=True, gridcolor="#F1F5F9", tickfont=dict(size=10, color="#64748B")),
                yaxis=dict(tickfont=dict(size=10, color="#102B50")),
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10, color="#64748B"))
            )
            st.plotly_chart(fig_subj, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with c_trend_chart:
            st.markdown(
                """
                <div style="background:#FFFFFF; border:1px solid #E2EAF3; border-radius:6px; padding:14px 16px; margin-bottom:14px; box-shadow:0 1px 3px rgba(16,43,80,0.03);">
                    <div style="font-weight:700; font-size:0.88rem; color:#102B50; margin-bottom:8px;">Performance Trend</div>
                """,
                unsafe_allow_html=True
            )

            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(
                x=sorted_attempts["exam_name"],
                y=sorted_attempts["percentage"],
                mode="lines+markers",
                name="Student Score",
                line=dict(color="#2878E5", width=2.5),
                marker=dict(size=7, color="#2878E5", line=dict(color="#FFFFFF", width=1.5))
            ))
            fig_trend.add_hline(
                y=60.0,
                line_dash="dash",
                line_color="#E35D63",
                annotation_text="Weakness Benchmark (60%)",
                annotation_position="bottom right",
                annotation_font=dict(color="#E35D63", size=9)
            )
            fig_trend.update_layout(
                margin=dict(l=0, r=10, t=10, b=10),
                height=240,
                yaxis=dict(range=[0, 105], showgrid=True, gridcolor="#F1F5F9", tickfont=dict(size=10, color="#64748B")),
                xaxis=dict(tickfont=dict(size=10, color="#102B50")),
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10, color="#64748B"))
            )
            st.plotly_chart(fig_trend, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # Row 2: Topic Performance & Recent Exams
        c_top_dist, c_recent_ex = st.columns([1, 1])

        with c_top_dist:
            st.markdown(
                """
                <div style="background:#FFFFFF; border:1px solid #E2EAF3; border-radius:6px; padding:14px 16px; margin-bottom:14px; box-shadow:0 1px 3px rgba(16,43,80,0.03);">
                    <div style="font-weight:700; font-size:0.88rem; color:#102B50; margin-bottom:8px;">Topic Performance Distribution</div>
                """,
                unsafe_allow_html=True
            )
            topic_diag = weakness_engine.analyze_all_topics(responses_df)
            if not topic_diag.empty:
                # Count by categories
                c_crit = (topic_diag["classification"] == "Repeated Weakness").sum()
                c_rev = (topic_diag["classification"] == "Weak").sum()
                c_good = (topic_diag["classification"].isin(["Monitoring", "Improving"])).sum()
                c_strong = (topic_diag["classification"] == "Strong").sum()

                cat_df = pd.DataFrame([
                    {"Category": "Strong (>=75%)", "Count": c_strong, "Color": "#16A58A"},
                    {"Category": "Good (60-74%)", "Count": c_good, "Color": "#E6A52E"},
                    {"Category": "Needs Revision (<60%)", "Count": c_rev, "Color": "#D9531E"},
                    {"Category": "Critical (Repeated)", "Count": c_crit, "Color": "#E35D63"}
                ])

                fig_pie = go.Figure(data=[go.Pie(
                    labels=cat_df["Category"],
                    values=cat_df["Count"],
                    hole=0.55,
                    marker=dict(colors=cat_df["Color"]),
                    textinfo="value",
                    textfont=dict(size=11, color="#FFFFFF")
                )])
                fig_pie.update_layout(
                    margin=dict(l=0, r=0, t=10, b=10),
                    height=200,
                    paper_bgcolor="#FFFFFF",
                    legend=dict(orientation="v", font=dict(size=10, color="#64748B"), yanchor="middle", y=0.5)
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with c_recent_ex:
            st.markdown(
                """
                <div style="background:#FFFFFF; border:1px solid #E2EAF3; border-radius:6px; padding:14px 16px; margin-bottom:14px; box-shadow:0 1px 3px rgba(16,43,80,0.03);">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <span style="font-weight:700; font-size:0.88rem; color:#102B50;">Recent Exams</span>
                        <span style="font-size:0.75rem; color:#2878E5; font-weight:600;">View All</span>
                    </div>
                """,
                unsafe_allow_html=True
            )
            disp_recent = sorted_attempts.tail(4)[["exam_name", "exam_date", "percentage"]].copy()
            disp_recent.columns = ["Exam", "Date", "Score"]
            disp_recent["Status"] = disp_recent["Score"].apply(lambda s: "Passed" if s >= 50.0 else "Needs Review")
            disp_recent["Score"] = disp_recent["Score"].apply(lambda s: f"{s:.1f}%")
            st.dataframe(disp_recent, use_container_width=True, hide_index=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # Row 3: Weekly Study Plan & Improvement Progress
        c_plan, c_imp = st.columns([1, 1])

        with c_plan:
            st.markdown(
                """
                <div style="background:#FFFFFF; border:1px solid #E2EAF3; border-radius:6px; padding:14px 16px; margin-bottom:14px; box-shadow:0 1px 3px rgba(16,43,80,0.03);">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                        <span style="font-weight:700; font-size:0.88rem; color:#102B50;">Weekly Study Plan</span>
                        <span style="font-size:0.75rem; color:#2878E5; font-weight:600;">Open Planner</span>
                    </div>
                """,
                unsafe_allow_html=True
            )
            if not tasks_df.empty:
                for _, t_row in tasks_df.head(3).iterrows():
                    p_badge = "#E35D63" if t_row["priority"] == "High" else "#E6A52E"
                    st.markdown(
                        f"""
                        <div style="border-left: 3px solid {p_badge}; padding-left: 10px; margin-bottom: 8px;">
                            <div style="font-size: 0.84rem; font-weight: 600; color: #102B50;">{t_row['task_description']}</div>
                            <div style="font-size: 0.74rem; color: #64748B;">{t_row['subject_name']} &bull; Due: {t_row['scheduled_date']} &bull; Status: {t_row['status']}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                st.markdown("<p style='font-size:0.82rem; color:#64748B;'>No active revision tasks scheduled.</p>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with c_imp:
            st.markdown(
                """
                <div style="background:#FFFFFF; border:1px solid #E2EAF3; border-radius:6px; padding:14px 16px; margin-bottom:14px; box-shadow:0 1px 3px rgba(16,43,80,0.03);">
                    <div style="font-weight:700; font-size:0.88rem; color:#102B50; margin-bottom:10px;">Improvement Progress</div>
                """,
                unsafe_allow_html=True
            )
            for _, s_row in subj_grp.head(3).iterrows():
                color = "#16A58A" if s_row["student_pct"] >= 75.0 else ("#E6A52E" if s_row["student_pct"] >= 60.0 else "#E35D63")
                render_progress_bar(s_row["subject_name"], s_row["student_pct"], score_text=f"{s_row['student_pct']:.1f}%", color=color)
            st.markdown("</div>", unsafe_allow_html=True)

    # =========================================================================
    # RIGHT SIDEBAR PANELS
    # =========================================================================
    with col_side:
        # Panel 1: Quick Actions
        st.markdown(
            """
            <div style="background:#FFFFFF; border:1px solid #E2EAF3; border-radius:6px; padding:14px 16px; margin-bottom:14px; box-shadow:0 1px 3px rgba(16,43,80,0.03);">
                <div style="font-weight:700; font-size:0.88rem; color:#102B50; margin-bottom:10px;">Quick Actions</div>
            """,
            unsafe_allow_html=True
        )
        if user["role"] == "Faculty":
            if st.button("Early Warning Matrix", use_container_width=True, type="secondary"):
                st.session_state.active_nav_page = "Class Analytics"
                st.rerun()

            if st.button("Faculty Dashboard", use_container_width=True, type="secondary"):
                st.session_state.active_nav_page = "Faculty Dashboard"
                st.rerun()

            if st.button("Student Performance", use_container_width=True, type="secondary"):
                st.session_state.active_nav_page = "Student Performance"
                st.rerun()

            if st.button("Import Assessment Data", use_container_width=True, type="primary"):
                st.session_state.active_nav_page = "Data Import"
                st.rerun()
        else:
            if st.button("Add Exam Result", use_container_width=True, type="secondary"):
                st.session_state.active_nav_page = "Exam Manager"
                st.rerun()

            if st.button("Import CSV/Excel", use_container_width=True, type="secondary"):
                st.session_state.active_nav_page = "Data Import"
                st.rerun()

            if st.button("Create Study Goal", use_container_width=True, type="secondary"):
                st.session_state.active_nav_page = "Study Goals"
                st.rerun()

            if st.button("Open Revision Planner", use_container_width=True, type="primary"):
                st.session_state.active_nav_page = "Revision Planner"
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        # Panel 2: Top Weaknesses
        st.markdown(
            """
            <div style="background:#FFFFFF; border:1px solid #E2EAF3; border-radius:6px; padding:14px 16px; margin-bottom:14px; box-shadow:0 1px 3px rgba(16,43,80,0.03);">
                <div style="font-weight:700; font-size:0.88rem; color:#102B50; margin-bottom:10px;">Top Weaknesses</div>
            """,
            unsafe_allow_html=True
        )
        weak_topics = topic_diag[topic_diag["classification"].isin(["Repeated Weakness", "Weak"])].head(3) if not topic_diag.empty else pd.DataFrame()
        if not weak_topics.empty:
            for _, w_row in weak_topics.iterrows():
                sev_color = "#E35D63" if w_row["classification"] == "Repeated Weakness" else "#D9531E"
                sev_bg = "#FDEBED" if w_row["classification"] == "Repeated Weakness" else "#FDF1EC"
                sev_label = "Critical" if w_row["classification"] == "Repeated Weakness" else "Needs Revision"
                st.markdown(
                    f"""
                    <div style="display:flex; justify-content:space-between; align-items:center; padding:8px 0; border-bottom:1px solid #F1F5F9;">
                        <div>
                            <div style="font-weight:600; font-size:0.84rem; color:#102B50;">{w_row['topic_name']}</div>
                            <div style="font-size:0.74rem; color:#64748B;">{w_row['subject_name']} &bull; {w_row['marks_lost']:.1f} marks lost</div>
                        </div>
                        <span style="background:{sev_bg}; color:{sev_color}; padding:2px 8px; border-radius:3px; font-size:0.7rem; font-weight:700;">{sev_label}</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.markdown("<p style='font-size:0.82rem; color:#16A58A;'>No critical weaknesses detected!</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Panel 3: Recommended Next Steps
        st.markdown(
            """
            <div style="background:#FFFFFF; border:1px solid #E2EAF3; border-radius:6px; padding:14px 16px; margin-bottom:14px; box-shadow:0 1px 3px rgba(16,43,80,0.03);">
                <div style="font-weight:700; font-size:0.88rem; color:#102B50; margin-bottom:10px;">Recommended Next Steps</div>
            """,
            unsafe_allow_html=True
        )
        if not recs_df.empty:
            for _, r_row in recs_df.head(2).iterrows():
                st.markdown(
                    f"""
                    <div style="background:#F8FAFC; border:1px solid #E2EAF3; border-radius:4px; padding:10px 12px; margin-bottom:8px;">
                        <div style="font-weight:700; font-size:0.82rem; color:#2878E5;">{r_row['recommendation_type']}</div>
                        <div style="font-size:0.78rem; color:#475569; margin-top:3px; line-height:1.4;">{r_row['explanation'][:120]}...</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.markdown("<p style='font-size:0.82rem; color:#64748B;'>Maintain current learning schedule.</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
