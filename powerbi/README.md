# GradeLens — Microsoft Power BI Integration Guide

This guide details the complete data model, SQL view integration, CSV data layer, DAX measures, and report layout specification for **GradeLens: Academic Performance Analytics & Weakness Detection Platform**.

Power BI serves as an enterprise BI interface to the GradeLens data engine, enabling deep cohort analysis, cross-subject drill-downs, and institutional reporting.

---

## 1. Connecting Power BI Desktop to GradeLens

You can connect Power BI Desktop to GradeLens via **either** of the two methods below:

### Method A: Connect Directly to PostgreSQL Database (Recommended for Live Relational Sync)
1. Open **Power BI Desktop**.
2. Click **Get Data** > **More...** > **Database** > **PostgreSQL database** > **Connect**.
3. In the Server dialog, enter:
   - **Server**: `localhost:5432`
   - **Database**: `gradelens_db`
   - **Data Connectivity mode**: `Import` (or `DirectQuery` for real-time streaming)
4. Enter credentials (User: `postgres`, Password: as configured in `.env`).
5. Select the **8 Analytical Views**:
   - `vw_student_performance`
   - `vw_subject_performance`
   - `vw_topic_performance`
   - `vw_question_level_analysis`
   - `vw_exam_comparison`
   - `vw_revision_effectiveness`
   - `vw_faculty_class_analytics`
   - `vw_recommendation_summary`
6. Click **Load**.

### Method B: Connect via Curated CSV Data Layer (Zero-Configuration / Offline Mode)
GradeLens includes an automated export pipeline that extracts all 8 database views into clean, typed CSV files.

1. Run the exporter script:
   ```powershell
   python powerbi/export_powerbi.py
   ```
   *Files will be generated in `powerbi/data/`:*
   - `student_performance.csv`
   - `subject_performance.csv`
   - `topic_performance.csv`
   - `question_level_analysis.csv`
   - `exam_comparison.csv`
   - `revision_effectiveness.csv`
   - `faculty_class_analytics.csv`
   - `recommendation_summary.csv`
2. In Power BI Desktop: Click **Get Data** > **Folder** > Browse to `<project-path>/powerbi/data` > **Combine & Load** (or load each CSV individually via **Get Data** > **Text/CSV**).

---

## 2. Power BI Data Model & Star-Schema Relationships

In the **Model View** of Power BI, configure the following single-direction (1-to-many) relationships:

```
[student_performance] (1) --------< (*) [question_level_analysis]
   (student_id)                               (student_id)

[subject_performance] (1) --------< (*) [question_level_analysis]
   (subject_id)                               (subject_id)

[topic_performance]   (1) --------< (*) [question_level_analysis]
   (topic_id)                                 (topic_id)

[exam_comparison]     (1) --------< (*) [question_level_analysis]
   (exam_id)                                  (exam_id)

[student_performance] (1) --------< (*) [revision_effectiveness]
   (student_id)                               (student_id)

[student_performance] (1) --------< (*) [recommendation_summary]
   (student_id)                               (student_id)
```

---

## 3. Essential DAX Measures

Create a dedicated measure table called `_Measures` and add the following DAX calculations:

### 1. Overall Accuracy Percentage
```dax
Overall Accuracy % = 
DIVIDE(
    SUM(question_level_analysis[marks_obtained]),
    SUM(question_level_analysis[maximum_marks]),
    0
) * 100
```

### 2. Total Marks Lost
```dax
Total Marks Lost = 
SUM(question_level_analysis[marks_lost])
```

### 3. Weak Topics Count (< 60% Accuracy)
```dax
Weak Topics Count = 
CALCULATE(
    DISTINCTCOUNT(topic_performance[topic_id]),
    FILTER(
        topic_performance,
        topic_performance[topic_percentage] < 60.0
    )
)
```

### 4. Repeated Mistake Percentage
```dax
Repeated Mistakes % = 
DIVIDE(
    CALCULATE(
        COUNTROWS(question_level_analysis),
        question_level_analysis[mistake_category] <> "None" &&
        question_level_analysis[mistake_category] <> ""
    ),
    COUNTROWS(question_level_analysis),
    0
) * 100
```

### 5. At-Risk Student Count (Score < 50% or >= 2 Weak Topics)
```dax
At-Risk Students = 
CALCULATE(
    DISTINCTCOUNT(student_performance[student_id]),
    FILTER(
        student_performance,
        student_performance[overall_percentage] < 50.0
    )
)
```

### 6. Score Improvement Post-Revision
```dax
Avg Revision Impact Delta = 
AVERAGEX(
    revision_effectiveness,
    revision_effectiveness[score_delta]
)
```

---

## 4. 5-Page Report Design Specification

### Page 1 — Academic Overview (Executive Dashboard)
- **Top Header**: Academic Period Slicer (`Semester 7`), Student Slicer (`All / Aarav / Diya / ...`).
- **KPI Cards**:
  - `Overall Accuracy %` (Target: >= 75%)
  - `Total Assessments Completed`
  - `Total Marks Lost`
  - `Weak Topics Count`
- **Main Visual 1 (Clustered Column Chart)**: Exam-to-Exam Score Progression (`exam_name` on X-axis, `Average Percentage` on Y-axis).
- **Main Visual 2 (Bar Chart)**: Subject-wise Performance comparison with 60% benchmark line.
- **Table**: Student Performance Summary Table with conditional formatting on overall score.

### Page 2 — Subject Intelligence & Curriculum Analysis
- **Slicers**: Subject Name (`DSA`, `DBMS`, `ML`, `OS`).
- **KPI Cards**: Subject Average, Assessment Count, Maximum Possible Marks, Marks Lost.
- **Visual 1 (Donut Chart)**: Marks Lost by Unit / Module.
- **Visual 2 (Horizontal Bar Chart)**: Topic-level Accuracy within selected subject.
- **Visual 3 (Scatter Plot)**: Question Difficulty vs. Average Score.

### Page 3 — Topic Weakness & Repeated Mistake Diagnostics (Core Differentiator)
- **KPI Cards**:
  - Repeated Weakness Topics (Count)
  - Primary Mistake Category (Card showing top mode)
  - Unanswered Questions Count
- **Visual 1 (Heatmap Matrix)**: Student vs. Topic Matrix, colored by Accuracy % (Green: >=75%, Amber: 60-74%, Red: <60%).
- **Visual 2 (Bar Chart)**: Marks Lost by Mistake Category (`Conceptual misunderstanding`, `Calculation error`, `Time-management`, etc.).
- **Visual 3 (Detail Table)**: Question-Level Breakdown showing question text, student answer status, difficulty, marks lost, and teacher remarks.

### Page 4 — Revision Effectiveness Tracking
- **KPI Cards**:
  - Total Revision Hours Logged
  - Number of Topics Revised
  - Average Score Delta Post-Revision (+14.5%)
- **Visual 1 (Slope / Dumbbell Chart)**: Pre-Revision Score vs. Post-Revision Score per Topic.
- **Visual 2 (Scatter Plot)**: Revision Duration (minutes) vs. Subsequent Score Gain.
- **Table**: Revision Sessions Log with student notes, duration, and subsequent examination outcome.

### Page 5 — Faculty & Institutional Cohort Analytics
- **Slicers**: Department, Academic Year, Class Section (`Section A`, `Section B`).
- **KPI Cards**: Class Average %, Pass Rate %, Students Requiring Academic Support.
- **Visual 1 (Histogram)**: Grade Distribution (<50%, 50-60%, 60-75%, 75-90%, >90%).
- **Visual 2 (Table)**: At-Risk Students Flagged with transparent trigger reasons (`Overall < 50%`, `3 Repeated Weak Topics`).
- **Visual 3 (Bar Chart)**: Cohort-Wide Hardest Topics (Highest total marks lost across class).

---

## 5. Automation & Continuous Refresh

Whenever new examination marks or question responses are entered in GradeLens:
1. Re-run `python powerbi/export_powerbi.py` (or automate via Windows Task Scheduler / batch script).
2. Click **Refresh** in Power BI Desktop to immediately update all visual reports and DAX measures.
