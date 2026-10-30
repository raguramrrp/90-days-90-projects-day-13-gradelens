-- =============================================================================
-- GradeLens: Academic Performance Analytics & Weakness Detection Platform
-- Database Schema DDL (PostgreSQL Compatible & ANSI SQL Standard)
-- =============================================================================

-- 1. Classes / Batches
CREATE TABLE IF NOT EXISTS classes (
    class_id VARCHAR(50) PRIMARY KEY,
    class_name VARCHAR(100) NOT NULL,
    department VARCHAR(100) NOT NULL,
    academic_year VARCHAR(20) NOT NULL,
    section VARCHAR(10) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Faculty
CREATE TABLE IF NOT EXISTS faculty (
    faculty_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    department VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Students
CREATE TABLE IF NOT EXISTS students (
    student_id VARCHAR(50) PRIMARY KEY,
    student_code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE,
    class_id VARCHAR(50) REFERENCES classes(class_id) ON DELETE SET NULL,
    department VARCHAR(100) NOT NULL,
    academic_year VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Subjects
CREATE TABLE IF NOT EXISTS subjects (
    subject_id VARCHAR(50) PRIMARY KEY,
    subject_code VARCHAR(30) UNIQUE NOT NULL,
    subject_name VARCHAR(150) NOT NULL,
    department VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Student Subjects (Enrollment Map)
CREATE TABLE IF NOT EXISTS student_subjects (
    student_id VARCHAR(50) REFERENCES students(student_id) ON DELETE CASCADE,
    subject_id VARCHAR(50) REFERENCES subjects(subject_id) ON DELETE CASCADE,
    enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (student_id, subject_id)
);

-- 6. Topics & Units
CREATE TABLE IF NOT EXISTS topics (
    topic_id VARCHAR(50) PRIMARY KEY,
    subject_id VARCHAR(50) NOT NULL REFERENCES subjects(subject_id) ON DELETE CASCADE,
    unit_name VARCHAR(100) NOT NULL,
    topic_name VARCHAR(150) NOT NULL,
    subtopic_name VARCHAR(150),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. Exams
CREATE TABLE IF NOT EXISTS exams (
    exam_id VARCHAR(50) PRIMARY KEY,
    exam_name VARCHAR(150) NOT NULL,
    exam_type VARCHAR(50) NOT NULL CHECK (exam_type IN ('Internal Assessment', 'Model Examination', 'Semester Examination', 'Quiz', 'Assignment', 'Practice Test')),
    exam_date DATE NOT NULL,
    academic_period VARCHAR(50) NOT NULL,
    maximum_marks NUMERIC(6, 2) NOT NULL CHECK (maximum_marks > 0),
    class_id VARCHAR(50) REFERENCES classes(class_id) ON DELETE SET NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. Questions
CREATE TABLE IF NOT EXISTS questions (
    question_id VARCHAR(50) PRIMARY KEY,
    exam_id VARCHAR(50) NOT NULL REFERENCES exams(exam_id) ON DELETE CASCADE,
    subject_id VARCHAR(50) NOT NULL REFERENCES subjects(subject_id) ON DELETE CASCADE,
    topic_id VARCHAR(50) NOT NULL REFERENCES topics(topic_id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    maximum_marks NUMERIC(6, 2) NOT NULL CHECK (maximum_marks > 0),
    difficulty VARCHAR(20) NOT NULL CHECK (difficulty IN ('Easy', 'Medium', 'Hard')),
    question_type VARCHAR(50) NOT NULL CHECK (question_type IN ('MCQ', 'Short Answer', 'Numerical', 'Long Answer', 'Code')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 9. Exam Attempts
CREATE TABLE IF NOT EXISTS attempts (
    attempt_id VARCHAR(50) PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    exam_id VARCHAR(50) NOT NULL REFERENCES exams(exam_id) ON DELETE CASCADE,
    total_marks NUMERIC(6, 2) NOT NULL CHECK (total_marks >= 0),
    marks_obtained NUMERIC(6, 2) NOT NULL CHECK (marks_obtained >= 0 AND marks_obtained <= total_marks),
    attempt_date DATE NOT NULL,
    duration_minutes INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_student_exam UNIQUE (student_id, exam_id)
);

-- 10. Question Responses
CREATE TABLE IF NOT EXISTS question_responses (
    response_id VARCHAR(50) PRIMARY KEY,
    attempt_id VARCHAR(50) NOT NULL REFERENCES attempts(attempt_id) ON DELETE CASCADE,
    question_id VARCHAR(50) NOT NULL REFERENCES questions(question_id) ON DELETE CASCADE,
    marks_obtained NUMERIC(6, 2) NOT NULL CHECK (marks_obtained >= 0),
    maximum_marks NUMERIC(6, 2) NOT NULL CHECK (maximum_marks > 0 AND marks_obtained <= maximum_marks),
    answer_status VARCHAR(30) NOT NULL CHECK (answer_status IN ('Correct', 'Partially Correct', 'Incorrect', 'Unanswered')),
    time_spent_seconds INTEGER,
    mistake_category VARCHAR(60) CHECK (mistake_category IN (
        'Conceptual misunderstanding',
        'Calculation error',
        'Formula error',
        'Careless mistake',
        'Incomplete answer',
        'Time-management issue',
        'Unanswered question',
        'Other or unknown',
        'None'
    )),
    confidence_rating VARCHAR(20) CHECK (confidence_rating IN ('Low', 'Medium', 'High')),
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 11. Revision Sessions
CREATE TABLE IF NOT EXISTS revision_sessions (
    session_id VARCHAR(50) PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    subject_id VARCHAR(50) NOT NULL REFERENCES subjects(subject_id) ON DELETE CASCADE,
    topic_id VARCHAR(50) NOT NULL REFERENCES topics(topic_id) ON DELETE CASCADE,
    revision_date DATE NOT NULL,
    duration_minutes INTEGER NOT NULL CHECK (duration_minutes > 0),
    revision_type VARCHAR(50) NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 12. Study Goals
CREATE TABLE IF NOT EXISTS study_goals (
    goal_id VARCHAR(50) PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    subject_id VARCHAR(50) NOT NULL REFERENCES subjects(subject_id) ON DELETE CASCADE,
    topic_id VARCHAR(50) REFERENCES topics(topic_id) ON DELETE SET NULL,
    target_type VARCHAR(50) NOT NULL,
    target_value NUMERIC(6, 2) NOT NULL,
    deadline DATE NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'In Progress' CHECK (status IN ('In Progress', 'Completed', 'Overdue', 'Abandoned')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 13. Revision Tasks
CREATE TABLE IF NOT EXISTS revision_tasks (
    task_id VARCHAR(50) PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    topic_id VARCHAR(50) NOT NULL REFERENCES topics(topic_id) ON DELETE CASCADE,
    task_description TEXT NOT NULL,
    priority VARCHAR(20) NOT NULL CHECK (priority IN ('High', 'Medium', 'Low')),
    scheduled_date DATE NOT NULL,
    completed_at TIMESTAMP,
    status VARCHAR(30) NOT NULL DEFAULT 'Pending' CHECK (status IN ('Pending', 'In Progress', 'Completed', 'Cancelled')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 14. Recommendations
CREATE TABLE IF NOT EXISTS recommendations (
    recommendation_id VARCHAR(50) PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    topic_id VARCHAR(50) NOT NULL REFERENCES topics(topic_id) ON DELETE CASCADE,
    recommendation_type VARCHAR(50) NOT NULL,
    explanation TEXT NOT NULL,
    priority VARCHAR(20) NOT NULL CHECK (priority IN ('High', 'Medium', 'Low')),
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(30) NOT NULL DEFAULT 'Active' CHECK (status IN ('Active', 'In Progress', 'Completed', 'Dismissed'))
);

-- =============================================================================
-- Indexes for Performance
-- =============================================================================
CREATE INDEX IF NOT EXISTS idx_students_class ON students(class_id);
CREATE INDEX IF NOT EXISTS idx_topics_subject ON topics(subject_id);
CREATE INDEX IF NOT EXISTS idx_questions_exam ON questions(exam_id);
CREATE INDEX IF NOT EXISTS idx_questions_topic ON questions(topic_id);
CREATE INDEX IF NOT EXISTS idx_attempts_student ON attempts(student_id);
CREATE INDEX IF NOT EXISTS idx_attempts_exam ON attempts(exam_id);
CREATE INDEX IF NOT EXISTS idx_responses_attempt ON question_responses(attempt_id);
CREATE INDEX IF NOT EXISTS idx_responses_question ON question_responses(question_id);
CREATE INDEX IF NOT EXISTS idx_revisions_student_topic ON revision_sessions(student_id, topic_id);
CREATE INDEX IF NOT EXISTS idx_tasks_student ON revision_tasks(student_id, status);
CREATE INDEX IF NOT EXISTS idx_recommendations_student ON recommendations(student_id, status);
