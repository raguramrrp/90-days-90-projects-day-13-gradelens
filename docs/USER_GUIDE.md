# GradeLens: User & Operational Guide

## 1. Navigating the Workspace
GradeLens provides a context-aware navigation bar in the left sidebar:
- **Workspace View**: Toggle between `Student` and `Faculty` modes.
- **Active Student / Faculty**: Select the active user persona from the dropdown.

## 2. Views Overview
1. **Overview**: Executive dashboard summarizing overall accuracy %, total marks lost, assessment progression, and urgent recommendation alerts.
2. **Exam Manager**:
   - **Bulk CSV/Excel Import**: Upload spreadsheet files, preview the first 5 rows, validate against database constraints, review errors, and commit valid rows inside a transaction.
   - **Record Question Response**: Manually input a question result with mistake category, difficulty, confidence, and remarks.
   - **Create Exam & Topic**: Add new assessments or curriculum topics.
   - **Exam History**: Review configured tests.
3. **Subject Intelligence**: Deep-dive into curriculum subjects. Filter by subject to inspect syllabus coverage, marks lost by unit, and accuracy across question difficulties.
4. **Topic Weakness**: View the diagnostic classification of each topic (`Repeated Weakness`, `Weak`, `Monitoring`, `Strong`, `Improving`). Review data-backed explanations and add weak topics directly to your Revision Planner.
5. **Revision Planner**:
   - **Daily Tasks**: Manage scheduled tasks with priority indicators and complete them.
   - **Log Revision Session**: Record study sessions (duration in minutes, study type, notes).
   - **Study Goals**: Set milestone target scores.
   - **Revision Effectiveness**: Track before vs after assessment scores on revised topics.
6. **Performance Trends**: Review examination trajectories, difficulty breakdowns, metacognitive confidence calibration ("Blind Spot" detection), and class ranking.
7. **Faculty Analytics**: Available in Faculty mode. Inspect class-wide averages, grade distribution histograms, cohort hardest topics, and transparent at-risk student alerts.
8. **Reports & Data**: Download question responses and diagnostic summaries as CSV or Excel, and synchronize the Power BI analytical layer.
9. **Settings**: Run PostgreSQL connection diagnostics, calibrate weakness engine thresholds, or reset to fresh synthetic demonstration personas.
