"""
GradeLens Power BI Data Layer & Analytical Exporter.
Exports 8 curated analytical tables from database views to CSV for Microsoft Power BI ingestion.
"""

from pathlib import Path
from typing import Dict, Any, List
import pandas as pd
from src.database.repository import Repository, repo

BASE_DIR = Path(__file__).resolve().parent.parent.parent
POWERBI_DATA_DIR = BASE_DIR / "powerbi" / "data"

POWERBI_VIEW_EXPORTS = [
    ("vw_student_performance", "student_performance.csv"),
    ("vw_subject_performance", "subject_performance.csv"),
    ("vw_topic_performance", "topic_performance.csv"),
    ("vw_question_level_analysis", "question_level_analysis.csv"),
    ("vw_exam_comparison", "exam_comparison.csv"),
    ("vw_revision_effectiveness", "revision_effectiveness.csv"),
    ("vw_faculty_class_analytics", "faculty_class_analytics.csv"),
    ("vw_recommendation_summary", "recommendation_summary.csv"),
]


def export_powerbi_datasets(repository: Repository = repo, output_dir: Path = POWERBI_DATA_DIR) -> Dict[str, Any]:
    """
    Executes SELECT against each analytical view and saves clean CSVs for Power BI.
    Returns status report with row counts and file sizes.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    summary: Dict[str, Any] = {}

    for view_name, csv_filename in POWERBI_VIEW_EXPORTS:
        target_path = output_dir / csv_filename
        try:
            df = repository.query_df(f"SELECT * FROM {view_name};")
            df.to_csv(target_path, index=False)
            summary[csv_filename] = {
                "status": "Success",
                "rows": len(df),
                "columns": len(df.columns),
                "path": str(target_path),
                "size_kb": round(target_path.stat().st_size / 1024, 2)
            }
        except Exception as exc:
            summary[csv_filename] = {
                "status": "Failed",
                "error": str(exc),
                "path": str(target_path)
            }

    return summary


if __name__ == "__main__":
    res = export_powerbi_datasets()
    print("Power BI Export Result:")
    for k, v in res.items():
        print(f" - {k}: {v.get('status')} ({v.get('rows', 0)} rows)")
