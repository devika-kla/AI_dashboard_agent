"""Database and model client builders."""

from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI

from config import settings
from core.constants import DEFAULT_LLM_TEMPERATURE, DEFAULT_SAMPLE_ROWS


def get_database(db_path: str | None = None) -> SQLDatabase:
    target_path = db_path or settings.DB_PATH
    return SQLDatabase.from_uri(
        f"sqlite:///{target_path}",
        sample_rows_in_table_info=DEFAULT_SAMPLE_ROWS,
    )


def get_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.OPENAI_MODEL,
        temperature=DEFAULT_LLM_TEMPERATURE,
        openai_api_key=settings.OPENAI_API_KEY,
    )
