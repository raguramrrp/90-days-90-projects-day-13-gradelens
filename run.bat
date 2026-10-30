@echo off
setlocal

echo ======================================================================
echo  GradeLens: Launching Academic Performance Platform...
echo ======================================================================

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found. Please run setup.bat first.
    pause
    exit /b 1
)

echo Starting Streamlit application on http://localhost:8501
echo Press Ctrl+C in this terminal window to stop the server.
echo.

".venv\Scripts\python.exe" -m streamlit run app/main.py --server.port 8501 --server.headless false

if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] GradeLens Streamlit application terminated unexpectedly.
    pause
)
