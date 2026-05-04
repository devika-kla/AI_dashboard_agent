"""Pydantic schemas for API request and response payloads."""

from typing import Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------


class DashboardQueryRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=5,
        description="Natural language question to build a dashboard for.",
        examples=["Show me monthly sales trends and top customers"],
    )


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class Widget(BaseModel):
    """A single dashboard panel returned by the agent."""

    question: str
    chart: str  # kpi | bar | line | pie | table
    data: Any
    insight: str


class DashboardQueryResponse(BaseModel):
    html: str = Field(..., description="Complete HTML dashboard string.")
    widgets: list[Widget] = Field(
        default_factory=list,
        description="Parsed widget metadata extracted from the agent run.",
    )
    intermediate_steps: list[Any] = Field(
        default_factory=list,
        description="Raw LangChain intermediate steps (tool calls + observations).",
    )