"""Dashboard orchestration service."""

import logging
from typing import Any

from core.agent import build_agent
from core.constants import MAX_INTERMEDIATE_OUTPUT_CHARS
from core.utils import safe_python_literal, open_dashboard_in_browser
from models.agent_models import DashboardQueryResponse, Widget
from services.llm_service import LLMService

logger = logging.getLogger(__name__)


def run_dashboard_query(query: str, db_path: str | None = None) -> DashboardQueryResponse:
    """Execute the dashboard agent and map raw output to a response model."""
    executor, _ = build_agent(db_path=db_path)

    logger.info("Running dashboard agent for query: %s", query)
    result = executor.invoke({"input": query})

    html = result.get("output", "")
    intermediate_steps = _format_intermediate_steps(result.get("intermediate_steps", []))
    widgets = _extract_widgets(result.get("intermediate_steps", []))
    html =  LLMService().build_dashboard_html(widgets)

    open_dashboard_in_browser(html)

    return DashboardQueryResponse(
        html=html,
        widgets=widgets,
        intermediate_steps=intermediate_steps
    )


def _extract_widgets(intermediate_steps: list[Any]) -> list[Widget]:
    widgets: list[Widget] = []
    last_sql_data: Any = []

    for action, observation in intermediate_steps:
        tool = getattr(action, "tool", "")
        tool_input = getattr(action, "tool_input", "") or ""

        if tool == "sql_db_query":
            last_sql_data = safe_python_literal(str(observation))
            continue

        if tool == "generate_insight":
            question = _extract_question_from_tool_input(tool_input)
            insight = str(observation).strip()
            widgets.append(
                Widget(
                    question=question,
                    chart="auto",
                    data=last_sql_data,
                    insight=insight,
                )
            )

    return widgets


def _extract_question_from_tool_input(tool_input: str) -> str:
    marker = "Question:"
    if marker not in tool_input:
        return tool_input.strip()
    return tool_input.split(marker, maxsplit=1)[1].split("\n", maxsplit=1)[0].strip()


def _format_intermediate_steps(intermediate_steps: list[Any]) -> list[dict[str, Any]]:
    formatted: list[dict[str, Any]] = []
    for action, observation in intermediate_steps:
        formatted.append(
            {
                "tool": getattr(action, "tool", ""),
                "input": getattr(action, "tool_input", ""),
                "output": str(observation)[:MAX_INTERMEDIATE_OUTPUT_CHARS],
            }
        )
    return formatted
