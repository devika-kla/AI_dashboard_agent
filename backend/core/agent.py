import json
import re
import logging
import sys
import os
from typing import Optional
from openai import AsyncOpenAI

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL
from db.chinook import execute_tool

logger = logging.getLogger(__name__)

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_tables",
            "description": "List all tables in the Chinook SQLite database.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "describe_table",
            "description": "Get the schema/columns of a specific table.",
            "parameters": {
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Name of the table to describe",
                    }
                },
                "required": ["table_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_sql_query",
            "description": (
                "Execute a read-only SQL SELECT query on the Chinook database "
                "and return results as JSON."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "A SQL SELECT query to execute",
                    }
                },
                "required": ["query"],
            },
        },
    },
]

SYSTEM_PROMPT = """You are an expert data analyst with access to the Chinook music store SQLite database.

Tables available:
- Customer (CustomerId, FirstName, LastName, Company, City, State, Country, Email, SupportRepId)
- Invoice (InvoiceId, CustomerId, InvoiceDate, BillingCity, BillingCountry, Total)
- InvoiceLine (InvoiceLineId, InvoiceId, TrackId, UnitPrice, Quantity)
- Track (TrackId, Name, AlbumId, MediaTypeId, GenreId, Milliseconds, UnitPrice)
- Album (AlbumId, Title, ArtistId)
- Artist (ArtistId, Name)
- Genre (GenreId, Name)
- MediaType (MediaTypeId, Name)
- Playlist (PlaylistId, Name)
- PlaylistTrack (PlaylistId, TrackId)
- Employee (EmployeeId, LastName, FirstName, Title, ReportsTo, HireDate, Country, Email)

Instructions:
1. For each KPI, run SQL queries to gather real data from the database.
2. Compile everything into a single self-contained HTML dashboard.
3. Return ONLY the complete HTML document — no markdown, no explanation.

Dashboard requirements:
- Complete self-contained HTML with inline CSS and Chart.js from CDN
- Dark theme: background #0f172a, cards #1e293b, accent #3b82f6
- One card per KPI with metric totals, charts (bar/pie/line), and a data table
- Responsive CSS grid, gradients, box shadows, clean typography
- Header: "Business Intelligence Dashboard" with KPI subtitle
"""


async def run_agent(
    kpis: list[str],
    verbose: bool = False,
) -> dict:
    if not OPENAI_API_KEY:
        raise ValueError(
            "OPENAI_API_KEY is not set. Copy .env.example to .env and add your key."
        )

    client = AsyncOpenAI(base_url=OPENAI_BASE_URL, api_key=OPENAI_API_KEY)

    kpi_list = "\n".join(f"- {k}" for k in kpis)
    user_message = (
        f"Generate a dashboard for these KPIs:\n\n{kpi_list}\n\n"
        "Query the database for real data and return ONLY the HTML document."
    )

    messages: list[dict] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    html_output = "<html><body><p>Error: agent produced no output.</p></body></html>"

    for iteration in range(20):
        if verbose:
            logger.info(f"Agent iteration {iteration + 1} | messages: {len(messages)}")

        response = await client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            tools=TOOLS,
            max_tokens=16384,
        )

        choice = response.choices[0]
        msg = choice.message

        messages.append(
            {
                "role": "assistant",
                "content": msg.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in (msg.tool_calls or [])
                ]
                or None,
            }
        )

        if choice.finish_reason == "stop" or not msg.tool_calls:
            html_output = msg.content or html_output
            break

        for tc in msg.tool_calls:
            try:
                args = json.loads(tc.function.arguments)
            except json.JSONDecodeError:
                args = {}

            if verbose:
                logger.info(f"  Tool: {tc.function.name}({args})")

            result = execute_tool(tc.function.name, args)

            if verbose:
                logger.info(f"  Result preview: {result[:200]}")

            messages.append(
                {"role": "tool", "tool_call_id": tc.id, "content": result}
            )
    else:
        html_output = (
            "<html><body><h1>Error: agent exceeded 20 iterations.</h1></body></html>"
        )

    match = re.search(
        r"<!DOCTYPE html>.*?</html>", html_output, re.DOTALL | re.IGNORECASE
    )
    if match:
        html_output = match.group(0)

    return {"html": html_output, "panel_count": len(kpis)}
