@echo off
echo 🧠 IntelliDocs AI - Starting...
echo ================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Check if app.py exists
if not exist "app.py" (
    echo ❌ app.py not found in current directory
    echo Make sure you're in the intellidocs-ai folder
    pause
    exit /b 1
)

REM Try to run the quick start script
echo ✅ Running quick start check...
python quick_start.py

pause