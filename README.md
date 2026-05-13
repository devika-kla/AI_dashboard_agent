# 📊 AI KPI Dashboard Generator

An AI-powered dashboard generation system that converts natural language KPI requests into interactive, data-driven dashboards — powered by an LLM, a FastAPI backend, a Streamlit frontend, and the Chinook SQLite dataset.

---

## ✨ Features

- **Natural language KPI input** — describe what you want to see, not how to query it
- **Dynamic SQL generation** — LLM writes SQLite-compatible SELECT queries on the fly
- **Single LLM call architecture** — fast, reliable, and cost-efficient (no agent loops)
- **Multiple chart types per KPI** — line, bar, pie, metric cards, and tables
- **Interactive Plotly visualizations** — rendered live in Streamlit
- **FastAPI backend API** — clean REST endpoint for dashboard generation
- **Lightweight & maintainable** — no LangChain, no tool-calling, minimal dependencies

---

## 🛠️ Tech Stack

| Layer             | Technology         |
|-------------------|--------------------|
| Frontend          | Streamlit          |
| Backend API       | FastAPI            |
| LLM               | OpenAI GPT         |
| Database          | SQLite (Chinook)   |
| Visualization     | Plotly             |
| ORM / DB Access   | SQLAlchemy         |
| Config Management | Pydantic Settings  |

---

## 📁 Project Structure

```
project/
│
├── api/
│   └── routes.py
│
├── core/
│   ├── prompts.py
│   └── llm.py
│
├── db/
│   └── chinook.db
│
├── models/
│   └── dashboard_models.py
│
├── services/
│   ├── dashboard_service.py
│   ├── database_service.py
│   └── schema_service.py
│
├── main.py
├── config.py
├── streamlit_app.py
├── requirements.txt
└── README.md
```

---

## 🏗️ Architecture

### High-Level Flow

```
User (Streamlit UI)
        ↓
FastAPI Endpoint
        ↓
Dashboard Service
        ↓
OpenAI LLM
        ↓
Dashboard Spec (JSON)
        ↓
SQL Execution
        ↓
Data Injection
        ↓
Frontend Rendering
```

### Detailed Workflow

#### 1. User Inputs KPIs

The user types one or more KPIs into the Streamlit interface. Example:

```
monthly sales, top customers, revenue by country
```

The request is sent from Streamlit to the FastAPI backend.

#### 2. LLM Generates Dashboard Spec

A **single LLM call** generates the complete dashboard specification, including:

- Dashboard title
- Sections (one per KPI)
- Widgets (charts, metrics, tables)
- Chart types
- SQL queries

Example LLM output:

```json
{
  "dashboard_title": "Sales Dashboard",
  "sections": [
    {
      "kpi": "monthly sales",
      "widgets": [
        {
          "title": "Monthly Sales Trend",
          "chart_type": "line",
          "sql": "SELECT strftime('%Y-%m', InvoiceDate) AS Month, SUM(Total) AS Sales FROM invoices GROUP BY Month ORDER BY Month"
        }
      ]
    }
  ]
}
```

#### 3. Backend Executes SQL

For every widget, the backend:

1. Executes the SQL query on the SQLite Chinook database
2. Converts results into JSON rows
3. Attaches data directly to the widget object

Example widget with data attached:

```json
{
  "title": "Monthly Sales Trend",
  "chart_type": "line",
  "sql": "SELECT ...",
  "data": [
    { "Month": "2025-01", "Sales": 1200 },
    { "Month": "2025-02", "Sales": 1450 }
  ]
}
```

#### 4. Streamlit Renders Dashboard

The frontend dynamically renders each widget using Plotly:

- **KPI cards** for single metric values
- **Line charts** for trends over time
- **Bar charts** for category comparisons
- **Pie charts** for distribution breakdowns
- **Tables** for raw tabular insights

---

## 🤖 LLM Strategy

### Single LLM Call Architecture

The system is intentionally designed around **one LLM call** — no agent loops, no tool-calling, no LangChain.

| Property       | Benefit                        |
|----------------|--------------------------------|
| Single call    | Fast response time             |
| No agent loops | Predictable, reliable output   |
| Minimal tokens | Lower cost per request         |
| No frameworks  | Simple to maintain and debug   |

### Prompt Engineering

The LLM prompt enforces strict constraints to ensure safe, usable output:

- SQLite-compatible SQL only
- `SELECT`-only queries (no mutations)
- Multiple widgets per KPI section
- Business-friendly chart titles
- Proper aggregations and groupings
- No markdown fences or code blocks
- Dashboard-ready JSON structure

---

## 📦 Supported Widget Types

| Widget Type | Description                   |
|-------------|-------------------------------|
| `metric`    | Single KPI value card         |
| `line`      | Trend visualization over time |
| `bar`       | Category comparison chart     |
| `pie`       | Distribution / share view     |
| `table`     | Tabular data insights         |

---

## 🔌 API Reference

### `POST /generate-dashboard`

Generates a complete dashboard specification with data for the requested KPIs.

**Request Body**

```json
{
  "kpis": [
    "monthly sales",
    "top customers"
  ]
}
```

**Response**

```json
{
  "dashboard_title": "Music Store Dashboard",
  "sections": [
    {
      "kpi": "monthly sales",
      "widgets": [
        {
          "title": "Monthly Sales Trend",
          "chart_type": "line",
          "sql": "SELECT ...",
          "data": [...]
        }
      ]
    }
  ]
}
```

---

## 🚀 Getting Started

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
DB_PATH=db/chinook.db
```

### 3. Run the FastAPI Backend

```bash
uvicorn main:app --reload
```

Backend runs at: [http://localhost:8000](http://localhost:8000)

### 4. Run the Streamlit Frontend

```bash
streamlit run streamlit_app.py
```

Frontend runs at: [http://localhost:8501](http://localhost:8501)

---

## 💡 Example KPI Inputs

Try any of the following in the Streamlit UI:

```
monthly sales
top customers
revenue by country
top genres
sales trend
customer retention
```

---

## 📄 License

This project is for educational and demonstration purposes using the [Chinook sample database](https://github.com/lerocha/chinook-database).