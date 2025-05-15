@echo off
:: Batch script to run the Claude AI File Organizer Settings GUI

echo Claude AI File Organizer Settings
echo ===============================

:: Set working directory to project root
cd /d %~dp0\..

:: Check if virtual environment exists and activate it
if exist .venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
) else (
    echo Warning: Virtual environment not found at .venv\Scripts\activate.bat
    echo Attempting to run with system Python...
    
    :: Check if Python is installed
    python --version > nul 2>&1
    if errorlevel 1 (
        echo Error: Python is not installed or not in PATH
        pause
        exit /b 1
    )
)

:: Set Python path to include the project root
set PYTHONPATH=%CD%

:: Run the settings GUI
echo Starting settings GUI...
python src\gui\settings.py

:: Deactivate virtual environment if it was activated
if exist .venv\Scripts\activate.bat (
    call deactivate
)

:: Pause to view any error messages
pause
