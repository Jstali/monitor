@echo off
TITLE Employee Monitoring Agent

echo ==========================================
echo    EMPLOYEE MONITORING AGENT SETUP
echo ==========================================

REM 1. Check for Python
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo ❌ Python is not installed!
    echo    Please install Python from https://www.python.org/downloads/
    echo    Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b
)

REM 2. Setup Virtual Environment
IF NOT EXIST "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM 3. Activate and Install Dependencies
call venv\Scripts\activate
echo ⬇️  Installing dependencies...
pip install -r requirements.txt >nul 2>&1

REM 4. Check Configuration
IF NOT EXIST ".env" (
    echo ⚠️  Configuration file not found!
    echo    Creating one for you...
    copy .env.example .env >nul
    
    echo.
    echo 📝 Please enter your credentials:
    set /p email="   Email: "
    set /p password="   Password: "
    
    echo API_URL=http://YOUR_SERVER_IP/api> .env
    echo DASHBOARD_URL=http://YOUR_SERVER_IP>> .env
    echo EMAIL=%email%>> .env
    echo PASSWORD=%password%>> .env
    
    echo.
    echo ✅ Configuration saved.
    echo ⚠️  IMPORTANT: Please ask your manager for the correct SERVER IP address
    echo    and update the API_URL and DASHBOARD_URL in the .env file.
    notepad .env
)

REM 5. Run Agent
echo 🚀 Starting Agent...
echo    (Keep this window open while working)
echo ==========================================
python monitor_agent.py
pause
