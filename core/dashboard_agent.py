"""
core/dashboard_agent.py

KPI Dashboard Agent — uses LangChain SQLDatabaseToolkit built-ins
for all SQL work, plus two custom tools (kpi_planner, dashboard_builder).

Tool inventory (6 total):
  From SQLDatabaseToolkit:
    sql_db_list_tables   — discover what tables exist
    sql_db_schema        — get DDL + sample rows for specific tables
    sql_db_query         — run a SELECT and return rows
    sql_db_query_checker — verify SQL correctness before running

  Custom:
    kpi_planner       — maps KPI keywords → panel specs with chart_type & tables_needed
    dashboard_builder — assembles enriched panel specs → self-contained HTML dashboard

Agent loop per KPI panel:
  sql_db_schema(tables_needed) → understand columns
  sql_db_query_checker(sql)    → verify the query
  sql_db_query(sql)            → fetch rows
  → accumulate panel result
  → dashboard_builder([all panels])
"""
import json
import time

from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI

from config import settings
from services.tool_registry import build_tools
# from core.prompts import _PROMPT
from core.utils import _extract_json_object


# ── System prompt ───────────────────────────────────────────────
# Rules:
#   {tools}            - required by create_react_agent (tool descriptions)
#   {tool_names}       - required by create_react_agent (comma-separated names)
#   {agent_scratchpad} - required by create_react_agent (running thought log)
#   {input}            - the user's question
#   {system_context}   - our custom instructions, injected at build time
#
# Never pre-fill {tools}, {tool_names}, or {agent_scratchpad} with .replace() —
# create_react_agent validates that these variables exist in the prompt template
# before accepting it. Injecting them early removes them and causes the error:
#   "Prompt missing required variables: {'tool_names', 'tools', 'agent_scratchpad'}"
 
_PROMPT = """\
{system_context}
 
AVAILABLE TOOLS:
{tools}
 
FORMAT — use exactly this structure for every step:
Question: {{input}}
Thought: <reasoning>
Action: <one tool name from [{tool_names}]>
Action Input: <input to that tool>
Observation: <tool output>
... (repeat Thought / Action / Action Input / Observation)
Thought: I have all enriched panels and am ready to build the dashboard.
Action: dashboard_builder
Action Input: <JSON array of all enriched panel objects>
Observation: <dashboard JSON>
Thought: Dashboard is ready.
Final Answer: <full JSON from dashboard_builder, unmodified>
 
Begin!
 
Question: {input}
Thought:{agent_scratchpad}"""
 
 
# Custom instructions injected into {system_context} at build time.
# Safe to use plain braces here — this string is never parsed as a template.
_SYSTEM_CONTEXT = """You are a KPI Dashboard Agent. You build data dashboards from KPI keywords.
 
WORKFLOW (follow this order strictly):
 
STEP 1 - Plan
  Call kpi_planner once with the user's full keyword string.
  It returns a JSON array of panel specs, each with:
    kpi_name, keyword, chart_type, description, tables_needed
 
STEP 2 - Fetch data for each panel
  For EACH panel spec returned by kpi_planner, run this loop:
 
  2a. sql_db_schema  — input: comma-separated table names from tables_needed
      Study the columns so you can write correct SQL.
 
  2b. sql_db_query_checker  — input: your SQL string
      Always verify before running. Fix any issues flagged.
 
  2c. sql_db_query  — input: the verified SQL string
      Captures the result as a string like: [(val1, val2), ...]
 
  2d. Parse result into columns + rows:
      - column names come from your SELECT clause aliases
      - rows come from parsing the returned string
 
  2e. Build the enriched panel object (plain JSON, no markdown):
      {
        "kpi_name"   : "...",
        "keyword"    : "...",
        "chart_type" : "bar|line|pie|doughnut|stat",
        "description": "...",
        "columns"    : ["col_a", "col_b"],
        "rows"       : [[val1, val2], [val1, val2]]
      }
 
STEP 3 - Build dashboard
  Call dashboard_builder ONCE with a JSON array of ALL enriched panel objects.
  Return the full JSON output from dashboard_builder as your Final Answer.
 
SQL RULES:
- Plain SQL only — no backticks, no markdown fences.
- SELECT only — never INSERT, UPDATE, DELETE, DROP.
- LIMIT 50 for grouped queries; LIMIT 1 for single-value stat queries.
- SQLite date grouping: strftime('%Y-%m', date_column).
- Always call sql_db_query_checker before sql_db_query."""
 

def build_dashboard_agent(db_path: str | None = None) -> tuple[AgentExecutor, SQLDatabase]:
    """Construct and return the dashboard AgentExecutor."""
    db_path = db_path or settings.DB_PATH
    db = SQLDatabase.from_uri(
        f"sqlite:///{db_path}",
        sample_rows_in_table_info=2,
    )
    llm = ChatOpenAI(
        model=settings.OPENAI_MODEL,
        temperature=0,
        openai_api_key=settings.OPENAI_API_KEY,
    )

    tools = build_tools(db=db, llm=llm)
 
    # Only inject {system_context} here — leave {tools}, {tool_names},
    # {agent_scratchpad}, and {input} for create_react_agent to handle.
    prompt = PromptTemplate(
        input_variables=["input", "agent_scratchpad", "tools", "tool_names"],
        partial_variables={"system_context": _SYSTEM_CONTEXT},
        template=_PROMPT,
    )
 

    agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)

    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        return_intermediate_steps=True,
        # Each panel needs ~4 steps (schema + checker + query + think);
        # allow headroom for retries and the planner/builder bookends.
        max_iterations=8 + 4 * 6,  # supports up to ~6 KPI panels
    )

    return executor, db


def run_dashboard(
    kpis: list[str],
    db_path: str | None = None,
    verbose: bool = False,
) -> dict:
    """
    Run the dashboard agent for a list of KPI keywords.

    Returns:
      {
        "html"             : "<self-contained Chart.js HTML>",
        "panel_count"      : N,
        "execution_time_ms": ms,
      }
    """
    executor, _ = build_dashboard_agent(db_path)
    keywords_str = ", ".join(kpis)

    start = time.time()
    response = executor.invoke({"input": keywords_str})
    elapsed = int((time.time() - start) * 1000)

    raw_output = response.get("output", "")

    html = ""
    panel_count = 0
    try:
        match = _extract_json_object(raw_output)
        if match:
            parsed = json.loads(match)
            html = parsed.get("html", "")
            panel_count = parsed.get("panel_count", 0)
    except Exception:
        html = raw_output  # fallback if output is already raw HTML

    return {
        "html": html,
        "panel_count": panel_count,
        "execution_time_ms": elapsed,
    }

