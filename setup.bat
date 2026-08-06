@echo off
echo =============================================
echo  Online Shopping System - Local Setup
echo =============================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python found
python --version

:: Create virtual environment if not exists
if not exist "venv" (
    echo.
    echo [INFO] Creating virtual environment...
    python -m venv venv
    echo [OK] Virtual environment created
) else (
    echo [OK] Virtual environment already exists
)

:: Activate venv and install dependencies
echo.
echo [INFO] Installing dependencies...
call venv\Scripts\activate
pip install -r requirements.txt --quiet
echo [OK] Dependencies installed

:: Check if .env exists
if not exist ".env" (
    echo.
    echo [WARNING] .env file not found. Creating from .env.example...
    copy .env.example .env
    echo [DONE] Created .env - please update DB_PASSWORD if needed
) else (
    echo [OK] .env file exists
)

echo.
echo =============================================
echo  Setup complete!
echo.
echo  Next steps:
echo  1. Make sure MySQL is running
echo  2. Run: python init_db.py  (creates database)
echo  3. Run: python seed_data.py (adds sample data)
echo  4. Run: python run.py  (starts the server)
echo.
echo  OR just run start.bat to do steps 2-4 automatically
echo =============================================
pause
