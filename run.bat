@echo off
REM TalentBridge Scraper Runner (Windows)
REM Usage: run.bat

echo 🚀 Starting TalentBridge Lead Scraper...
echo 📅 Timestamp: %DATE% %TIME%
echo.

REM Ensure we're in the project root
cd /d "%~dp0"

REM Check Python version
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: python not found. Please install Python 3.10+
    pause
    exit /b 1
)

REM Install dependencies if venv doesn't exist
if not exist "venv\" (
    echo 📦 Installing dependencies...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

REM Run the scraper
echo 🔍 Fetching leads...
python main.py

REM Capture exit code
set EXIT_CODE=%ERRORLEVEL%

echo.
if %EXIT_CODE% equ 0 (
    echo ✅ Scraper completed successfully.
    echo 📊 Check run.log for detailed stats.
    echo 📈 Open your Google Sheet to view new leads.
) else (
    echo ❌ Scraper failed with exit code %EXIT_CODE%
    echo 🔍 Check run.log for error details.
)

REM Deactivate venv
deactivate

pause
exit /b %EXIT_CODE%