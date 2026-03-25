@echo off
echo ========================================================
echo 🎮  AAA Game Studio Multi-Agent Orchestrator
echo ========================================================
echo.
echo Setting up Python Environment for 14-Agent System...

:: Check if user has python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed. Please install Python 3.10+ from python.org
    pause
    exit
)

echo.
echo [1/3] Creating virtual environment...
if not exist "venv" (
    python -m venv venv
)

echo [2/3] Activating virtual environment and installing dependencies...
call venv\Scripts\activate
pip install --default-timeout=150 -r requirements.txt

echo.
echo [3/3] Starting Orchestrator...
echo Ensure you have added your GEMINI_API_KEY in the .env file!
echo.
python main.py

echo.
pause
