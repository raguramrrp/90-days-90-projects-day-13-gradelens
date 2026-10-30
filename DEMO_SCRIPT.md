# GradeLens — 90-Second Demonstration Script

Use this structured walkthrough to showcase **GradeLens** in interviews, project evaluations, or video demonstrations.

---

## 🎬 Act 1: The Problem & The Student Perspective (0:00 – 0:30)

1. **Launch GradeLens**: Start via `.\run.bat`. Notice the clean, cool-neutral typography and muted blue interface.
2. **Select Student Persona `Aarav Sharma (STU101)`**:
   - Point out the **Overview** dashboard: Overall Accuracy is `61.4%`, 4 assessments, and `67.5` total marks lost.
   - Highlight the alert banner: *"Action Required: Urgent Revision on Dynamic Programming"*.
3. **Navigate to `Topic Weakness`**:
   - **Show the Differentiator**: Emphasize that GradeLens doesn't just show marks—it diagnoses *why* marks were lost.
   - Point out `Dynamic Programming`: Classified as **Repeated Weakness** because performance was $<60\%$ across 3 assessments, driven by 4 *Calculation errors*.
   - Point out the pie chart: 48% of total marks lost were due to *Calculation errors*, not conceptual absence.
   - Click **"Add to Planner"** right from the diagnosis card.

---

## 🎬 Act 2: Revision Planning & Effectiveness Tracking (0:30 – 1:00)

1. **Navigate to `Revision Planner`**:
   - Show the newly scheduled revision task under **Daily Tasks** and click **"Done"**.
2. **Switch to Persona `Diya Patel (STU102)`**:
   - Navigate to the **Revision Effectiveness** tab.
   - **Show the Before vs. After Correlation**:
     - *Pre-Revision Score*: 40.0% on Gradient Descent.
     - *Revision Logged*: 2 sessions (105 minutes) of formula derivations and flashcards.
     - *Post-Revision Score*: 90.0% (+50.0% observed gain!).
   - Highlight the transparent scientific disclaimer: *"Observed comparison; individual results may depend on assessment difficulty."*

---

## 🎬 Act 3: Bulk Import & Faculty Intelligence (1:00 – 1:30)

1. **Navigate to `Exam Manager`**:
   - Show the **Bulk CSV/Excel Import** tab.
   - Download the sample template or upload a file.
   - Demonstrate the validation engine: catches negative marks, marks exceeding maximum, invalid difficulty levels, and duplicates before database insertion.
2. **Switch Role to `Faculty`**:
   - Navigate to **Faculty Analytics**.
   - Show the Class Average (66.5%), cohort pass rate, and the **At-Risk Students Table**:
     - *Ananya Sen (STU104)* is flagged transparently because overall score is $<50\%$.
   - Show the **Cohort-Wide Hardest Topics** bar chart to see what curriculum areas require faculty re-teaching.
3. **Navigate to `Reports & Data`**:
   - Click **"Export All Datasets for Power BI"** to demonstrate the automated 8-dataset pipeline into `powerbi/data/`.
   - Conclude with how GradeLens bridges daily student revision and institutional faculty decision-making.
