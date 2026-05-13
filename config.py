from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4.1-mini"
    DB_PATH: str = "db/chinook.db"

    class Config:
        env_file = ".env"


settings = Settings()