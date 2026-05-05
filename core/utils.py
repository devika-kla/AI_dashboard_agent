import ast
import json
from typing import Any
import webbrowser
import tempfile
import os
from datetime import datetime
from models.agent_models import DashboardRequest
from core.constants import OUTPUT_DIR


def clean_llm_text(value: str) -> str:
    return value.replace("```html", "").replace("```", "").strip()


def safe_python_literal(value: str) -> Any:
    try:
        return ast.literal_eval(value)
    except (ValueError, SyntaxError):
        return value
    

def open_dashboard_in_browser(html: str):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as f:
        f.write(html.encode("utf-8"))
        file_path = f.name

    webbrowser.open(f"file://{file_path}")

def clean_llm_json(output: str) -> str:
    return (
        output
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )



def _extract_json_object(text: str) -> str | None:
    """Extract the first balanced {...} JSON object from a string."""
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    for i, ch in enumerate(text[start:], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start: i + 1]
    return None

def save_output(session_id: str, request: DashboardRequest, result: dict):
    """Save request + HTML to disk"""
    try:
        # fallback if no session_id
        sid = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        base_path = os.path.join(OUTPUT_DIR, sid)
        os.makedirs(base_path, exist_ok=True)

        # save request
        with open(os.path.join(base_path, "request.json"), "w", encoding="utf-8") as f:
            json.dump({
                "kpis": request.kpis,
                "verbose": request.verbose,
                "session_id": request.session_id
            }, f, indent=2)

        # save HTML
        html = result.get("html", "")
        with open(os.path.join(base_path, "dashboard.html"), "w", encoding="utf-8") as f:
            f.write(html)

    except Exception as e:
        print(f"[WARN] Failed to save output: {e}")