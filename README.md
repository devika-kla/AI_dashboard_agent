# 📊 AI KPI Dashboard Agent

An AI-powered dashboard generation system that converts simple KPI keywords into a fully functional, self-contained HTML dashboard using SQL + LLM reasoning.

Built using:
- LangChain SQL Agent
- OpenAI LLM
- Chinook Dataset
- FastAPI
- Chart.js (for visualization)

---

## 🚀 Overview

This system allows users to input **KPI keywords** like:
"revenue, churn, top customers"

And automatically:
1. Plans dashboard panels (via LLM)
2. Generates SQL queries
3. Fetches data from database
4. Builds a complete interactive dashboard (HTML)

---

## 🧠 Architecture
User Input (KPIs)
↓
kpi_planner (LLM)
↓
SQL Tools (LangChain Toolkit)
↓
dashboard_builder
↓
Final HTML Dashboard


---

## 🧰 Tools Used

### 🔹 Built-in SQL Tools (LangChain)
- `sql_db_list_tables`
- `sql_db_schema`
- `sql_db_query`
- `sql_db_query_checker`

### 🔹 Custom Tools
- `kpi_planner`
- `dashboard_builder`

---


---

## ⚙️ API Endpoints

### ▶️ Create Dashboard

POST /dashboard

#### Request:
```json
{
  "kpis": ["revenue", "top customers", "sales by country"],
  "session_id": "test-123"
}
```

#### Response:
```json
{
  "html": "<full dashboard html>",
  "panel_count": 3,
  "execution_time_ms": 1200,
  "session_id": "test-123"
}
```

### 👀 Preview Dashboard
GET /dashboard/preview/{session_id}

Open in browser to view rendered dashboard.

## Generated Output Dashboard
input - 
  "kpis": ["total revenue","monthly revenue","top customers","sales by country","top tracks","sales by genre","sales trend"]
  
![Project Screenshot](\outputs\user-008\Screenshot_4-5-2026_174247_.jpeg)

## 🧪 Test Cases (Multi-KPI Inputs)

The agent is designed to handle multiple KPI keywords (5–6 at once) and generate a complete dashboard in a single run.

🔹 1. Basic Mixed Dashboard
["revenue", "customers", "invoices", "sales by country", "top customers"]
🔹 2. Business Overview Dashboard
["total revenue", "monthly sales", "top customers", "sales by country", "invoice count", "average invoice value"]
🔹 3. Sales-Focused Dashboard
["revenue over time", "top selling tracks", "sales by genre", "top customers", "revenue by country"]
🔹 4. Customer Insights Dashboard
["customer count", "top customers", "customers by country", "repeat customers", "average spend per customer"]
🔹 5. Product / Music Analytics (Chinook-specific)
["top tracks", "top artists", "sales by genre", "album performance", "track purchases", "revenue by artist"]
🔹 6. Time-Series Heavy Dashboard
["monthly revenue", "yearly sales trend", "invoice trend", "customer growth", "revenue over time"]
🔹 7. Distribution + Ranking Mix
["sales by country", "sales by genre", "top customers", "top tracks", "revenue distribution"]
🔹 8. Stress Test (7 KPIs)
["total revenue", "monthly revenue", "top customers", "sales by country", "top tracks", "sales by genre", "sales trend"]
🔹 9. Synonym Robustness Test
["income", "earnings", "client count", "purchases", "sales trend", "revenue distribution"]
🔹 10. Noisy Input Test
["revenue","abc xyz", "top customers", "???", "sales by country", "random metric"]