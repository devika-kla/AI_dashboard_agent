from langchain_openai import ChatOpenAI

from config import settings
import langchain

langchain.verbose = True

llm = ChatOpenAI(
    model=settings.OPENAI_MODEL,
    temperature=0,
    openai_api_key=settings.OPENAI_API_KEY,
)