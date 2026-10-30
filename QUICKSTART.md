# GradeLens — Quick Start Guide

Get **GradeLens** running on Windows in under two minutes.

---

## Fast Track (Automatic)

1. Open PowerShell and navigate to the project directory:
   ```powershell
   cd "d:\90 days\90-days-90-projects-day-13-gradelens"
   ```
2. Run the setup script:
   ```powershell
   .\setup.bat
   ```
3. Start the application:
   ```powershell
   .\run.bat
   ```
4. GradeLens will open in your browser at `http://localhost:8501`.

---

## Manual Execution Commands

If you prefer executing each step manually:

```powershell
# 1. Activate Virtual Environment
.\.venv\Scripts\Activate.ps1

# 2. Re-seed Database (optional)
python -m src.data.seeder

# 3. Export Power BI Data (optional)
python powerbi/export_powerbi.py

# 4. Run Pytest Suite
pytest -v

# 5. Launch Streamlit
streamlit run app/main.py
```

---

## Exploring the Demonstration Personas

In the fixed left sidebar **Workspace Role**:
1. Select **Student** and switch between personas:
   - **Aarav Sharma (STU101)**: Navigate to **Topic Weakness** to view `Repeated Weakness` on Dynamic Programming and Window Functions. Check **Planning > Revision Planner** for scheduled review tasks.
   - **Diya Patel (STU102)**: Navigate to **Planning > Revision History** to view empirical score improvement (+50% score gain post-revision on Gradient Descent). Check **Planning > Study Goals** to monitor progress against target score percentages.
   - **Ananya Sen (STU104)**: Notice overall percentage (<50%) and multiple weak topics triggering academic intervention alerts.
2. Switch role to **Faculty**:
   - Open **Faculty Dashboard** to review cohort averages, pass rates, grade distribution histograms, and hardest curriculum topics.
   - Open **Student Performance** to inspect individual student trajectories and record formal faculty academic advisory notes.
   - Open **Class Analytics** to see the transparent Early Warning At-Risk Intervention Matrix.
3. Open **Data & Reports**:
   - Open **Data Import** to download pre-formatted CSV/Excel templates, validate files, and run atomic transaction imports.
   - Open **Reports & Exports** to download student response sheets as CSV/Excel or click **Export All Datasets for Power BI** to refresh `powerbi/data/`.
