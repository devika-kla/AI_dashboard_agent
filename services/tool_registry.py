"""
services/tool_registry.py

Tool set for the KPI dashboard agent.

Built-in from SQLDatabaseToolkit (used as-is):
  sql_db_list_tables   — list all tables in the DB
  sql_db_schema        — get DDL + sample rows for given tables
  sql_db_query         — execute a SQL SELECT and return rows
  sql_db_query_checker — ask LLM to verify SQL before running

Custom (added on top):
  kpi_planner       — maps KPI keywords → one panel spec per keyword
  dashboard_builder — takes all fetched panel data → self-contained HTML dashboard
"""

from __future__ import annotations

from langchain.tools import Tool
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI

from services.kpi_planner import plan_kpis
from services.dashboard_builder import build_dashboard


def build_tools(db: SQLDatabase, llm: ChatOpenAI) -> list[Tool]:
    """
    Return the full tool list for the dashboard agent:
      4 toolkit built-ins  +  2 custom tools  =  6 total
    """
    # ── built-ins from LangChain SQLDatabaseToolkit ────────────
    # Gives us: sql_db_query, sql_db_schema,
    #           sql_db_list_tables, sql_db_query_checker
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    sql_tools = toolkit.get_tools()

    # ── custom: KPI planner ────────────────────────────────────
    kpi_planner_tool = Tool(
        name="kpi_planner",
        description=(
            "ALWAYS call this first. "
            "Input: the raw KPI keyword string from the user "
            "(e.g. 'revenue, top customers, sales by country'). "
            "Returns a JSON array — one panel spec per keyword — each containing: "
            "kpi_name, keyword, chart_type (bar|line|pie|doughnut|stat), "
            "description, and tables_needed. "
            "Use this plan to drive all subsequent sql_db_schema and sql_db_query calls."
        ),
        func=lambda keywords: plan_kpis(keywords, db, llm),
    )

    # ── custom: dashboard builder ──────────────────────────────
    dashboard_builder_tool = Tool(
        name="dashboard_builder",
        description=(
            "Call this LAST after fetching data for all KPI panels. "
            "Input: a JSON array where each element is a panel spec enriched with "
            "query results. Each element must have: "
            "kpi_name, keyword, chart_type, description, columns (list of str), "
            "rows (list of lists). "
            "Returns JSON with 'html' (complete self-contained Chart.js dashboard) "
            "and 'panel_count'. The html value is the final answer."
        ),
        func=build_dashboard,
    )

    return sql_tools + [kpi_planner_tool, dashboard_builder_tool]