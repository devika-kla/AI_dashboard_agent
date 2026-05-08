# Chinook Insights

An agentic BI dashboard generator. Enter KPI keywords — an AI agent queries the Chinook music store SQLite database with SQL tools and generates a complete HTML dashboard with Chart.js charts, metric cards, and data tables.

## Project Structure

```
chinook-insights/
├── backend/                   # Python FastAPI + OpenAI agent
│   ├── api/
│   │   └── dashboard.py       # FastAPI router
│   ├── core/
│   │   └── agent.py           # Tool-calling agent loop
│   ├── db/
│   │   ├── chinook.py         # SQLite tools + auto-download
│   │   └── chinook.db         # Auto-downloaded (gitignored)
│   ├── models/
│   │   └── dashboard.py       # Pydantic models
│   ├── services/
│   │   └── dashboard.py       # Service layer
│   ├── main.py                # FastAPI app entry point
│   ├── config.py              # Environment settings
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
│
├── frontend/                  # React + Vite + TypeScript UI
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── index.css
│   │   └── pages/Home.tsx
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts         # Proxies /api → localhost:8000
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   └── README.md
│
└── README.md
```

## Quick Start

You need **two terminals** — one for the backend, one for the frontend.

### Terminal 1 — Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env — add your OPENAI_API_KEY

# Start the server (auto-downloads chinook.db on first run)
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Backend available at **http://localhost:8000**

### Terminal 2 — Frontend

```bash
cd frontend

npm install
npm run dev
```

Open **http://localhost:5173** in your browser.

## How It Works

```
User enters KPIs  →  POST /dashboard
                          ↓
                  services/dashboard.py
                          ↓
                    core/agent.py
                          ↓
                OpenAI (gpt-4o-mini)
                     ↓         ↑
               tool_call?    tool result
                     ↓
             db/chinook.py (SQLite)
               list_tables
               describe_table
               run_sql_query
                          ↓
                    HTML dashboard
                          ↓
              Rendered in <iframe>
```

## Requirements

| Component | Version |
|---|---|
| Python | 3.11+ |
| Node.js | 18+ |
| OpenAI API key | Required |

## Tech Stack

| | Technology |
|---|---|
| **Frontend** | React 18, Vite, TypeScript, Tailwind CSS, TanStack Query, Framer Motion |
| **Backend** | Python 3.11, FastAPI, Uvicorn, Pydantic v2 |
| **AI Agent** | OpenAI SDK, `gpt-4o-mini`, tool-calling loop |
| **Database** | Chinook SQLite (auto-downloaded) |
