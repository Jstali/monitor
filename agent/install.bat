@echo off
REM Employee Monitoring Agent - Windows Installer

echo ==========================================
echo   Employee Monitoring Agent Installer
echo ==========================================
echo.

REM Check Python installation
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo X Python is not installed!
    echo Please install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)
echo √ Python found
echo.

REM Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo √ Virtual environment created
) else (
    echo √ Virtual environment already exists
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo √ Virtual environment activated
echo.

REM Install dependencies
echo Installing required packages...
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo √ All packages installed
echo.

REM Get JWT token
if not exist ".env" (
    echo ==========================================
    echo   First Time Setup - Login Required
    echo ==========================================
    echo.
    python get_token.py
    echo.
)

REM Create desktop shortcut
echo Creating desktop shortcut...
set SCRIPT_DIR=%~dp0
set SHORTCUT=%USERPROFILE%\Desktop\StartMonitoring.bat

echo @echo off > "%SHORTCUT%"
echo cd /d "%SCRIPT_DIR%" >> "%SHORTCUT%"
echo call venv\Scripts\activate.bat >> "%SHORTCUT%"
echo python monitor_agent.py >> "%SHORTCUT%"
echo pause >> "%SHORTCUT%"

echo √ Desktop shortcut created: StartMonitoring.bat
echo.

echo ==========================================
echo   Installation Complete!
echo ==========================================
echo.
echo To start monitoring:
echo   1. Double-click 'StartMonitoring.bat' on your Desktop
echo   OR
echo   2. Run: start_monitoring.bat
echo.
echo The agent will open your dashboard automatically.
echo Click 'Start Monitoring' in the dashboard to begin.
echo.
pause
