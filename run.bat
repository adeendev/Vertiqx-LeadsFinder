@echo off
echo Starting Vertiqx Lead Intelligence System...

:: Start Shared Browser Server
echo Starting Shared Browser Server...
start "LeadGen Browser Server" cmd /k "cd backend && venv\Scripts\activate && python browser_server.py"

:: Start Backend Server
echo Starting Python Backend (Port 8000)...
start "LeadGen Backend" cmd /k "cd backend && venv\Scripts\activate && uvicorn main:app --reload --port 8000"

:: Start Frontend UI
echo Starting Lead Intelligence UI (Port 3000)...
start "LeadGen Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo System is starting up!
echo ---------------------------------------------
echo Backend API:    http://localhost:8000/docs
echo Frontend UI:    http://localhost:3000
echo ---------------------------------------------
pause
