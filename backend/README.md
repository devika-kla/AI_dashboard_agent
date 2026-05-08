# Chinook Insights — Backend

Python FastAPI backend with an OpenAI tool-calling agent that queries the Chinook music store SQLite database and generates self-contained HTML dashboards.

## Prerequisites

- Python 3.11 or higher
- An OpenAI API key — get one at https://platform.openai.com/api-keys

## Project Structure

```
backend/
├── api/
│   └── dashboard.py      # FastAPI router — /healthz + /dashboard endpoints
├── core/
│   └── agent.py          # OpenAI tool-calling loop (TOOLS, SYSTEM_PROMPT, run_agent)
├── db/
│   ├── chinook.py        # SQLite tool execution + auto-download logic
│   └── chinook.db        # Auto-downloaded Chinook database (gitignored)
├── models/
│   └── dashboard.py      # Pydantic request/response models
├── services/
│   └── dashboard.py      # Service layer — orchestrates agent + timing
├── main.py               # FastAPI app setup, CORS, lifespan, router registration
├── config.py             # All settings loaded from environment variables
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variable template
└── .env                  # Your local config (not committed)
```

## Setup

### 1. Create and activate a virtual environment

```bash
cd backend

python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and set your OpenAI API key:

```
OPENAI_API_KEY=sk-your-key-here
```

### 4. Run the server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The server starts at **http://localhost:8000**.  
The Chinook SQLite database is downloaded automatically on first run (~9 MB) and cached at `db/chinook.db`.

## API Endpoints

### `GET /healthz`
```bash
curl http://localhost:8000/healthz
# {"status":"ok"}
```

### `POST /dashboard`
```bash
curl -X POST http://localhost:8000/dashboard \
  -H "Content-Type: application/json" \
  -d '{"kpis": ["revenue", "top customers", "sales by country"], "verbose": false}'
```

**Request body:**
```json
{
  "kpis": ["revenue", "top customers", "sales by country"],
  "verbose": false,
  "session_id": "user-001"
}
```

**Response:**
```json
{
  "html": "<complete self-contained HTML dashboard>",
  "panel_count": 3,
  "execution_time_ms": 14200,
  "session_id": "user-001"
}
```

## Interactive API Docs

FastAPI auto-generates docs at:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `OPENAI_API_KEY` | Yes | — | Your OpenAI API key |
| `OPENAI_MODEL` | No | `gpt-4o-mini` | Model to use |
| `OPENAI_BASE_URL` | No | `https://api.openai.com/v1` | API base URL |
| `CORS_ORIGINS` | No | `http://localhost:5173,...` | Comma-separated allowed origins |

## How the Agent Works

1. Request arrives at `api/dashboard.py` → routed to `services/dashboard.py`
2. Service calls `core/agent.py` → `run_agent(kpis, verbose, session_id)`
3. Agent sends KPIs to OpenAI with 3 SQL tools:
   - `list_tables` — lists all tables in the Chinook DB
   - `describe_table` — returns column schema for a table
   - `run_sql_query` — executes a read-only SELECT (max 300 rows)
4. OpenAI calls tools → `db/chinook.py` executes against the local SQLite file
5. Loop continues (max 20 iterations) until the model returns finished HTML
6. HTML is extracted and returned as `DashboardResponse`
