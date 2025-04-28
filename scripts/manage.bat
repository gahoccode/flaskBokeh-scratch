@echo off
REM Batch script for environment setup and project management

set VENV=.venv
set REQUIREMENTS=requirements.txt
set PYTHON=python

:MENU
echo.
echo ==== Portfolio Optimizer Project ====
echo 1. Activate virtual environment
echo 2. Install dependencies
echo 3. Run Flask app
echo 4. Lint with ruff
echo 5. Exit
set /p choice="Select an option: "
if "%choice%"=="1" goto ACTIVATE
if "%choice%"=="2" goto INSTALL
if "%choice%"=="3" goto RUN
if "%choice%"=="4" goto LINT
if "%choice%"=="5" exit

goto MENU

:ACTIVATE
call %VENV%\Scripts\activate
cmd /k

goto MENU

:INSTALL
call %VENV%\Scripts\activate
uv pip install -r %REQUIREMENTS%
goto MENU

:RUN
call %VENV%\Scripts\activate
%PYTHON% app.py
goto MENU

:LINT
call %VENV%\Scripts\activate
ruff app/
goto MENU
