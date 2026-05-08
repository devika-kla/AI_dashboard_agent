import sqlite3
import json
import logging
import urllib.request
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import DB_PATH, DB_DOWNLOAD_URL

logger = logging.getLogger(__name__)


def ensure_db() -> None:
    if DB_PATH.exists():
        logger.info(f"Chinook DB found at {DB_PATH}")
        return
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    logger.info("Downloading Chinook SQLite database (~9 MB)...")
    urllib.request.urlretrieve(DB_DOWNLOAD_URL, DB_PATH)
    logger.info(f"Chinook DB saved to {DB_PATH}")


def execute_tool(tool_name: str, tool_args: dict) -> str:
    db_path = str(DB_PATH)

    if tool_name == "list_tables":
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            )
            tables = [row[0] for row in cursor.fetchall()]
        return json.dumps(tables)

    if tool_name == "describe_table":
        table_name = tool_args.get("table_name", "")
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
        if not columns:
            return f"Table '{table_name}' not found."
        schema = [{"name": c[1], "type": c[2], "pk": bool(c[5])} for c in columns]
        return json.dumps(schema)

    if tool_name == "run_sql_query":
        query = tool_args.get("query", "").strip()
        if not query.upper().startswith("SELECT"):
            return "Error: Only SELECT queries are allowed."
        try:
            with sqlite3.connect(db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(query)
                rows = cursor.fetchmany(300)
            return json.dumps([dict(row) for row in rows], default=str)
        except Exception as e:
            return f"SQL Error: {str(e)}"

    return f"Unknown tool: {tool_name}"
