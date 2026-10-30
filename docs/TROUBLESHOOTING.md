# GradeLens: Troubleshooting & Common Issues Guide

## 1. Database Connection Diagnostics

### Issue: "PostgreSQL Unreachable / localhost:5432 - no response"
- **Cause**: The PostgreSQL Windows service is stopped or not installed.
- **Solution 1 (Start Service)**:
  Open an Administrator Command Prompt or PowerShell and start the service:
  ```cmd
  net start postgresql-x64-18
  ```
- **Solution 2 (Switch to Local Engine)**:
  GradeLens includes zero-configuration SQLite support. Open `.env` and set:
  ```env
  DATABASE_TYPE=sqlite
  ```
  Restart the application (`run.bat`).

---

## 2. Python Environment & Dependency Issues

### Issue: "'streamlit' is not recognized as an internal or external command"
- **Cause**: Virtual environment not activated or dependencies not installed.
- **Solution**:
  Run `setup.bat` to rebuild the virtual environment, or activate it manually:
  ```powershell
  .\.venv\Scripts\Activate.ps1
  pip install -r requirements.txt
  ```

---

## 3. CSV / Excel Import Issues

### Issue: "Missing required columns in file"
- **Cause**: Uploaded file header does not match GradeLens expected fields.
- **Solution**:
  Click **Download Sample CSV Template** in the **Exam Manager** tab to obtain the expected schema:
  - `student_code`
  - `subject_code`
  - `topic_name`
  - `exam_name`
  - `maximum_marks`
  - `marks_obtained`

---

## 4. Power BI Desktop Refresh

### Issue: "Power BI visual shows outdated data"
- **Cause**: Power BI imported static CSV files that have not been re-exported after new marks were entered.
- **Solution**:
  Navigate to **Reports & Data** in Streamlit and click **Export All Datasets for Power BI** (or run `python powerbi/export_powerbi.py`), then click **Refresh** in Power BI Desktop.
