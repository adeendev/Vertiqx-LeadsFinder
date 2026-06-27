@echo off
title Lead Intelligence Backend
echo ============================================
echo   Lead Intelligence System - Backend Only
echo ============================================
echo.

pushd backend

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate

echo Installing/updating Python dependencies...
pip install -r requirements.txt

echo Installing Playwright browser (Chromium)...
playwright install chromium

echo.
echo Starting Backend Server...
echo   API:      http://localhost:8000
echo   Docs:     http://localhost:8000/docs
echo.
python main.py

pause
