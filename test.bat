@echo off
setlocal

echo ======================================================================
echo  GradeLens: Executing Automated Test Suite...
echo ======================================================================

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found. Please run setup.bat first.
    exit /b 1
)

".venv\Scripts\python.exe" -m pytest -v --tb=short

if %ERRORLEVEL% equ 0 (
    echo ======================================================================
    echo  [PASS] All automated unit and integration tests passed!
    echo ======================================================================
) else (
    echo ======================================================================
    echo  [FAIL] One or more tests failed. Review the pytest output above.
    echo ======================================================================
    exit /b %ERRORLEVEL%
)
