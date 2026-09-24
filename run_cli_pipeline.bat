@echo off
title Smart Classroom CLI Pipeline
color 0E

set SCRIPT_DIR=%~dp0
set VENV_PYTHON=%SCRIPT_DIR%.venv\Scripts\python.exe

if not exist "%VENV_PYTHON%" (
    echo [ERROR] Virtual environment not found at %VENV_PYTHON%
    pause
    exit /b 1
)

cd /d "%SCRIPT_DIR%project"

echo =======================================================================
echo          RUNNING COMPLETE SMART CLASSROOM PIPELINE (CLI)
echo =======================================================================
echo.

"%VENV_PYTHON%" main.py

echo.
echo =======================================================================
echo  Pipeline execution completed! Check project/data/ for reports.
echo =======================================================================
pause
