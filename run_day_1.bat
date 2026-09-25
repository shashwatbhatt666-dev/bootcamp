@echo off
title Bootcamp on AI - Day 1 Practical Runner
color 0B

set SCRIPT_DIR=%~dp0
set VENV_PYTHON=%SCRIPT_DIR%.venv\Scripts\python.exe

if not exist "%VENV_PYTHON%" (
    echo [ERROR] Virtual environment not found at:
    echo "%VENV_PYTHON%"
    echo Please ensure .venv is configured or run: python -m venv .venv
    pause
    exit /b 1
)

set NOTEBOOK_PATH=%SCRIPT_DIR%BOOTCAMP ON AI_Practicals\Day_1.ipynb
if not "%~1"=="" (
    set NOTEBOOK_PATH=%~1
)

echo =======================================================================
echo               BOOTCAMP ON AI - DAY 1 PRACTICAL RUNNER
echo =======================================================================
echo.
echo Target Notebook: "%NOTEBOOK_PATH%"
echo.
echo Choose execution mode:
echo   [1] Run directly in Console (All cells & interactive plots) [Default]
echo   [2] Open in Jupyter Notebook (Interactive Web Browser)
echo.

set /p CHOICE="Select [1 or 2, default: 1]: "

if "%CHOICE%"=="2" goto LAUNCH_JUPYTER
goto RUN_IN_CONSOLE

:RUN_IN_CONSOLE
echo.
echo -----------------------------------------------------------------------
echo  Executing Day 1 notebook cells with Python (.venv)...
echo -----------------------------------------------------------------------
echo.
"%VENV_PYTHON%" "%SCRIPT_DIR%run_notebook.py" "%NOTEBOOK_PATH%"
goto FINISH

:LAUNCH_JUPYTER
echo.
echo -----------------------------------------------------------------------
echo  Opening Day 1 notebook in Jupyter...
echo -----------------------------------------------------------------------
where jupyter >nul 2>nul
if %errorlevel% equ 0 (
    jupyter notebook "%NOTEBOOK_PATH%"
) else (
    "%VENV_PYTHON%" -m notebook "%NOTEBOOK_PATH%"
)
goto FINISH

:FINISH
echo.
echo =======================================================================
echo  Execution finished.
echo =======================================================================
pause
