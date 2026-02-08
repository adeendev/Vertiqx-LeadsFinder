@echo off
cd backend
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate
echo Installing dependencies...
pip install -r requirements.txt
echo Installing Playwright browsers...
playwright install
echo Starting Backend Server...
python main.py
pause
