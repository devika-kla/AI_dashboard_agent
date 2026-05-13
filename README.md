# 📊 AI KPI Dashboard Generator
### LangGraph · FastAPI · Streamlit · OpenAI GPT · SQLite · Plotly

An AI-powered KPI dashboard generator that converts natural language requests into interactive, data-driven dashboards — orchestrated by a **LangGraph workflow**, powered by an OpenAI LLM, and rendered live in Streamlit.

---

## ✨ Features

- **Natural language KPI input** — describe what you want to see, not how to query it
- **Single LLM call** — one prompt generates the full dashboard spec (no agent loops)
- **Automatic SQL generation** — LLM writes SQLite-compatible `SELECT` queries on the fly
- **Multi-chart dashboards** — at least 2–3 widgets per KPI: metric cards, trends, rankings
- **LangGraph workflow** — explicit node graph with error routing
- **Interactive Plotly charts** — rendered live in Streamlit
- **FastAPI backend** — clean REST endpoint for dashboard generation
- **SQLite integration** — uses the Chinook sample music store database

---

## 🏗️ Architecture

```text
User Input
    ↓
Streamlit Frontend
    ↓
FastAPI API
    ↓
LangGraph Workflow
    ↓
LLM Generates Dashboard Spec
    ↓
Route On Error (conditional edge)
    ↓
Execute SQL Queries
    ↓
Attach Data To Widgets
    ↓
Return Dashboard JSON
    ↓
Render Interactive Dashboard
```

## 🤖 LangGraph Workflow

The application uses a **3-node LangGraph workflow** with a conditional error routing edge.

### Agent Graph

![LangGraph Agent Flow](langgraph_flow.jpg)

```
__start__
    ↓
generate_dashboard_spec
    ↓
route_on_error ──── error ──────────────→ __end__
    │
  success
    ↓
execute_dashboard_queries
    ↓
__end__
```

---

### Node 1 — `generate_dashboard_spec`

Responsible for:
- Understanding KPI requests
- Generating dashboard structure
- Creating widget definitions
- Generating SQLite `SELECT` queries
- Retrying up to 3 times on JSON parse failure

**Output:**

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
          "sql": "SELECT strftime('%Y-%m', InvoiceDate) AS Month, SUM(Total) AS Sales FROM invoices GROUP BY Month ORDER BY Month LIMIT 50"
        }
      ]
    }
  ]
}
```

---

### conditional node — `route_on_error`

A conditional function that:
- Inspects `state["error"]`
- Routes to `execute_dashboard_queries` on success
- Routes directly to `__end__` if spec generation failed

This node is rendered explicitly in the graph so the branching logic is visible in the diagram.

---

### Node 2 — `execute_dashboard_queries`

Responsible for:
- Executing SQL queries against SQLite
- Fetching and formatting result rows as JSON
- Appending `data` to each widget in-place

**Final output:**

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
          "sql": "...",
          "data": [
            { "Month": "2020-01", "Sales": 37.62 },
            { "Month": "2020-02", "Sales": 52.47 }
          ]
        }
      ]
    }
  ]
}
```

---

### LangGraph State

```python
class DashboardState(TypedDict):
    kpis: List[str]
    schema: str           # filtered schema subset, read-only after node 1
    dashboard: Dict       # mutated in-place: spec → spec + data
    error: Optional[str]  # surfaces failures without raising exceptions
```

---

## 📊 Dashboard Output

![Dashboard Output](kpi_dashboard_output.pdf)

> See [`kpi_dashboard_output.pdf`](kpi_dashboard_output.pdf) for the full rendered dashboard example.

---

## 📦 Supported Widget Types

| Widget Type | Description                    |
|-------------|--------------------------------|
| `metric`    | Single KPI value card          |
| `line`      | Trend visualization over time  |
| `bar`       | Category comparison chart      |
| `pie`       | Distribution / share view      |
| `table`     | Tabular data insights          |

---

## 🛠️ Tech Stack

| Layer             | Technology         |
|-------------------|--------------------|
| Frontend          | Streamlit          |
| Backend API       | FastAPI            |
| Workflow Engine   | LangGraph          |
| LLM               | OpenAI GPT         |
| Database          | SQLite (Chinook)   |
| Visualization     | Plotly             |
| ORM / DB Access   | SQLAlchemy         |
| Config Management | Pydantic Settings  |

---

## 🗄️ Database

This project uses the [Chinook SQLite sample database](https://github.com/lerocha/chinook-database) — a music store dataset.

**Main tables used:**

| Table         | Description                        |
|---------------|------------------------------------|
| `Invoice`     | Customer purchase records          |
| `InvoiceLine` | Line items per invoice             |
| `Customer`    | Customer details and location      |
| `Track`       | Song/track metadata                |
| `Album`       | Album metadata                     |
| `Artist`      | Artist names                       |
| `Genre`       | Music genre classification         |

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone <repo-url>
cd project
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

```bash
# Windows
.venv\Scripts\activate

# Mac / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
DB_PATH=db/chinook.db
```

### 5. Run the FastAPI backend

```bash
uvicorn main:app --reload
```

Backend runs at: [http://localhost:8000](http://localhost:8000)

### 6. Run the Streamlit frontend

```bash
streamlit run streamlit_app.py
```

Frontend runs at: [http://localhost:8501](http://localhost:8501)

---

## 🔌 API Reference

### `POST /generate-dashboard`

Generates a complete dashboard specification with data for the requested KPIs.

**Request:**

```json
{
  "kpis": [
    "monthly sales",
    "top customers",
    "revenue by country"
  ]
}
```

**Response:**

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

## 💡 Example KPI Inputs

Try any of the following in the Streamlit UI:

```
monthly sales
top customers
revenue by country
top tracks
genre popularity
customer growth
sales trend
artist revenue
```

---

## 📄 License

This project is for educational and demonstration purposes using the [Chinook sample database](https://github.com/lerocha/chinook-database).