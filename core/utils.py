import ast
import json
from typing import Any
import webbrowser
import tempfile


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
