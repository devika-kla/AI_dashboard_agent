"""
Configuration — loads from environment variables or .env file
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # OpenAI
    OPENAI_API_KEY: str = "sk-your-openai-key-here"
    OPENAI_MODEL: str = "gpt-3.5-turbo"  # Free-tier friendly; swap to gpt-4o when ready

    # Database
    DB_PATH: str = "db/chinook.db"           # Path to your SQLite file

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
