"""LangChain tool definitions for the dashboard agent."""

from __future__ import annotations

from collections.abc import Callable

from langchain.agents import Tool
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI

def build_tools(
    db: SQLDatabase,
    llm: ChatOpenAI,
    question_generator: Callable[[str], str],
    insight_generator: Callable[[str], str],
) -> list[Tool]:
    """Return all LangChain tools available to the dashboard agent."""

    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    base_tools = toolkit.get_tools()

    question_tool = Tool(
        name="generate_dashboard_questions",
        description=(
            "Decompose a user query into 4-6 analytical sub-questions for a dashboard. "
            "Input: the raw user query string. "
            "Returns a JSON list of objects with a 'question' key each."
        ),
        func=question_generator,
    )

    insight_tool = Tool(
        name="generate_insight",
        description=(
            "Generate a concise 1-2 sentence business insight from a dataset. "
            "Input: a string containing the analytical question and the SQL query result."
        ),
        func=insight_generator,
    )

    return base_tools + [question_tool, insight_tool]
