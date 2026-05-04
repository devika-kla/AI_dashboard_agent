# 📊 AI Dashboard Agent (Backend)

An intelligent backend service that converts natural language queries into fully interactive data dashboards.

This system uses an **agentic workflow powered by LLMs** to:

* Understand user questions
* Generate SQL queries
* Extract insights
* Automatically build a **self-contained HTML dashboard** with charts and tables

---

## 🚀 Features

* 🔍 Natural language → SQL query execution
* 🧠 Agent-based reasoning (ReAct pattern)
* 📈 Automatic chart selection (bar, line, pie, KPI, table)
* 💡 Insight generation for visualizations
* 🖥️ Fully rendered HTML dashboard (Chart.js)
* 🌐 Auto-opens dashboard in browser
* 🧩 Modular tool-based architecture

---
## Output Dashboard

<img src="\AI_dashboard_agent\Screenshot_4-5-2026_105938_.jpeg" alt="Generated Dashboard">

## 🏗️ Architecture Overview

```
User Query
    ↓
Agent (LLM + Tools)
    ↓
1. Generate sub-questions
2. Run SQL queries
3. Generate insights
    ↓
Backend processing
    ↓
HTML Dashboard Generator
    ↓
Browser Rendering
```

---

## 🧰 Tech Stack

* **FastAPI** – API framework
* **LangChain** – Agent + tool orchestration
* **OpenAI / LLM** – reasoning & generation
* **SQLite** – database (Chinook sample DB)
* **Chart.js** – frontend visualization (in HTML)

---

## 📂 Project Structure

```
backend/
│
├── core/
│   └── agent.py                # Agent + prompt setup
│
├── services/
│   ├── tool_registry.py       # Tool definitions
│   ├── agent_service.py       # Agent execution logic
│   └── response_service.py    # Parsing + HTML handling
│
├── db/
│   └── connection.py          # DB + LLM initialization
│
├── models/
│   └── agent_models.py        # Pydantic models
│
├── api/
│   └── routes.py              # FastAPI endpoints
│
└── main.py                    # App entry point
```

---

## ⚙️ Setup Instructions

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd backend
```

---

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Configure environment variables

Create a `.env` file:

```env
OPENAI_API_KEY=your_api_key_here
```

---

### 5. Run the server

```bash
uvicorn main:app --reload
```

---

## 📡 API Endpoint

### ▶️ Generate Dashboard

```http
POST /dashboard
```

### Request Body

```json
{
  "query": "Show me monthly sales trends and top customers"
}
```

---

### Response

```json
{
  "html": "<!DOCTYPE html>...",
  "widgets": [...],
  "intermediate_steps": [...]
}
```

---

## 🌐 How It Works

1. User sends a query
2. Agent:

   * Breaks into sub-questions
   * Generates SQL
   * Executes queries
   * Produces insights
3. Backend:

   * Reconstructs structured widget data
   * Generates dashboard HTML
4. System:

   * Opens dashboard automatically in browser

---

## 🧠 Agent Workflow

The agent follows a structured pipeline:

* `generate_dashboard_questions`
* `sql_db_query`
* `generate_insight`
* `build_dashboard_html`

---

## 📊 Output

The system generates a **fully self-contained HTML dashboard** with:

* KPI cards
* Line / bar / pie charts
* Data tables
* Business insights

No frontend required — runs directly in browser.

---

## ⚠️ Notes

* Currently uses SQLite (Chinook DB)
* Only supports **read queries (SELECT)**
* LLM output is validated and post-processed for stability
* HTML generation includes fallback if agent fails

---

## 🔮 Future Improvements

* Filters & interactivity (date range, dropdowns)
* Export dashboard (PDF / image)
* Multi-database support
* Frontend UI (React)
* Saved dashboards



