@echo off
REM Start Monitoring Agent - Windows

cd /d %~dp0
call venv\Scripts\activate.bat
python monitor_agent.py
pause
