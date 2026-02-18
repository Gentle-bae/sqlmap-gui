@echo off
cd /d "%~dp0"

::: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python and add to PATH.
    pause
    exit /b 1
)

::: Start GUI
start "" pythonw sqlmap-gui.py
