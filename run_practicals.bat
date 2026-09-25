@echo off
title Bootcamp on AI - Practicals and Assignments Suite
color 0E

set SCRIPT_DIR=%~dp0
set VENV_PYTHON=%SCRIPT_DIR%.venv\Scripts\python.exe

if exist "%VENV_PYTHON%" goto VENV_OK

echo [ERROR] Virtual environment not found at:
echo "%VENV_PYTHON%"
pause
exit /b 1

:VENV_OK

:MENU
cls
echo =======================================================================
echo              BOOTCAMP ON AI - PRACTICALS AND ASSIGNMENTS
echo =======================================================================
echo.
echo  --- PRACTICAL NOTEBOOKS ---
echo  [1] Day 1: Python Basics
echo  [2] Day 2: NumPy, Pandas and Matplotlib
echo  [3] Day 3: Machine Learning and NLP
echo  [4] Day 4: Deep Learning and Computer Vision
echo.
echo  --- ASSIGNMENT NOTEBOOKS ---
echo  [5] Assignment 1
echo  [6] Assignment 2
echo  [7] Assignment 3
echo  [8] Assignment 4
echo.
echo  --- INTERACTIVE TOOLS ---
echo  [J] Launch Jupyter Notebook Browser
echo  [Q] Exit
echo.
echo =======================================================================

set /p OPT="Enter your selection [1-8, J, Q]: "

if /i "%OPT%"=="1" goto DAY1
if /i "%OPT%"=="2" goto DAY2
if /i "%OPT%"=="3" goto DAY3
if /i "%OPT%"=="4" goto DAY4
if /i "%OPT%"=="5" goto ASSIGN1
if /i "%OPT%"=="6" goto ASSIGN2
if /i "%OPT%"=="7" goto ASSIGN3
if /i "%OPT%"=="8" goto ASSIGN4
if /i "%OPT%"=="J" goto JUPYTER
if /i "%OPT%"=="Q" goto EXIT

echo Invalid option. Please try again.
timeout /t 2 >nul
goto MENU

:DAY1
"%VENV_PYTHON%" "%SCRIPT_DIR%run_notebook.py" "%SCRIPT_DIR%BOOTCAMP ON AI_Practicals\Day_1.ipynb"
goto PAUSE_AND_LOOP

:DAY2
"%VENV_PYTHON%" "%SCRIPT_DIR%run_notebook.py" "%SCRIPT_DIR%BOOTCAMP ON AI_Practicals\Day_2.ipynb"
goto PAUSE_AND_LOOP

:DAY3
"%VENV_PYTHON%" "%SCRIPT_DIR%run_notebook.py" "%SCRIPT_DIR%BOOTCAMP ON AI_Practicals\Day_3.ipynb"
goto PAUSE_AND_LOOP

:DAY4
"%VENV_PYTHON%" "%SCRIPT_DIR%run_notebook.py" "%SCRIPT_DIR%BOOTCAMP ON AI_Practicals\Day_4.ipynb"
goto PAUSE_AND_LOOP

:ASSIGN1
"%VENV_PYTHON%" "%SCRIPT_DIR%run_notebook.py" "%SCRIPT_DIR%BOOTCAMP ON AI_Assignments\Assignment_1.ipynb"
goto PAUSE_AND_LOOP

:ASSIGN2
"%VENV_PYTHON%" "%SCRIPT_DIR%run_notebook.py" "%SCRIPT_DIR%BOOTCAMP ON AI_Assignments\Assignment_2.ipynb"
goto PAUSE_AND_LOOP

:ASSIGN3
"%VENV_PYTHON%" "%SCRIPT_DIR%run_notebook.py" "%SCRIPT_DIR%BOOTCAMP ON AI_Assignments\Assignment_3.ipynb"
goto PAUSE_AND_LOOP

:ASSIGN4
"%VENV_PYTHON%" "%SCRIPT_DIR%run_notebook.py" "%SCRIPT_DIR%BOOTCAMP ON AI_Assignments\Assignment_4.ipynb"
goto PAUSE_AND_LOOP

:JUPYTER
echo Launching Jupyter Notebook in browser...
where jupyter >nul 2>nul
if %errorlevel% equ 0 (
    start "" jupyter notebook "%SCRIPT_DIR%BOOTCAMP ON AI_Practicals"
) else (
    start "" "%VENV_PYTHON%" -m notebook "%SCRIPT_DIR%BOOTCAMP ON AI_Practicals"
)
goto PAUSE_AND_LOOP

:PAUSE_AND_LOOP
echo.
pause
goto MENU

:EXIT
exit /b 0
