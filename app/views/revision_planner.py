"""
GradeLens View 5: Revision Planner.
Targeted daily study tasks, weak concept prioritization, and weekly schedule management.
Strict light design system: #F5F8FC / #FFFFFF / #102B50 / #2878E5, zero emojis.
"""

import uuid
import streamlit as st
import pandas as pd
from src.database.repository import Repository, repo
from app.components.metrics import render_kpi_card, render_section_header
from app.auth import get_current_user_context


def render_revision_planner_view(repository: Repository = repo):
    user = get_current_user_context(repository)
    st.markdown(
        """
        <div style="margin-bottom: 20px;">
            <h1 style="font-size: 1.65rem; font-weight: 700; color: #102B50; margin: 0 0 4px 0;">
                Revision Planner
            </h1>
            <p style="color: #64748B; font-size: 0.88rem; margin: 0;">
                Turn weakness insights into daily structured tasks, prioritize weak topics, and organize your weekly study plan.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    student_id = user["id"] if user["role"] == "Student" else None
    if not student_id:
        st.info("Please select an active student from the sidebar to view personal revision tasks.")
        return

    tasks_df = repository.get_revision_tasks(student_id=student_id)

    # Summary KPI row
    pending_count = (tasks_df["status"] == "Pending").sum() if not tasks_df.empty else 0
    in_prog_count = (tasks_df["status"] == "In Progress").sum() if not tasks_df.empty else 0
    completed_count = (tasks_df["status"] == "Completed").sum() if not tasks_df.empty else 0
    high_prio_count = (tasks_df["priority"] == "High").sum() if not tasks_df.empty else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card("Pending Tasks", str(pending_count), f"{in_prog_count} in progress")
    with c2:
        render_kpi_card("High Priority", str(high_prio_count), "Urgent weak topics")
    with c3:
        render_kpi_card("Completed Tasks", str(completed_count), "Verified finished")
    with c4:
        total_tasks = len(tasks_df) if not tasks_df.empty else 0
        render_kpi_card("Total Planned", str(total_tasks), "Assigned tasks")

    render_section_header("Task Management", "Create new revision tasks or update progress on existing assignments.")

    col_form, col_list = st.columns([1, 2])

    with col_form:
        st.markdown("<div style='font-weight:600; font-size:0.88rem; color:#102B50; margin-bottom:8px;'>Schedule Revision Task</div>", unsafe_allow_html=True)
        with st.form("create_revision_task_form"):
            topics_df = repository.get_topics()
            top_opts = {r["topic_id"]: f"{r['subject_code']} - {r['topic_name']}" for _, r in topics_df.iterrows()} if not topics_df.empty else {}
            sel_topic = st.selectbox("Topic", options=list(top_opts.keys()), format_func=lambda k: top_opts[k])
            task_desc = st.text_input("Task Description", value="Review practice problems and summary notes")
            priority = st.selectbox("Priority Level", options=["High", "Medium", "Low"], index=0)
            sched_date = st.date_input("Scheduled Date", value=pd.Timestamp.now().date())

            submitted = st.form_submit_button("Add Task", type="primary", use_container_width=True)
            if submitted:
                task_id = f"tsk_{uuid.uuid4().hex[:8]}"
                repository.create_revision_task(
                    task_id=task_id,
                    student_id=student_id,
                    topic_id=sel_topic,
                    task_description=task_desc,
                    priority=priority,
                    scheduled_date=str(sched_date)
                )
                st.success("Revision task created.")
                st.rerun()

    with col_list:
        st.markdown("<div style='font-weight:600; font-size:0.88rem; color:#102B50; margin-bottom:8px;'>Scheduled Tasks</div>", unsafe_allow_html=True)
        if not tasks_df.empty:
            for _, row in tasks_df.iterrows():
                tid = row["task_id"]
                status = row["status"]
                priority = row["priority"]
                p_border = "#E35D63" if priority == "High" else ("#E6A52E" if priority == "Medium" else "#2878E5")
                status_color = "#16A58A" if status == "Completed" else ("#2878E5" if status == "In Progress" else "#64748B")

                with st.container():
                    c_main, c_done, c_del = st.columns([3.5, 1, 0.8])
                    with c_main:
                        card_html = (
                            f'<div style="background-color:#FFFFFF; border:1px solid #E2EAF3; border-left:4px solid {p_border}; '
                            f'border-radius:4px; padding:10px 14px; margin-bottom:8px;">'
                            f'<div style="font-weight:600; font-size:0.88rem; color:#102B50;">{row["task_description"]}</div>'
                            f'<div style="font-size:0.78rem; color:#64748B; margin-top:3px;">'
                            f'{row["subject_name"]} &bull; {row["topic_name"]} &bull; Scheduled: {row["scheduled_date"]} &bull; '
                            f'<span style="color:{status_color}; font-weight:600;">{status}</span>'
                            f'</div>'
                            f'</div>'
                        )
                        st.markdown(card_html, unsafe_allow_html=True)
                    with c_done:
                        st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
                        if status != "Completed":
                            if st.button("Mark Done", key=f"btn_done_{tid}", use_container_width=True):
                                repository.update_task_status(tid, "Completed")
                                st.rerun()
                        else:
                            if st.button("Reopen", key=f"btn_reopen_{tid}", use_container_width=True):
                                repository.update_task_status(tid, "Pending")
                                st.rerun()
                    with c_del:
                        st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
                        if st.button("Delete", key=f"btn_del_{tid}", use_container_width=True):
                            repository.delete_revision_task(tid)
                            st.rerun()
        else:
            st.info("No revision tasks currently scheduled.")

    # Weekly Study Schedule Overview
    render_section_header("Weekly Study Schedule", "Planned distribution of revision tasks across the current week.")
    days_data = [
        {"Day": "Monday", "Topics": "Database Transactions & ACID", "Type": "Concept Review", "Duration": "45 min", "Status": "Completed"},
        {"Day": "Tuesday", "Topics": "Window Functions & Complex Joins", "Type": "Practice Questions", "Duration": "60 min", "Status": "In Progress"},
        {"Day": "Wednesday", "Topics": "Deadlock Detection & Prevention", "Type": "Problem Solving", "Duration": "45 min", "Status": "Scheduled"},
        {"Day": "Thursday", "Topics": "Process Synchronization & Semaphores", "Type": "Formula & Theorem Drill", "Duration": "50 min", "Status": "Scheduled"},
        {"Day": "Friday", "Topics": "Dynamic Programming (Knapsack)", "Type": "Code Implementation", "Duration": "60 min", "Status": "Scheduled"},
        {"Day": "Saturday", "Topics": "Mock Assessment 1 (Timed)", "Type": "Exam Simulation", "Duration": "90 min", "Status": "Scheduled"},
        {"Day": "Sunday", "Topics": "Weekly Error Review & Mistake Journal", "Type": "Retrospective Review", "Duration": "30 min", "Status": "Scheduled"}
    ]
    st.dataframe(pd.DataFrame(days_data), use_container_width=True, hide_index=True)
