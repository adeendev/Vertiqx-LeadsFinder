@echo off
echo Starting Lead Intelligence System...

echo.
echo Checking backend Python environment and dependencies...
if not exist "backend\venv" (
    echo Creating Python virtual environment in backend\venv ...
    pushd backend
    python -m venv venv
    if errorlevel 1 (
        echo Failed to create virtual environment. Ensure Python is installed and on PATH.
        pause
        exit /b 1
    )
    call venv\Scripts\activate
    echo Installing Python dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Failed to install Python dependencies.
        pause
        exit /b 1
    )
    popd
) else (
    echo Python virtual environment already exists.
)

echo.
echo Checking frontend Node.js dependencies...
if not exist "frontend\node_modules" (
    echo Installing frontend dependencies with npm install...
    pushd frontend
    npm install
    if errorlevel 1 (
        echo Failed to install frontend dependencies. Ensure Node.js and npm are installed.
        pause
        exit /b 1
    )
    popd
) else (
    echo Frontend dependencies already installed.
)

echo.
echo Starting Shared Browser Server...
start "LeadGen Browser Server" cmd /k "cd backend && venv\Scripts\activate && python browser_server.py"

echo Starting Python Backend (Port 8000)...
start "LeadGen Backend" cmd /k "cd backend && venv\Scripts\activate && uvicorn main:app --reload --port 8000"

echo Starting Lead Intelligence UI (Port 3000)...
start "LeadGen Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo System is starting up!
echo ---------------------------------------------
echo Backend API:    http://localhost:8000/docs
echo Frontend UI:    http://localhost:3000
echo ---------------------------------------------
pause
