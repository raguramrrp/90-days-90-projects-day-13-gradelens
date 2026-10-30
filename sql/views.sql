-- =============================================================================
-- GradeLens: Reusable Analytical SQL Views for Power BI & Streamlit Analytics
-- =============================================================================

-- View 1: Student Overall Performance
CREATE VIEW IF NOT EXISTS vw_student_performance AS
SELECT 
    s.student_id,
    s.student_code,
    s.name AS student_name,
    s.department,
    s.academic_year,
    c.class_name,
    COUNT(a.attempt_id) AS total_exams_attempted,
    COALESCE(SUM(a.total_marks), 0) AS total_possible_marks,
    COALESCE(SUM(a.marks_obtained), 0) AS total_marks_obtained,
    ROUND(
        CASE 
            WHEN SUM(a.total_marks) > 0 
            THEN (SUM(a.marks_obtained) * 100.0 / SUM(a.total_marks)) 
            ELSE 0 
        END, 2
    ) AS overall_percentage,
    ROUND(AVG(a.marks_obtained * 100.0 / NULLIF(a.total_marks, 0)), 2) AS average_exam_percentage
FROM students s
LEFT JOIN classes c ON s.class_id = c.class_id
LEFT JOIN attempts a ON s.student_id = a.student_id
GROUP BY s.student_id, s.student_code, s.name, s.department, s.academic_year, c.class_name;

-- View 2: Subject Performance Intelligence
CREATE VIEW IF NOT EXISTS vw_subject_performance AS
SELECT 
    sub.subject_id,
    sub.subject_code,
    sub.subject_name,
    sub.department,
    s.student_id,
    s.name AS student_name,
    COUNT(DISTINCT e.exam_id) AS total_assessments,
    COALESCE(SUM(qr.maximum_marks), 0) AS total_max_marks,
    COALESCE(SUM(qr.marks_obtained), 0) AS total_obtained_marks,
    COALESCE(SUM(qr.maximum_marks - qr.marks_obtained), 0) AS total_marks_lost,
    ROUND(
        CASE 
            WHEN SUM(qr.maximum_marks) > 0 
            THEN (SUM(qr.marks_obtained) * 100.0 / SUM(qr.maximum_marks)) 
            ELSE 0 
        END, 2
    ) AS subject_percentage,
    MAX(a.marks_obtained * 100.0 / NULLIF(a.total_marks, 0)) AS highest_score_pct,
    MIN(a.marks_obtained * 100.0 / NULLIF(a.total_marks, 0)) AS lowest_score_pct
FROM subjects sub
CROSS JOIN students s
LEFT JOIN questions q ON sub.subject_id = q.subject_id
LEFT JOIN exams e ON q.exam_id = e.exam_id
LEFT JOIN attempts a ON e.exam_id = a.exam_id AND s.student_id = a.student_id
LEFT JOIN question_responses qr ON a.attempt_id = qr.attempt_id AND q.question_id = qr.question_id
GROUP BY sub.subject_id, sub.subject_code, sub.subject_name, sub.department, s.student_id, s.name;

-- View 3: Topic Performance & Weakness Analytics
CREATE VIEW IF NOT EXISTS vw_topic_performance AS
SELECT 
    t.topic_id,
    t.topic_name,
    t.unit_name,
    sub.subject_id,
    sub.subject_name,
    sub.subject_code,
    a.student_id,
    s.name AS student_name,
    COUNT(qr.response_id) AS questions_attempted,
    COALESCE(SUM(qr.maximum_marks), 0) AS topic_max_marks,
    COALESCE(SUM(qr.marks_obtained), 0) AS topic_marks_obtained,
    COALESCE(SUM(qr.maximum_marks - qr.marks_obtained), 0) AS marks_lost,
    ROUND(
        CASE 
            WHEN SUM(qr.maximum_marks) > 0 
            THEN (SUM(qr.marks_obtained) * 100.0 / SUM(qr.maximum_marks)) 
            ELSE 0 
        END, 2
    ) AS topic_percentage,
    SUM(CASE WHEN qr.answer_status = 'Incorrect' THEN 1 ELSE 0 END) AS incorrect_count,
    SUM(CASE WHEN qr.answer_status = 'Partially Correct' THEN 1 ELSE 0 END) AS partial_count,
    SUM(CASE WHEN qr.answer_status = 'Correct' THEN 1 ELSE 0 END) AS correct_count,
    SUM(CASE WHEN qr.answer_status = 'Unanswered' THEN 1 ELSE 0 END) AS unanswered_count
FROM topics t
JOIN subjects sub ON t.subject_id = sub.subject_id
JOIN questions q ON t.topic_id = q.topic_id
JOIN question_responses qr ON q.question_id = qr.question_id
JOIN attempts a ON qr.attempt_id = a.attempt_id
JOIN students s ON a.student_id = s.student_id
GROUP BY t.topic_id, t.topic_name, t.unit_name, sub.subject_id, sub.subject_name, sub.subject_code, a.student_id, s.name;

-- View 4: Question-Level Detailed Analysis
CREATE VIEW IF NOT EXISTS vw_question_level_analysis AS
SELECT 
    qr.response_id,
    a.student_id,
    s.student_code,
    s.name AS student_name,
    e.exam_id,
    e.exam_name,
    e.exam_type,
    e.exam_date,
    sub.subject_id,
    sub.subject_name,
    t.topic_id,
    t.topic_name,
    t.unit_name,
    q.question_id,
    q.question_text,
    q.difficulty,
    q.question_type,
    qr.maximum_marks,
    qr.marks_obtained,
    (qr.maximum_marks - qr.marks_obtained) AS marks_lost,
    ROUND((qr.marks_obtained * 100.0 / NULLIF(qr.maximum_marks, 0)), 2) AS score_percentage,
    qr.answer_status,
    qr.mistake_category,
    qr.confidence_rating,
    qr.time_spent_seconds,
    qr.remarks
FROM question_responses qr
JOIN attempts a ON qr.attempt_id = a.attempt_id
JOIN students s ON a.student_id = s.student_id
JOIN questions q ON qr.question_id = q.question_id
JOIN exams e ON q.exam_id = e.exam_id
JOIN subjects sub ON q.subject_id = sub.subject_id
JOIN topics t ON q.topic_id = t.topic_id;

-- View 5: Exam Comparison Intelligence
CREATE VIEW IF NOT EXISTS vw_exam_comparison AS
SELECT 
    e.exam_id,
    e.exam_name,
    e.exam_type,
    e.exam_date,
    e.academic_period,
    e.maximum_marks AS exam_max_marks,
    c.class_name,
    COUNT(a.attempt_id) AS total_students_appeared,
    ROUND(AVG(a.marks_obtained), 2) AS class_average_marks,
    ROUND(AVG(a.marks_obtained * 100.0 / NULLIF(a.total_marks, 0)), 2) AS class_average_percentage,
    MAX(a.marks_obtained) AS highest_marks,
    MIN(a.marks_obtained) AS lowest_marks
FROM exams e
LEFT JOIN classes c ON e.class_id = c.class_id
LEFT JOIN attempts a ON e.exam_id = a.exam_id
GROUP BY e.exam_id, e.exam_name, e.exam_type, e.exam_date, e.academic_period, e.maximum_marks, c.class_name;

-- View 6: Revision Effectiveness Correlation
CREATE VIEW IF NOT EXISTS vw_revision_effectiveness AS
SELECT 
    rs.student_id,
    s.name AS student_name,
    sub.subject_id,
    sub.subject_name,
    t.topic_id,
    t.topic_name,
    COUNT(DISTINCT rs.session_id) AS total_revision_sessions,
    COALESCE(SUM(rs.duration_minutes), 0) AS total_revision_minutes,
    MIN(rs.revision_date) AS first_revision_date,
    MAX(rs.revision_date) AS last_revision_date
FROM revision_sessions rs
JOIN students s ON rs.student_id = s.student_id
JOIN subjects sub ON rs.subject_id = sub.subject_id
JOIN topics t ON rs.topic_id = t.topic_id
GROUP BY rs.student_id, s.name, sub.subject_id, sub.subject_name, t.topic_id, t.topic_name;

-- View 7: Faculty Class-Level Analytics
CREATE VIEW IF NOT EXISTS vw_faculty_class_analytics AS
SELECT 
    c.class_id,
    c.class_name,
    c.department,
    c.academic_year,
    sub.subject_id,
    sub.subject_name,
    COUNT(DISTINCT s.student_id) AS enrolled_students,
    ROUND(AVG(a.marks_obtained * 100.0 / NULLIF(a.total_marks, 0)), 2) AS subject_class_average_pct,
    SUM(CASE WHEN (a.marks_obtained * 100.0 / NULLIF(a.total_marks, 0)) < 50.0 THEN 1 ELSE 0 END) AS students_below_threshold
FROM classes c
JOIN students s ON c.class_id = s.class_id
JOIN student_subjects ss ON s.student_id = ss.student_id
JOIN subjects sub ON ss.subject_id = sub.subject_id
LEFT JOIN questions q ON sub.subject_id = q.subject_id
LEFT JOIN exams e ON q.exam_id = e.exam_id AND e.class_id = c.class_id
LEFT JOIN attempts a ON e.exam_id = a.exam_id AND s.student_id = a.student_id
GROUP BY c.class_id, c.class_name, c.department, c.academic_year, sub.subject_id, sub.subject_name;

-- View 8: Recommendation Summary
CREATE VIEW IF NOT EXISTS vw_recommendation_summary AS
SELECT 
    r.recommendation_id,
    r.student_id,
    s.name AS student_name,
    sub.subject_name,
    t.topic_name,
    r.recommendation_type,
    r.priority,
    r.explanation,
    r.status,
    r.generated_at
FROM recommendations r
JOIN students s ON r.student_id = s.student_id
JOIN topics t ON r.topic_id = t.topic_id
JOIN subjects sub ON t.subject_id = sub.subject_id;
