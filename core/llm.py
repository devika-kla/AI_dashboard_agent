from langchain_openai import ChatOpenAI
import re
import json
from config import settings

llm = ChatOpenAI(
    model=settings.OPENAI_MODEL,
    api_key=settings.OPENAI_API_KEY,
    temperature=0,
)


def parse_llm_json(content: str) -> dict:
    """Strip any markdown fences GPT sneaks in despite instructions."""
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", content.strip())
    return json.loads(cleaned)
