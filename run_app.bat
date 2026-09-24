@echo off
title Smart Classroom & Student Engagement AI Suite
color 0B

echo =======================================================================
echo          SMART CLASSROOM & STUDENT ENGAGEMENT AI SUITE
echo               (Full-Stack Enterprise & Kaggle Vision)
echo =======================================================================
echo.

set SCRIPT_DIR=%~dp0
set VENV_PYTHON=%SCRIPT_DIR%.venv\Scripts\python.exe

if not exist "%VENV_PYTHON%" (
    echo [ERROR] Virtual environment not found at:
    echo "%VENV_PYTHON%"
    echo Please make sure .venv exists or run: python -m venv .venv
    pause
    exit /b 1
)

echo [1/3] Virtual environment detected: %VENV_PYTHON%
echo [2/3] Starting FastAPI Web Server and loading Kaggle AI Models...

cd /d "%SCRIPT_DIR%project"

:: Launch browser in background after 2 seconds
start "" cmd /c "timeout /t 2 /nobreak >nul && start http://localhost:8000"

echo [3/3] Opening web browser at http://localhost:8000 ...
echo.
echo =======================================================================
echo  Server is running on: http://localhost:8000
echo  Press Ctrl+C in this console window to stop the server anytime.
echo =======================================================================
echo.

"%VENV_PYTHON%" -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload

pause
