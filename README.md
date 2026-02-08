# Lead Intelligence System

A production-ready, safe, intelligent lead-generation system for identifying businesses that need website redesign services.

## Architecture

- **Backend**: Python (FastAPI) + Playwright + SQLModel (SQLite/Postgres)
- **Frontend**: Next.js (App Router) + Tailwind CSS
- **Scraper**: Playwright (Headful/Headless) with human-like delays
- **Analysis**: Custom website analyzer with builder detection and multi-dimension scoring

## Setup

### Prerequisites

- Python 3.9+
- Node.js 18+

### Backend Setup

1. Navigate to `backend` folder:
   ```bash
   cd backend
   ```
2. Create virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   # source venv/bin/activate # Mac/Linux
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Install Playwright browsers:
   ```bash
   playwright install
   ```
5. Run the server:
   ```bash
   python main.py
   ```
   Server will run at `http://localhost:8000`.

### Frontend Setup

1. Navigate to `frontend` folder:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
   Dashboard will run at `http://localhost:3000`.

## Usage

1. Open the dashboard.
2. Enter a **Keyword** (e.g., "Landscaping") and **Location** (e.g., "Austin, TX").
3. Click **Start Scan**.
4. The backend will launch a browser (headless by default), search Google Maps, and analyze results.
5. Results will appear in the table as they are processed (auto-refresh every 5s).
6. Filter by Tier to find "Gold" leads (Bad site + AI builder + No email).

## Safety Features

- Random delays (2-5s) between actions.
- Limit to top results per scan (configurable in code).
- User-Agent rotation (basic implementation included).
