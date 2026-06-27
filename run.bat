@echo off
setlocal enabledelayedexpansion
title Lead Intelligence System
echo ============================================
echo    Lead Intelligence System - Launcher
echo ============================================
echo.

:: ─── Backend Setup ──────────────────────────────────────
echo [1/4] Checking Python virtual environment...
pushd backend

if not exist "venv" (
    echo       Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo       FAILED: Ensure Python 3.9+ is installed and on PATH.
        pause
        exit /b 1
    )
)

call venv\Scripts\activate

echo       Installing/updating Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo       FAILED: pip install failed.
    pause
    exit /b 1
)

echo       Installing Playwright browser (Chromium)...
playwright install chromium
if errorlevel 1 (
    echo       FAILED: Playwright browser install failed.
    pause
    exit /b 1
)

popd

:: ─── Frontend Setup ─────────────────────────────────────
echo [2/4] Checking frontend dependencies...
pushd frontend

if not exist "node_modules" (
    echo       Installing npm packages...
    npm install
    if errorlevel 1 (
        echo       FAILED: npm install failed. Ensure Node.js 18+ is installed.
        pause
        exit /b 1
    )
) else (
    echo       node_modules found, skipping install.
)

popd

:: ─── Launch Services ────────────────────────────────────
echo [3/4] Launching services...

echo       Starting Shared Browser Server (port 9222)...
start "LeadGen Browser Server" cmd /k "cd backend && venv\Scripts\activate && python browser_server.py"

echo       Starting Backend API (port 8000)...
start "LeadGen Backend" cmd /k "cd backend && venv\Scripts\activate && uvicorn main:app --reload --port 8000"

echo       Starting Frontend UI (port 3000)...
start "LeadGen Frontend" cmd /k "cd frontend && npm run dev"

:: ─── Done ───────────────────────────────────────────────
echo [4/4] All services launched!
echo.
echo ============================================
echo   Backend API:    http://localhost:8000/docs
echo   Frontend UI:    http://localhost:3000
echo ============================================
echo.
echo   Close this window to stop all services.
echo   (Close each service window individually)
echo ============================================
pause
