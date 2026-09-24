@echo off
title SmartClass AI Server Launcher
color 0A

set SCRIPT_DIR=%~dp0
set VENV_PYTHON=%SCRIPT_DIR%..\.venv\Scripts\python.exe

if not exist "%VENV_PYTHON%" (
    echo [ERROR] Virtual environment not found at %VENV_PYTHON%
    pause
    exit /b 1
)

cd /d "%SCRIPT_DIR%"

echo =======================================================================
echo          SMART CLASSROOM & STUDENT ENGAGEMENT AI SUITE
echo =======================================================================
echo  Starting server and launching web browser...
echo.

start "" cmd /c "timeout /t 2 /nobreak >nul && start http://localhost:8000"

"%VENV_PYTHON%" -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload

pause
