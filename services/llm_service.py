"""LLM interaction service with centralized prompt execution."""

from langchain_openai import ChatOpenAI

from core.prompts import (
    build_dashboard_html_prompt,
    build_generate_insight_prompt,
    build_generate_questions_prompt,
)
from core.utils import clean_llm_text
from db.connection import get_llm


class LLMService:
    """Wrapper around ChatOpenAI to centralize prompt invocation."""

    def __init__(self, llm: ChatOpenAI | None = None):
        self._llm = llm or get_llm()

    def generate_dashboard_questions(self, query: str) -> str:
        prompt = build_generate_questions_prompt(query)
        return self._llm.invoke(prompt).content

    def generate_insight(self, input_text: str) -> str:
        prompt = build_generate_insight_prompt(input_text)
        return self._llm.invoke(prompt).content

    def build_dashboard_html(self, widgets_json: str) -> str:
        prompt = build_dashboard_html_prompt(widgets_json)
        return clean_llm_text(self._llm.invoke(prompt).content)

    @property
    def llm(self) -> ChatOpenAI:
        return self._llm
