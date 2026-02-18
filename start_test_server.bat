@echo off
title SQL Injection Test Server
cd /d "%~dp0"
color 0a

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python and add to PATH.
    pause
    exit /b 1
)

:: Check Flask
python -c "import flask" 2>nul
if errorlevel 1 (
    echo [INFO] Installing Flask...
    pip install flask
)

echo ============================================
echo   SQL Injection Test Server
echo   Access: http://127.0.0.1:5000
echo   Press Ctrl+C to stop
echo ============================================
echo.

python test_sqli_server.py
pause
