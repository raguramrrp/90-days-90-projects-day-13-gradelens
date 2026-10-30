"""
GradeLens Realistic Synthetic Dataset Generator.
Populates the database with multi-student, multi-subject, question-level data
featuring repeated weaknesses, improving trajectories, revision logs, and goals.
"""

import uuid
from datetime import date, timedelta
from typing import Dict, Any, List, Optional
import pandas as pd
from src.database.connection import db_manager, DatabaseManager
from src.database.schema import init_database
from src.database.repository import Repository

# Synthetic Classes
CLASSES_DATA = [
    ("cls_ai_a", "B.Tech AI & DS - Section A", "Artificial Intelligence & Data Science", "2023-2027", "A"),
    ("cls_ai_b", "B.Tech AI & DS - Section B", "Artificial Intelligence & Data Science", "2023-2027", "B")
]

# Synthetic Faculty
FACULTY_DATA = [
    ("fac_01", "Dr. K. Ramanathan", "k.ramanathan@gradelens.edu", "Artificial Intelligence & Data Science"),
    ("fac_02", "Prof. Sneha Deshmukh", "s.deshmukh@gradelens.edu", "Computer Science & Engineering")
]

# Synthetic Students with varied personas
STUDENTS_DATA = [
    ("stu_01", "STU101", "Aarav Sharma", "aarav.sharma@gradelens.edu", "cls_ai_a", "AI & DS", "Year 4"),
    ("stu_02", "STU102", "Diya Patel", "diya.patel@gradelens.edu", "cls_ai_a", "AI & DS", "Year 4"),
    ("stu_03", "STU103", "Rohan Iyer", "rohan.iyer@gradelens.edu", "cls_ai_a", "AI & DS", "Year 4"),
    ("stu_04", "STU104", "Ananya Sen", "ananya.sen@gradelens.edu", "cls_ai_a", "AI & DS", "Year 4"),
    ("stu_05", "STU105", "Vikram Nair", "vikram.nair@gradelens.edu", "cls_ai_a", "AI & DS", "Year 4"),
    ("stu_06", "STU106", "Pooja Hegde", "pooja.hegde@gradelens.edu", "cls_ai_a", "AI & DS", "Year 4"),
]

# Synthetic Subjects
SUBJECTS_DATA = [
    ("sub_dsa", "CS701", "Data Structures & Algorithms", "Computer Science"),
    ("sub_dbms", "CS702", "Database Management Systems", "Computer Science"),
    ("sub_ml", "AI701", "Machine Learning & Pattern Recognition", "Artificial Intelligence"),
    ("sub_os", "CS703", "Operating Systems & Concurrency", "Computer Science")
]

# Synthetic Topics
TOPICS_DATA = [
    # DSA
    ("top_dsa_1", "sub_dsa", "Unit 1: Trees & Graphs", "Binary Search Trees", "Balancing & Traversal"),
    ("top_dsa_2", "sub_dsa", "Unit 2: Dynamic Programming", "DP Optimizations", "Knapsack & LCS"),
    ("top_dsa_3", "sub_dsa", "Unit 3: Graph Algorithms", "Shortest Path & MST", "Dijkstra & Kruskal"),
    # DBMS
    ("top_db_1", "sub_dbms", "Unit 1: Relational Modeling", "Relational Algebra", "Join & Projection Operations"),
    ("top_db_2", "sub_dbms", "Unit 2: SQL Advanced", "Window Functions & Joins", "Aggregations & CTEs"),
    ("top_db_3", "sub_dbms", "Unit 3: Transactions", "ACID & Concurrency Control", "Two-Phase Locking"),
    # ML
    ("top_ml_1", "sub_ml", "Unit 1: Supervised Learning", "Linear & Logistic Regression", "Gradient Descent & Cost Functions"),
    ("top_ml_2", "sub_ml", "Unit 2: Tree-based Models", "Decision Trees & Random Forests", "Splitting Criteria & Gini Impurity"),
    ("top_ml_3", "sub_ml", "Unit 3: Neural Networks", "Backpropagation & Optimizers", "Activation Functions & Overfitting"),
    # OS
    ("top_os_1", "sub_os", "Unit 1: CPU Scheduling", "Preemptive Scheduling", "Round Robin & Priority"),
    ("top_os_2", "sub_os", "Unit 2: Memory Management", "Paging & Segmentation", "Virtual Memory & Page Replacement")
]

# Synthetic Exams
EXAMS_DATA = [
    ("ex_ia1", "Internal Assessment 1", "Internal Assessment", "2026-08-20", "Semester 7", 50.0, "cls_ai_a", "IA1 on Units 1 and 2"),
    ("ex_quiz1", "Diagnostic Quiz 1", "Quiz", "2026-09-05", "Semester 7", 20.0, "cls_ai_a", "Mid-term MCQ Diagnostic"),
    ("ex_ia2", "Internal Assessment 2", "Internal Assessment", "2026-09-28", "Semester 7", 50.0, "cls_ai_a", "IA2 on Units 2 and 3"),
    ("ex_model", "Model Examination", "Model Examination", "2026-10-18", "Semester 7", 100.0, "cls_ai_a", "Full-syllabus Model Assessment")
]

# Synthetic Questions for each exam (balanced across subjects & topics)
QUESTIONS_DATA = [
    # IA 1 Questions (Total 50 marks)
    ("q_ia1_1", "ex_ia1", "sub_dsa", "top_dsa_1", "Explain AVL tree rotation with an unbalanced insertion example.", 10.0, "Medium", "Long Answer"),
    ("q_ia1_2", "ex_ia1", "sub_dsa", "top_dsa_2", "Solve 0/1 Knapsack using Dynamic Programming with state transition table.", 15.0, "Hard", "Numerical"),
    ("q_ia1_3", "ex_ia1", "sub_dbms", "top_db_1", "Write Relational Algebra expressions for division and natural join operations.", 10.0, "Medium", "Short Answer"),
    ("q_ia1_4", "ex_ia1", "sub_dbms", "top_db_2", "Write an SQL query using DENSE_RANK() and PARTITION BY to find top 2 scores per department.", 15.0, "Hard", "Code"),

    # Quiz 1 Questions (Total 20 marks)
    ("q_qz1_1", "ex_quiz1", "sub_dsa", "top_dsa_2", "What is the time complexity of top-down memoized Fibonacci?", 5.0, "Easy", "MCQ"),
    ("q_qz1_2", "ex_quiz1", "sub_dbms", "top_db_2", "Which clause is mandatory in SQL window functions?", 5.0, "Easy", "MCQ"),
    ("q_qz1_3", "ex_quiz1", "sub_ml", "top_ml_1", "In Gradient Descent, what happens if learning rate alpha is excessively large?", 5.0, "Medium", "Short Answer"),
    ("q_qz1_4", "ex_quiz1", "sub_os", "top_os_1", "Which CPU scheduling algorithm can lead to starvation?", 5.0, "Easy", "MCQ"),

    # IA 2 Questions (Total 50 marks)
    ("q_ia2_1", "ex_ia2", "sub_dsa", "top_dsa_3", "Implement Dijkstra's shortest path algorithm using a min-heap priority queue.", 15.0, "Hard", "Code"),
    ("q_ia2_2", "ex_ia2", "sub_dbms", "top_db_3", "Demonstrate how Two-Phase Locking (2PL) guarantees conflict serializability.", 10.0, "Medium", "Long Answer"),
    ("q_ia2_3", "ex_ia2", "sub_ml", "top_ml_1", "Derive the weight update rule for batch Gradient Descent in Logistic Regression.", 15.0, "Hard", "Numerical"),
    ("q_ia2_4", "ex_ia2", "sub_os", "top_os_2", "Calculate page faults for FIFO and LRU algorithms given reference string [1, 2, 3, 4, 2, 1, 5].", 10.0, "Medium", "Numerical"),

    # Model Exam Questions (Total 100 marks)
    ("q_md_1", "ex_model", "sub_dsa", "top_dsa_1", "Construct a Red-Black Tree and verify balance properties.", 15.0, "Hard", "Long Answer"),
    ("q_md_2", "ex_model", "sub_dsa", "top_dsa_2", "Formulate Longest Common Subsequence (LCS) using DP recursion and reconstruct string.", 15.0, "Hard", "Numerical"),
    ("q_md_3", "ex_model", "sub_dbms", "top_db_2", "Write complex multi-table SQL queries utilizing CTEs and Window Functions.", 15.0, "Hard", "Code"),
    ("q_md_4", "ex_model", "sub_dbms", "top_db_3", "Explain Deadlock detection, wait-for graphs, and recovery in DBMS.", 10.0, "Medium", "Short Answer"),
    ("q_md_5", "ex_model", "sub_ml", "top_ml_1", "Compare Batch, Stochastic, and Mini-batch Gradient Descent convergence.", 15.0, "Medium", "Long Answer"),
    ("q_md_6", "ex_model", "sub_ml", "top_ml_2", "Calculate Information Gain and Gini Index to select root feature for Decision Tree.", 15.0, "Medium", "Numerical"),
    ("q_md_7", "ex_model", "sub_os", "top_os_2", "Analyze Thrashing in Virtual Memory and Working-Set model.", 15.0, "Hard", "Long Answer")
]


def seed_database(manager: DatabaseManager = None, force_reset: bool = False) -> Dict[str, Any]:
    """
    Populates all entities and generates realistic question responses.
    Deterministic: yields reproducible analytics on every seed.
    """
    mgr = manager or db_manager

    if force_reset:
        init_database(mgr)

    conn = mgr.get_connection()
    cursor = conn.cursor()

    try:
        # Check if already seeded
        cursor.execute("SELECT COUNT(*) FROM students;")
        count = cursor.fetchone()[0]
        if count > 0 and not force_reset:
            return {"status": "Already seeded", "students_count": count}

        # 1. Insert Classes
        for cls in CLASSES_DATA:
            cursor.execute("""
                INSERT INTO classes (class_id, class_name, department, academic_year, section)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(class_id) DO NOTHING;
            """, cls)

        # 2. Insert Faculty
        for fac in FACULTY_DATA:
            cursor.execute("""
                INSERT INTO faculty (faculty_id, name, email, department)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(faculty_id) DO NOTHING;
            """, fac)

        # 3. Insert Students
        for stu in STUDENTS_DATA:
            cursor.execute("""
                INSERT INTO students (student_id, student_code, name, email, class_id, department, academic_year)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(student_id) DO NOTHING;
            """, stu)

        # 4. Insert Subjects
        for sub in SUBJECTS_DATA:
            cursor.execute("""
                INSERT INTO subjects (subject_id, subject_code, subject_name, department)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(subject_id) DO NOTHING;
            """, sub)

        # 5. Enroll Students in Subjects
        for stu in STUDENTS_DATA:
            for sub in SUBJECTS_DATA:
                cursor.execute("""
                    INSERT INTO student_subjects (student_id, subject_id)
                    VALUES (?, ?)
                    ON CONFLICT(student_id, subject_id) DO NOTHING;
                """, (stu[0], sub[0]))

        # 6. Insert Topics
        for top in TOPICS_DATA:
            cursor.execute("""
                INSERT INTO topics (topic_id, subject_id, unit_name, topic_name, subtopic_name)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(topic_id) DO NOTHING;
            """, top)

        # 7. Insert Exams
        for ex in EXAMS_DATA:
            cursor.execute("""
                INSERT INTO exams (exam_id, exam_name, exam_type, exam_date, academic_period, maximum_marks, class_id, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(exam_id) DO NOTHING;
            """, ex)

        # 8. Insert Questions
        for q in QUESTIONS_DATA:
            cursor.execute("""
                INSERT INTO questions (question_id, exam_id, subject_id, topic_id, question_text, maximum_marks, difficulty, question_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(question_id) DO NOTHING;
            """, q)

        # 9. Generate Student Performance & Question Responses
        # Persona definitions:
        # stu_01 (Aarav): Repeated weakness in Dynamic Programming (top_dsa_2) and Window Functions & Joins (top_db_2)
        # stu_02 (Diya): Improving in Gradient Descent (top_ml_1) - initially low, revised, then high
        # stu_03 (Rohan): High achiever (85-100% across all)
        # stu_04 (Ananya): Struggling overall (<50%)
        # stu_05 (Vikram): Time-management lapses (leaves questions unanswered)
        # stu_06 (Pooja): Average student with moderate monitoring topics

        questions_by_exam = {}
        for q in QUESTIONS_DATA:
            questions_by_exam.setdefault(q[1], []).append(q)

        total_responses = 0

        for stu in STUDENTS_DATA:
            s_id = stu[0]

            for ex in EXAMS_DATA:
                ex_id = ex[0]
                ex_date = ex[3]
                q_list = questions_by_exam.get(ex_id, [])

                exam_obtained = 0.0
                exam_total = sum(q[5] for q in q_list)
                attempt_id = f"att_{s_id}_{ex_id}"

                # Calculate question responses according to persona
                responses_to_insert = []
                for q in q_list:
                    q_id = q[0]
                    t_id = q[3]
                    max_m = q[5]
                    diff = q[6]

                    # Default performance factors
                    score_factor = 0.75
                    ans_status = "Correct"
                    mistake = "None"
                    conf = "High"

                    # Persona customizations
                    if s_id == "stu_01":  # Aarav Sharma: Repeated Weakness in DP and Window Functions
                        if t_id in ["top_dsa_2", "top_db_2"]:
                            score_factor = 0.35  # Consistently < 60%
                            ans_status = "Incorrect" if score_factor < 0.2 else "Partially Correct"
                            mistake = "Calculation error" if "Numerical" in q[7] else "Conceptual misunderstanding"
                            conf = "Medium"
                        else:
                            score_factor = 0.80

                    elif s_id == "stu_02":  # Diya Patel: Improving student in Gradient Descent
                        if t_id == "top_ml_1":
                            if ex_id in ["ex_ia1", "ex_quiz1", "ex_ia2"]:
                                score_factor = 0.40  # Pre-revision low
                                ans_status = "Partially Correct"
                                mistake = "Formula error"
                                conf = "Low"
                            else:
                                score_factor = 0.90  # Post-revision significant gain!
                                ans_status = "Correct"
                                mistake = "None"
                                conf = "High"
                        else:
                            score_factor = 0.78

                    elif s_id == "stu_03":  # Rohan Iyer: Top Performer
                        score_factor = 0.92
                        ans_status = "Correct"
                        mistake = "None"
                        conf = "High"

                    elif s_id == "stu_04":  # Ananya Sen: Struggling overall (<50%)
                        score_factor = 0.42
                        ans_status = "Incorrect" if diff in ["Medium", "Hard"] else "Partially Correct"
                        mistake = "Conceptual misunderstanding"
                        conf = "Low"

                    elif s_id == "stu_05":  # Vikram Nair: Time management issues
                        if q_id in ["q_ia1_4", "q_ia2_3", "q_md_7"]:
                            score_factor = 0.0
                            ans_status = "Unanswered"
                            mistake = "Time-management issue"
                            conf = "Low"
                        else:
                            score_factor = 0.70

                    else:  # Pooja Hegde: Average
                        score_factor = 0.65

                    obtained = round(max_m * score_factor, 1)
                    if obtained == max_m:
                        ans_status = "Correct"
                        mistake = "None"
                    elif obtained == 0.0 and ans_status != "Unanswered":
                        ans_status = "Incorrect"

                    exam_obtained += obtained
                    resp_id = f"resp_{s_id}_{q_id}"
                    time_spent = 300 if ans_status != "Unanswered" else 20
                    remarks = f"Assessed on {ex_date}"

                    responses_to_insert.append((
                        resp_id, attempt_id, q_id, obtained, max_m,
                        ans_status, time_spent, mistake, conf, remarks
                    ))

                # Insert attempt
                cursor.execute("""
                    INSERT INTO attempts (attempt_id, student_id, exam_id, total_marks, marks_obtained, attempt_date, duration_minutes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(student_id, exam_id) DO NOTHING;
                """, (attempt_id, s_id, ex_id, exam_total, exam_obtained, ex_date, 90))

                # Insert responses
                for r in responses_to_insert:
                    cursor.execute("""
                        INSERT INTO question_responses (
                            response_id, attempt_id, question_id, marks_obtained, maximum_marks,
                            answer_status, time_spent_seconds, mistake_category, confidence_rating, remarks
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(response_id) DO NOTHING;
                    """, r)
                    total_responses += 1

        # 10. Insert Revision Sessions
        # Diya Patel had revision sessions on Gradient Descent before Model Exam (Oct 10 & Oct 14)
        revisions = [
            ("rev_01", "stu_02", "sub_ml", "top_ml_1", "2026-10-05", 60, "Practice Problems", "Reviewed step-size updates and derivation"),
            ("rev_02", "stu_02", "sub_ml", "top_ml_1", "2026-10-12", 45, "Concept Review", "Flashcards and formula sheet for backpropagation"),
            ("rev_03", "stu_01", "sub_dsa", "top_dsa_2", "2026-09-10", 30, "Self Study", "Attempted 0/1 knapsack problems"),
            ("rev_04", "stu_03", "sub_dbms", "top_db_2", "2026-09-15", 40, "Peer Discussion", "Discussed lead/lag and partition bounds"),
        ]
        for rev in revisions:
            cursor.execute("""
                INSERT INTO revision_sessions (session_id, student_id, subject_id, topic_id, revision_date, duration_minutes, revision_type, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(session_id) DO NOTHING;
            """, rev)

        # 11. Insert Revision Tasks
        tasks = [
            ("tsk_01", "stu_01", "top_dsa_2", "Complete 5 standard DP problems on LeetCode", "High", "2026-11-02", "Pending"),
            ("tsk_02", "stu_01", "top_db_2", "Practice Window Functions syntax with mock dataset", "High", "2026-11-03", "Pending"),
            ("tsk_03", "stu_02", "top_ml_1", "Re-derive mini-batch gradient descent update equations", "Medium", "2026-10-25", "Completed"),
            ("tsk_04", "stu_05", "top_os_2", "Timed 30-minute practice test on paging and virtual memory", "High", "2026-11-04", "In Progress")
        ]
        for tsk in tasks:
            cursor.execute("""
                INSERT INTO revision_tasks (task_id, student_id, topic_id, task_description, priority, scheduled_date, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(task_id) DO NOTHING;
            """, tsk)

        # 12. Insert Study Goals
        goals = [
            ("goal_01", "stu_01", "sub_dsa", "top_dsa_2", "Topic Score Target", 75.0, "2026-11-15", "In Progress"),
            ("goal_02", "stu_01", "sub_dbms", "top_db_2", "Topic Score Target", 80.0, "2026-11-20", "In Progress"),
            ("goal_03", "stu_02", "sub_ml", "top_ml_1", "Topic Score Target", 85.0, "2026-10-20", "Completed"),
            ("goal_04", "stu_04", "sub_dsa", None, "Subject Overall Target", 60.0, "2026-11-30", "In Progress")
        ]
        for g in goals:
            cursor.execute("""
                INSERT INTO study_goals (goal_id, student_id, subject_id, topic_id, target_type, target_value, deadline, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(goal_id) DO NOTHING;
            """, g)

        conn.commit()

        # 13. Auto-generate baseline recommendations for all students
        from src.recommendations.engine import recommendation_engine
        for stu in STUDENTS_DATA:
            try:
                recommendation_engine.generate_recommendations_for_student(stu[0])
            except Exception:
                pass

        return {
            "status": "Success",
            "students": len(STUDENTS_DATA),
            "subjects": len(SUBJECTS_DATA),
            "topics": len(TOPICS_DATA),
            "exams": len(EXAMS_DATA),
            "questions": len(QUESTIONS_DATA),
            "responses": total_responses,
            "revisions": len(revisions)
        }
    finally:
        conn.close()


if __name__ == "__main__":
    res = seed_database(force_reset=True)
    print("Seed execution finished:", res)
