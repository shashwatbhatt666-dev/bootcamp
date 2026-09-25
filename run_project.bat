@echo off
title Smart Classroom and Student Engagement AI Suite - Project Runner
color 0B

set SCRIPT_DIR=%~dp0
set VENV_PYTHON=%SCRIPT_DIR%.venv\Scripts\python.exe

if exist "%VENV_PYTHON%" goto VENV_OK

echo =======================================================================
echo  [ERROR] Python Virtual Environment was not found!
echo  Expected location: "%VENV_PYTHON%"
echo =======================================================================
echo  Please ensure .venv is installed in the workspace root.
echo  To create it, run:
echo     python -m venv .venv
echo     .\.venv\Scripts\pip install -r project\requirements.txt
echo =======================================================================
pause
exit /b 1

:VENV_OK

:MENU
cls
echo =======================================================================
echo          SMART CLASSROOM AND STUDENT ENGAGEMENT AI SUITE
echo               (Full-Stack Enterprise and Kaggle Vision)
echo =======================================================================
echo.
echo  Virtual Environment: .venv [OK]
echo  Project Directory  : %SCRIPT_DIR%project
echo.
echo  Select an option to run:
echo.
echo    [1] Start Web Dashboard (Full UI with Vision, ML and SQLite) [DEFAULT]
echo    [2] Run Complete CLI Machine Learning and Analytics Pipeline
echo    [3] Open Interactive REST API Documentation (Swagger /docs)
echo    [Q] Exit
echo.
echo =======================================================================
set /p CHOICE="Enter choice [1, 2, 3 or Q, default is 1]: "

if /i "%CHOICE%"=="Q" goto QUIT
if "%CHOICE%"=="2" goto RUN_CLI
if "%CHOICE%"=="3" goto RUN_DOCS
goto RUN_WEB

:RUN_WEB
cls
echo =======================================================================
echo       LAUNCHING SMART CLASSROOM WEB DASHBOARD (PORT 8000)
echo =======================================================================
echo.
echo [1/3] Loading PyTorch, YOLOv8 Vision and Kaggle Classifiers...
echo [2/3] Initializing SQLite Student Database...
echo [3/3] Background health check active.
echo.
echo - Web Dashboard will open automatically at:
echo      http://127.0.0.1:8000  (or http://localhost:8000)
echo.
echo - Press Ctrl+C in this console window to stop the server anytime.
echo =======================================================================
echo.

cd /d "%SCRIPT_DIR%project"

:: Launch browser in background once the server responds HTTP 200
start "" /B "%VENV_PYTHON%" launch_browser.py "http://127.0.0.1:8000"

:: Start Uvicorn ASGI server
"%VENV_PYTHON%" -m uvicorn server:app --host 0.0.0.0 --port 8000
goto PAUSE_AND_END

:RUN_CLI
cls
echo =======================================================================
echo            RUNNING COMPLETE MACHINE LEARNING PIPELINE (CLI)
echo =======================================================================
echo.
cd /d "%SCRIPT_DIR%project"
"%VENV_PYTHON%" main.py
echo.
echo =======================================================================
echo  Pipeline execution completed! Check project/data/ for reports.
echo =======================================================================
goto PAUSE_AND_END

:RUN_DOCS
cls
echo =======================================================================
echo          OPENING INTERACTIVE REST API DOCUMENTATION
echo =======================================================================
echo.
cd /d "%SCRIPT_DIR%project"
start "" /B "%VENV_PYTHON%" launch_browser.py "http://127.0.0.1:8000/docs"
"%VENV_PYTHON%" -m uvicorn server:app --host 0.0.0.0 --port 8000
goto PAUSE_AND_END

:PAUSE_AND_END
echo.
pause
goto MENU

:QUIT
exit /b 0
