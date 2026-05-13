"""
services/kpi_planner.py

kpi_planner tool implementation.

Input : comma-separated KPI keywords  e.g. "revenue, churn, top customers"
Output: JSON array — one panel spec per keyword

Each panel spec:
  {
    "kpi_name"     : "Revenue by month",
    "keyword"      : "revenue",
    "chart_type"   : "bar",          # bar | line | pie | doughnut | stat
    "description"  : "Total invoice amount grouped by calendar month",
    "tables_needed": ["Invoice"]     # hints for the agent's sql_db_schema calls
  }

chart_type guide:
  stat     = single aggregate number (COUNT, SUM, AVG — no GROUP BY)
  bar      = comparison across categories
  line     = trend over time (dates/months on x-axis)
  pie      = part-of-whole with few categories (≤ 8)
  doughnut = same as pie, preferred when a center label is useful

The agent uses tables_needed to call sql_db_schema, then writes and
runs the SQL itself via sql_db_query / sql_db_query_checker.
"""

from __future__ import annotations

import json
import re

from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI


_SYSTEM = """\
You are a BI dashboard planning expert.

Given KPI keywords and a database schema, produce a dashboard plan:
one panel spec per keyword.

For each keyword output:
  kpi_name     : short human-readable metric name (≤ 5 words)
  keyword      : the original keyword, lower-cased
  chart_type   : EXACTLY one of: bar | line | pie | doughnut | stat
                 stat = a single aggregate number (no grouping)
                 bar  = comparison across named categories
                 line = trend over time (x-axis is dates or months)
                 pie / doughnut = proportional breakdown (≤ 8 slices)
  description  : one sentence — what this panel shows and why it matters
  tables_needed: list of table names from the schema that are relevant

Return ONLY a JSON array, no markdown, no commentary.

Example:
[
  {
    "kpi_name": "Revenue by month",
    "keyword": "revenue",
    "chart_type": "line",
    "description": "Total invoice amount per calendar month showing sales trend.",
    "tables_needed": ["Invoice"]
  },
  {
    "kpi_name": "Total customers",
    "keyword": "customers",
    "chart_type": "stat",
    "description": "Count of unique customers in the database.",
    "tables_needed": ["Customer"]
  }
]
"""


def plan_kpis(keywords_str: str, db: SQLDatabase, llm: ChatOpenAI) -> str:
    """Map KPI keywords → panel plan JSON. Called by the kpi_planner Tool."""
    schema = db.get_table_info()
    prompt = f"{_SYSTEM}\n\nDatabase schema:\n{schema}\n\nKPI keywords: {keywords_str}"

    response = llm.invoke(prompt)
    raw = _strip_fences(response.content)

    try:
        panels = json.loads(raw)
        if not isinstance(panels, list):
            raise ValueError("Expected a JSON array")
        return json.dumps(panels)
    except Exception as exc:
        return json.dumps({"error": str(exc), "raw": raw[:400]})


def _strip_fences(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```[a-zA-Z]*\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()