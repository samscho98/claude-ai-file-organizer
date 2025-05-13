@echo off
:: Batch script to run the Claude AI File Organizer

echo Claude AI File Organizer
echo =======================

:: Set working directory to project root
cd /d %~dp0\..
set PYTHONPATH=%CD%

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

:: Run the main script
echo Running organizer...
python src\main.py %*

:: Check if API endpoint extraction is enabled
echo.
echo Checking API endpoint extraction...
python scripts\check_point_extraction.py

echo.
echo Done!

:: Deactivate virtual environment if it was activated
if exist .venv\Scripts\activate.bat (
    call deactivate
)

echo.
echo Press any key to close this window...
pause > nul