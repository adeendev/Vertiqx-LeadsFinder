@echo off
setlocal enabledelayedexpansion
title Lead Intelligence System

echo.
echo ============================================================
echo    Lead Intelligence System - Launcher
echo ============================================================
echo.
echo [1/6] Checking prerequisites...

where python >nul 2>nul
if errorlevel 1 (
    echo   [FAIL] Python not found. Install Python 3.9+ from https://python.org
    pause
    exit /b 1
)
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set "PY_VER=%%v"
for /f "tokens=1,2 delims=." %%a in ("!PY_VER!") do set "PY_MAJOR=%%a" & set "PY_MINOR=%%b"
if !PY_MAJOR! lss 3 (
    echo   [FAIL] Python 3.9+ required, found !PY_VER!.
    pause
    exit /b 1
)
if !PY_MAJOR! equ 3 if !PY_MINOR! lss 9 (
    echo   [FAIL] Python 3.9+ required, found !PY_VER!.
    pause
    exit /b 1
)
echo   [OK] Python !PY_VER!

where node >nul 2>nul
if errorlevel 1 (
    echo   [FAIL] Node.js not found. Install Node.js 18+ from https://nodejs.org
    pause
    exit /b 1
)
for /f "tokens=1" %%v in ('node --version') do set "NODE_VER=%%v"
echo   [OK] Node.js !NODE_VER!
echo.

:: STEP 2
echo [2/6] Setting up Python virtual environment...
pushd backend
if errorlevel 1 (
    echo   [FAIL] Cannot find 'backend' folder.
    pause
    exit /b 1
)

if not exist "venv" (
    echo   ~ Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo   [FAIL] Could not create virtual environment.
        pause
        exit /b 1
    )
) else (
    echo   [OK] Virtual environment exists.
)

call venv\Scripts\activate >nul
echo   [OK] Virtual environment activated.

:: STEP 3
echo.
echo [3/6] Installing Python dependencies...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo   [FAIL] pip install failed.
    pause
    exit /b 1
)
echo   [OK] Python packages installed.

echo.
echo   ~ Checking system compatibility...
python -c "import os,sys;f=os.path.join(sys.prefix,'Lib','site-packages','sitecustomize.py');open(f,'w').write('import os,sys\ntry:\n os.add_dll_directory(sys.base_prefix)\nexcept:\n pass')" >nul 2>nul
python -c "import greenlet._greenlet" >nul 2>nul
if errorlevel 1 (
    echo   ~ Fixing missing VC++ runtime DLL...
    python -c "import os,sys,shutil;d=sys.base_prefix;c=['C:\\Windows\\System32\\Microsoft-Edge-WebView\\msvcp140.dll','C:\\Windows\\System32\\msvcp140.dll'];t=os.path.join(d,'msvcp140.dll');[(shutil.copy2(s,t),None) for s in c if os.path.exists(s)]" >nul 2>nul
    python -c "import greenlet._greenlet" >nul 2>nul
    if errorlevel 1 (
        echo   [FAIL] Missing MSVCP140.dll - Install Visual C++ Redistributable:
        echo          https://aka.ms/vs/17/release/vc_redist.x64.exe
        pause
        exit /b 1
    )
)
echo   [OK] System compatible.

:: STEP 4
echo.
echo [4/6] Installing Playwright browser...
python -m playwright install chromium
if errorlevel 1 (
    echo   [FAIL] Playwright browser install failed.
    pause
    exit /b 1
)
echo   [OK] Chromium browser ready.

popd

:: STEP 5
echo.
echo [5/6] Setting up frontend...
pushd frontend
if errorlevel 1 (
    echo   [FAIL] Cannot find 'frontend' folder.
    pause
    exit /b 1
)

if not exist "node_modules" (
    echo   ~ Installing npm packages...
    call npm install
    if errorlevel 1 (
        echo   [FAIL] npm install failed.
        pause
        exit /b 1
    )
    echo   [OK] Frontend packages installed.
) else (
    echo   [OK] node_modules exists.
)

popd

:: STEP 6
echo.
echo [6/6] Launching services...
echo.

echo   ^>^> Starting Shared Browser Server (port 9222)...
start "LeadGen Browser" cmd /k "cd /d backend && venv\Scripts\activate && python browser_server.py"

echo   ^>^> Starting Backend API (port 8000)...
start "LeadGen Backend" cmd /k "cd /d backend && venv\Scripts\activate && uvicorn main:app --reload --port 8000"

echo   ^>^> Starting Frontend UI (port 3000)...
start "LeadGen Frontend" cmd /k "cd /d frontend && npm run dev"

echo.
echo ============================================================
echo    All services launched!
echo ============================================================
echo.
echo   Backend API:    http://localhost:8000/docs
echo   Frontend UI:    http://localhost:3000
echo.
echo   Close this window to stop all services.
echo   Each service runs in its own window.
echo ============================================================
echo.
pause
