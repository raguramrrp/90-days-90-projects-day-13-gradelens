@echo off
setlocal enabledelayedexpansion

echo ======================================================================
echo  GradeLens Setup — Day 13 of 90 Days 90 Projects Challenge
echo  Academic Performance Analytics & Weakness Detection Platform
echo ======================================================================

:: 1. Check for Python
set "PYTHON_CMD="
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
) else (
    where python >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        set "PYTHON_CMD=python"
    ) else (
        echo [ERROR] Python 3.10+ was not found on PATH or standard directory.
        echo Please install Python 3.12 from https://www.python.org/
        pause
        exit /b 1
    )
)

echo [1/6] Using Python: %PYTHON_CMD%

:: 2. Create or verify virtual environment
if not exist ".venv\Scripts\python.exe" (
    echo [2/6] Creating dedicated virtual environment in .venv...
    "%PYTHON_CMD%" -m venv .venv
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
) else (
    echo [2/6] Virtual environment already exists in .venv.
)

:: 3. Install dependencies
echo [3/6] Verifying and installing dependencies from requirements.txt...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo [WARNING] Pip install returned non-zero. Continuing with installed site packages...
)

:: 4. Check for .env file
if not exist ".env" (
    echo [4/6] Creating .env from .env.example...
    copy ".env.example" ".env" >nul
) else (
    echo [4/6] Existing .env file preserved.
)

:: 5. Initialize Database & Seed Synthetic Personas
echo [5/6] Initializing database schema and synthetic student personas...
".venv\Scripts\python.exe" -m src.data.seeder
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Database initialization failed.
    pause
    exit /b 1
)

:: 6. Export Power BI Datasets
echo [6/6] Generating curated CSV analytical datasets for Power BI Desktop...
".venv\Scripts\python.exe" powerbi/export_powerbi.py

echo ======================================================================
echo  Setup Complete! 
echo  - Launch Streamlit: run.bat
echo  - Run Test Suite:   test.bat
echo ======================================================================
pause
