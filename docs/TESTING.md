# GradeLens: Testing & Quality Assurance Documentation

## 1. Test Suite Summary
The automated test suite is built using **pytest** and executes against an isolated temporary test database fixture.

- **Total Test Cases**: 31
- **Passed**: 31 (100%)
- **Failed**: 0
- **Execution Time**: ~1.8 seconds on Windows 11

## 2. Test Modules Breakdown

| Test File | Scope | Cases | Status |
|---|---|---|---|
| `test_database.py` | Schema DDL, 14 tables, 8 views, status check, constraints, rollback | 6 | PASS |
| `test_academic_calcs.py` | Safe percentage, zero division, subject metrics, difficulty breakdown, dense ranking ties, exam trends, mistakes, confidence calibration | 8 | PASS |
| `test_weakness_engine.py` | Insufficient data, strong topic, repeated weakness across assessments, improving topic, seeded student diagnostics | 5 | PASS |
| `test_recommendations.py` | Recommendation generation, deduplication, priority assignment, status transitions | 3 | PASS |
| `test_revision_planner.py` | Revision tasks lifecycle, study goals, before/after score impact | 3 | PASS |
| `test_imports_exports.py` | Valid CSV/Excel data, invalid row error detection, atomic transactions, Power BI 8-view CSV exports | 4 | PASS |
| `test_faculty_analytics.py` | Class aggregations, transparent at-risk student rules | 2 | PASS |

## 3. Running the Tests
To run all tests:
```powershell
.\test.bat
```
Or directly using pytest:
```powershell
.\.venv\Scripts\python.exe -m pytest -v --tb=short
```
