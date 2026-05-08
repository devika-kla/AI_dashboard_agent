import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional

BASE_DIR = Path(__file__).parent

class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8"
    )
    # OpenAI
    OPENAI_API_KEY: str = "sk-your-openai-key-here"
    OPENAI_MODEL: str = "gpt-3.5-turbo"  # Free-tier friendly; swap to gpt-4o when ready
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"

    # Database
    DB_PATH: Path = BASE_DIR / "db" / "chinook.db"          # Path to your SQLite file
    DB_DOWNLOAD_URL: Optional[str] = (
    "https://github.com/lerocha/chinook-database/raw/master/"
    "ChinookDatabase/DataSources/Chinook_Sqlite.sqlite"
)
    # API
    CORS_ORIGINS: Optional[list[str]] = ["http://localhost:5173", "http://localhost:3000"]


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

OPENAI_API_KEY = settings.OPENAI_API_KEY
OPENAI_MODEL = settings.OPENAI_MODEL
OPENAI_BASE_URL = settings.OPENAI_BASE_URL
DB_PATH = settings.DB_PATH
DB_DOWNLOAD_URL = settings.DB_DOWNLOAD_URL
CORS_ORIGINS = settings.CORS_ORIGINS