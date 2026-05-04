"""Core dashboard agent: wires together LLM, tools, and the ReAct executor."""

from __future__ import annotations

from langchain.agents import AgentExecutor, create_react_agent
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI

from core.prompts import build_prompt
from db.connection import get_database, get_llm
from services.llm_service import LLMService
from services.tool_registry import build_tools

# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def build_agent(db_path: str | None = None) -> tuple[AgentExecutor, SQLDatabase]:
    """Construct and return the AgentExecutor together with the SQLDatabase."""
    db: SQLDatabase = get_database(db_path)
    llm: ChatOpenAI = get_llm()
    llm_service = LLMService(llm)
    all_tools = build_tools(
        db=db,
        llm=llm,
        question_generator=llm_service.generate_dashboard_questions,
        insight_generator=llm_service.generate_insight,
    )

    prompt = build_prompt(db, all_tools)

    agent = create_react_agent(llm=llm, tools=all_tools, prompt=prompt)

    executor = AgentExecutor(
        agent=agent,
        tools=all_tools,
        verbose=True,
        handle_parsing_errors=True,
        return_intermediate_steps=True,
        max_iterations=20,
    )

    return executor, db