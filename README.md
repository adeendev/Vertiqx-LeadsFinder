
<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.9+"/>
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/Next.js-14-000000?style=for-the-badge&logo=nextdotjs&logoColor=white" alt="Next.js 14"/>
  <img src="https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript"/>
  <img src="https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white" alt="Tailwind CSS"/>
  <img src="https://img.shields.io/badge/Playwright-2EAD33?style=for-the-badge&logo=playwright&logoColor=white" alt="Playwright"/>
  <img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite"/>
</p>

<br>

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:667eea,100:764ba2&height=200&section=header&text=Lead%20Intelligence%20System&fontSize=48&fontColor=ffffff&animation=fadeIn&fontAlignY=36" width="100%"/>
</p>

<p align="center">
  <b>🚀 Discover. Analyze. Score. Convert.</b><br>
  <i>A production-ready lead-generation engine that finds businesses with outdated websites, analyzes their digital presence, scores them by sales potential, and automates outreach — all from a beautiful web dashboard.</i>
</p>

<br>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-configuration">Configuration</a> •
  <a href="#-usage">Usage</a> •
  <a href="#-api">API</a> •
  <a href="#-deployment">Deployment</a>
</p>

<br>

---

## ✨ Features

<table>
  <tr>
    <td width="50%">
      <h3>🔍 Google Maps Discovery</h3>
      Searches by keyword + location, extracts name, website, phone, address, rating, reviews, and social links. CAPTCHA-aware with manual solve pause.
    </td>
    <td width="50%">
      <h3>🌐 Website Analysis</h3>
      Visits each site via Playwright, detects <b>20+ issues</b>: no SSL, slow loading, missing CTA, thin content, no schema, missing OG tags, no favicon, and more.
    </td>
  </tr>
  <tr>
    <td width="50%">
      <h3>🏗️ Builder Detection</h3>
      Identifies WordPress, Shopify, Wix, Squarespace, Webflow, GoDaddy, Hostinger, React, Next.js. AI-built sites (GoDaddy, Hostinger, Wix ADI) get <b>priority boost</b>.
    </td>
    <td width="50%">
      <h3>📊 Smart Scoring & Tiers</h3>
      <b>Tier-1 Gold</b> (≥80) — bad site + AI builder + no email<br>
      <b>Tier-1</b> (≥60) — bad site + weak builder<br>
      <b>Tier-2</b> (≥40) — medium quality<br>
      <b>Ignore</b> (&lt;40) — strong existing sites
    </td>
  </tr>
  <tr>
    <td width="50%">
      <h3>📧 Email Intelligence</h3>
      Extracts emails via mailto, footer, contact pages, and regex. Ranks quality: <code>no email &gt; personal &gt; generic &gt; named</code>. Auto-ignores your own domain.
    </td>
    <td width="50%">
      <h3>✉️ Email Outreach</h3>
      SMTP-based with <b>smart auto-template selection</b> based on lead status. HTML templates with placeholders, rate-limited batch sending.
    </td>
  </tr>
  <tr>
    <td width="50%">
      <h3>🔄 Data Enrichment</h3>
      Fallback Google/DuckDuckGo searches + Facebook page deep-dive to extract missing websites and emails.
    </td>
    <td width="50%">
      <h3>📈 Live Dashboard</h3>
      Real-time activity log, sortable/filterable lead table, stats cards, CSV export, project management, and settings page.
    </td>
  </tr>
</table>

---

## 🏗️ Architecture

<pre>

┌─────────────────────────────────────────────────────────────────────────┐
│                          Frontend (Next.js 14)                         │
│                           Port 3000 │ Static SPA                       │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Dashboard  │  Projects  │  Settings  │  CSV Export  │  Logs    │   │
│  └────────────────────────────────┬────────────────────────────────┘   │
│                                   │ axios                              │
└───────────────────────────────────┼─────────────────────────────────────┘
                                    │
┌───────────────────────────────────┼─────────────────────────────────────┐
│                        Backend (FastAPI)                               │
│                           Port 8000                                    │
│  ┌────────────────────────────────┴────────────────────────────────┐   │
│  │  main.py — API Routes                                          │   │
│  │  /api/scan  /api/leads  /api/settings  /api/send_email          │   │
│  │  /api/analyze  /api/enrich  /api/apify  /api/email_all          │   │
│  └────────────────────────────────┬────────────────────────────────┘   │
│                                   │ subprocess.Popen                    │
│  ┌────────────────────────────────┴────────────────────────────────┐   │
│  │  worker.py — Background Workers                                │   │
│  │  [search]  →  Google Maps scraping                              │   │
│  │  [analyze] →  Website analysis via Playwright                   │   │
│  │  [enrich]  →  Data fallback + Facebook deep-dive                │   │
│  └────────────────────────────────┬────────────────────────────────┘   │
│                                   │                                     │
│  ┌────────────────────────────────┴────────────────────────────────┐   │
│  │  Services Layer                                                 │   │
│  │  scraper.py  analyzer.py  scoring.py  builder_detector.py       │   │
│  │  email_extractor.py  emailer.py  apify_scraper.py               │   │
│  │  browser_manager.py  status.py  email_template.py               │   │
│  └────────────────────────────────┬────────────────────────────────┘   │
│                                   │                                     │
│  ┌────────────────────────────────┴────────────────────────────────┐   │
│  │  Database (SQLite / PostgreSQL via SQLModel)                    │   │
│  │  tables: Lead  Project  SystemLog  Settings                    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘

</pre>

<table>
  <tr>
    <th>Layer</th>
    <th>Technology</th>
  </tr>
  <tr><td><b>Backend Framework</b></td><td>Python 3.9+ / FastAPI + Uvicorn</td></tr>
  <tr><td><b>Web Scraping</b></td><td>Playwright + playwright-stealth</td></tr>
  <tr><td><b>Database ORM</b></td><td>SQLModel (by FastAPI creator)</td></tr>
  <tr><td><b>Database</b></td><td>SQLite (dev) / PostgreSQL (production)</td></tr>
  <tr><td><b>Frontend</b></td><td>Next.js 14 (App Router) + TypeScript</td></tr>
  <tr><td><b>Styling</b></td><td>Tailwind CSS 3 + lucide-react</td></tr>
  <tr><td><b>HTTP Client</b></td><td>axios</td></tr>
  <tr><td><b>Email</b></td><td>smtplib + custom HTML templates</td></tr>
  <tr><td><b>HTML Parsing</b></td><td>BeautifulSoup4</td></tr>
  <tr><td><b>API Integration</b></td><td>Apify (optional third-party scraping)</td></tr>
</table>

---

## 📦 Prerequisites

<p>
  <img src="https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white" height="24"/>
  <img src="https://img.shields.io/badge/Node.js-18%2B-339933?style=flat-square&logo=nodedotjs&logoColor=white" height="24"/>
  <img src="https://img.shields.io/badge/Git-F05032?style=flat-square&logo=git&logoColor=white" height="24"/>
</p>

---

## 🚀 Quick Start

```bash
# Clone
git clone https://github.com/yourusername/vertiqx-leads-finder.git
cd vertiqx-leads-finder

# One command — creates venv, installs deps, launches everything
.\run.bat
```

That's it. The script handles:
1. ✅ Creates Python virtual environment
2. ✅ Installs backend dependencies + Playwright browsers
3. ✅ Installs frontend npm packages
4. ✅ Launches shared browser server (persistent Chrome)
5. ✅ Starts FastAPI backend on **port 8000**
6. ✅ Starts Next.js frontend on **port 3000**

<br>

| Service | URL |
|---|---|
| 🌐 **Frontend Dashboard** | http://localhost:3000 |
| 📡 **Backend API** | http://localhost:8000 |
| 📖 **API Docs (Swagger)** | http://localhost:8000/docs |

---

## 🔧 Manual Setup

<details>
<summary><b>📋 Backend Setup</b></summary>

```bash
cd backend

# Virtual environment
python -m venv venv
.\venv\Scripts\activate          # Windows
source venv/bin/activate          # macOS / Linux

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (chromium)
playwright install chromium

# Create environment file
copy .env .env.local              # Windows
# cp .env .env.local               # macOS / Linux
# — Edit .env.local with your SMTP / Apify credentials —

# Start the backend
uvicorn main:app --reload --port 8000
# OR: python main.py
```
</details>

<details>
<summary><b>🎨 Frontend Setup</b></summary>

```bash
cd frontend

# Install dependencies
npm install

# (Optional) Edit .env.local if backend URL differs
# Default: NEXT_PUBLIC_API_BASE=http://localhost:8000/api

# Start development server
npm run dev
```
</details>

<details>
<summary><b>🌍 Browser Server (recommended)</b></summary>

Launches a persistent Chrome instance on port 9222 that workers reuse — faster startup and no repeated browser launches.

```bash
cd backend
.\venv\Scripts\activate
python browser_server.py
```
</details>

---

## ⚙️ Configuration

### Backend Environment (`backend/.env.local`)

```env
# ─── Database ─────────────────────────────────────────────
# SQLite (default — no config needed)
# PostgreSQL (production):
# DATABASE_URL=postgresql://user:password@host:5432/leads_db

# ─── Email — Hostinger ────────────────────────────────────
HOSTINGER_PASS=your_hostinger_password
HOSTINGER_HOST=smtp.hostinger.com
HOSTINGER_PORT=465
HOSTINGER_USER=you@yourdomain.com
HOSTINGER_FROM=you@yourdomain.com

# ─── Email — Gmail (alternative) ──────────────────────────
GMAIL_PASS=your_gmail_app_password
GMAIL_HOST=smtp.gmail.com
GMAIL_PORT=587
GMAIL_USER=your_email@gmail.com
GMAIL_FROM=your_email@gmail.com

# ─── Apify (optional) ─────────────────────────────────────
APIFY_API_TOKEN=apify_api_token_here
```

### Frontend Environment (`frontend/.env.local`)

```env
NEXT_PUBLIC_API_BASE=http://localhost:8000/api
```

> 💡 SMTP settings, email templates, and Apify token can also be configured via the **Settings** page in the dashboard — those are stored in the database.

---

## 📖 Usage

```mermaid
flowchart LR
    A[Create Project] --> B[Run Scan]
    B --> C[Analyze Websites]
    C --> D[Review & Filter]
    D --> E{Has Email?}
    E -->|Yes| F[Send Outreach]
    E -->|No| G[Enrich Data]
    G --> D
    F --> H[Export CSV]
```

### 1. 👤 Create a Project
Open the dashboard → **"Create Project"** → name it (e.g., "Plumbers Chicago").

### 2. 🔍 Run a Scan
Select your project → enter **Keyword** + **Location** → set a **Limit** (50–80 recommended) → choose **Search Mode** → **Start Scan**.

> A browser window opens. If a CAPTCHA appears, solve it manually — scanning auto-resumes.

### 3. 🌐 Analyze Websites
**"Analyze All"** or select specific leads → **"Analyze Selected"**. The system visits each site, detects issues, identifies the builder, and scores the lead.

### 4. 🎯 Review & Filter

| Filter | What it finds |
|---|---|
| **Tier-1 Gold** | Bad site + AI builder + no email — your best targets |
| **Tier-1** | Bad site + weak builder |
| **> AI Builders** | Sites built with GoDaddy, Hostinger, Wix ADI |
| **> No Email** | No publicly listed email (high-value) |
| **✅ Ready to Email** | Have email + haven't been contacted |
| **📨 Email Sent** | Already emailed |

### 5. ✉️ Send Emails
Filter target leads → **"Email All"** or **"Email Selected"** → system auto-selects best template → preview → send.

### 6. 📥 Export
**"Export CSV"** — downloads all leads as a spreadsheet.

---

## 📂 Project Structure

```
vertiqx-leads-finder/
│
├── backend/                         # Python FastAPI backend
│   ├── main.py                      # API routes, startup, app config
│   ├── models.py                    # SQLModel: Lead, Project, SystemLog, Settings
│   ├── database.py                  # DB engine, session, table creation
│   ├── worker.py                    # Background workers (search/analyze/enrich)
│   ├── browser_server.py           # Persistent Chrome CDP server
│   ├── .env                         # Environment template
│   ├── requirements.txt             # Python dependencies
│   ├── Dockerfile                   # Hugging Face / Docker config
│   │
│   └── services/
│       ├── scraper.py               # Google Maps scraping
│       ├── analyzer.py              # Website analysis + fallback search
│       ├── scoring.py               # Multi-dimension scoring engine
│       ├── builder_detector.py      # CMS / builder detection
│       ├── email_extractor.py       # Email extraction & quality ranking
│       ├── emailer.py               # SMTP email service
│       ├── email_template.py        # HTML email template rendering
│       ├── apify_scraper.py         # Apify API integration
│       ├── browser_manager.py       # Shared browser connection manager
│       └── status.py                # Activity log management
│
├── frontend/                        # Next.js dashboard
│   ├── app/
│   │   ├── page.tsx                 # Main dashboard
│   │   ├── layout.tsx               # Root layout
│   │   ├── globals.css              # Tailwind + custom styles
│   │   ├── projects/page.tsx       # Project management
│   │   └── settings/page.tsx       # System configuration
│   │
│   ├── components/
│   │   ├── Navbar.tsx               # Top navigation
│   │   ├── DashboardStats.tsx       # Stats cards
│   │   ├── ProjectSelector.tsx      # Project selection
│   │   ├── CreateProjectModal.tsx   # New project modal
│   │   ├── LeadActions.tsx          # Lead action dropdown
│   │   ├── EmailModal.tsx           # Email compose modal
│   │   ├── EditLeadModal.tsx        # Edit lead modal
│   │   ├── AddLeadModal.tsx         # Manual lead addition
│   │   └── Toast.tsx                # Toast notifications
│   │
│   ├── .env.local                   # NEXT_PUBLIC_API_BASE
│   ├── package.json
│   ├── next.config.js
│   └── tailwind.config.ts
│
├── leads.db                         # SQLite database (auto-created)
├── run.bat                          # One-click startup (Windows)
├── run_backend.bat                  # Backend-only startup
├── vercel.json                      # Vercel deployment config
└── public/                          # Static assets
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/scan` | Start Google Maps scan |
| `GET` | `/api/leads` | List leads (filterable) |
| `GET` | `/api/leads/{id}` | Get single lead |
| `PUT` | `/api/leads/{id}` | Update lead |
| `DELETE` | `/api/leads/{id}` | Delete lead |
| `POST` | `/api/analyze` | Analyze website(s) |
| `POST` | `/api/enrich` | Enrich lead data |
| `POST` | `/api/send_email` | Send single email |
| `POST` | `/api/email_all` | Batch email filtered leads |
| `GET` | `/api/projects` | List projects |
| `POST` | `/api/projects` | Create project |
| `GET` | `/api/settings` | Get all settings |
| `PUT` | `/api/settings` | Update settings |
| `POST` | `/api/apify/run` | Run Apify scraper |
| `GET` | `/api/status` | Get activity log |
| `POST` | `/api/stop` | Stop running worker |
| `GET` | `/api/export/csv` | Export leads as CSV |

---

## 🛡️ Safety & Anti-Detection

| Measure | Implementation |
|---|---|
| ⏱️ **Human-like delays** | 2–6 seconds random between actions |
| 🕵️ **Stealth mode** | `playwright-stealth` — hides automation fingerprints |
| 👁️ **Headful browsing** | Visible browser window (more natural) |
| 🔒 **CAPTCHA handling** | Detects CAPTCHA → pauses → manual solve → auto-resume |
| 📉 **Rate limits** | 50–80 businesses/day recommended |
| 🔄 **User-Agent rotation** | Basic rotation implemented |
| 🖥️ **Shared browser CDP** | Reuse one Chrome instance (optional) |

> ⚠️ **Use responsibly.** Excessive scraping can lead to IP bans. Designed for ethical lead generation — respect websites' terms of service.

---

## 📊 Scoring Formula

```
Final Score = (Bad Website Score × 0.40)
            + (AI Builder Bonus × 0.20)
            + (No Email Bonus   × 0.25)
            + (Low Reviews      × 0.15)
```

| Tier | Score | Description |
|---|---|---|
| 🥇 **Tier-1 Gold** | 80–100 | Bad site + AI builder + no email |
| 🔴 **Tier-1** | 60–79 | Bad site + weak builder |
| 🟡 **Tier-2** | 40–59 | Medium quality |
| ⚪ **Ignore** | 0–39 | Strong existing sites |

---

## 🚢 Deployment

<details>
<summary><b>🐳 Backend — Docker</b></summary>

```bash
cd backend
docker build -t vertiqx-backend .
docker run -p 8000:8000 \
  -e DATABASE_URL=sqlite:///./leads.db \
  -e HOSTINGER_PASS=your_password \
  vertiqx-backend
```

Push to Hugging Face Spaces with Docker SDK — the included `Dockerfile` runs uvicorn on port 7860.
</details>

<details>
<summary><b>▲ Frontend — Vercel</b></summary>

```bash
cd frontend
npm run build        # outputs to frontend/out/
```

Deploy `frontend/` to Vercel. Configure in Vercel dashboard:
- **Root Directory:** `frontend`
- **Output Directory:** `frontend/out`
- **Build Command:** `cd frontend && npm install && npm run build`

> ⚡ Since the frontend is a static export, set `NEXT_PUBLIC_API_BASE` to your deployed backend URL before building.
</details>

---

## ❗ Troubleshooting

| Problem | Solution |
|---|---|
| **❌ Playwright browser not found** | Run `playwright install chromium` in `backend/` with venv active |
| **🔴 Port 8000 already in use** | `uvicorn main:app --reload --port 8001` + update `frontend/.env.local` |
| **🛡️ CAPTCHA blocks search** | Solve it in the visible browser — scan resumes automatically |
| **📧 Emails not sending** | Check SMTP in Settings. For Gmail, use an App Password (not your regular password) |
| **🗄️ Database errors** | Delete `leads.db` and restart — tables recreate automatically |
| **📡 Frontend shows no data** | Verify backend is running + `NEXT_PUBLIC_API_BASE` is correct |
| **🔍 No results from scan** | Try different keywords/locations. Check if Google Maps is blocking |

---

<p align="center">
  Built with ❤️ for lead generation<br>
  <sub>Private — All Rights Reserved</sub>
</p>

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:667eea,100:764ba2&height=120&section=footer" width="100%"/>
</p>
