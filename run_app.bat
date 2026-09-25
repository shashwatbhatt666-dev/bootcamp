@echo off
title Smart Classroom and Student Engagement AI Suite
color 0B

set SCRIPT_DIR=%~dp0
set VENV_PYTHON=%SCRIPT_DIR%.venv\Scripts\python.exe

if exist "%VENV_PYTHON%" goto VENV_OK

echo [ERROR] Virtual environment not found at:
echo "%VENV_PYTHON%"
echo Please make sure .venv exists or run: python -m venv .venv
pause
exit /b 1

:VENV_OK

echo =======================================================================
echo          SMART CLASSROOM AND STUDENT ENGAGEMENT AI SUITE
echo               (Full-Stack Enterprise and Kaggle Vision)
echo =======================================================================
echo.
echo [1/3] Virtual environment detected: %VENV_PYTHON%
echo [2/3] Initializing FastAPI server, PyTorch, YOLO, and Kaggle AI models...

cd /d "%SCRIPT_DIR%project"

:: Launch browser in background once the server actually starts responding
start "" /B "%VENV_PYTHON%" launch_browser.py "http://127.0.0.1:8000"

echo [3/3] Background health check active. Browser will open at:
echo       http://127.0.0.1:8000 (as soon as AI models are loaded)
echo.
echo =======================================================================
echo  Server running on: http://127.0.0.1:8000 (and http://localhost:8000)
echo  Press Ctrl+C in this console window to stop the server anytime.
echo =======================================================================
echo.

"%VENV_PYTHON%" -m uvicorn server:app --host 0.0.0.0 --port 8000

pause
