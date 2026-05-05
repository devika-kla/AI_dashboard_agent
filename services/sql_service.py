"""Database-focused reusable business logic."""

import json
from langchain_community.utilities import SQLDatabase


class SQLService:
    """Encapsulates reusable SQL-oriented operations."""

    def __init__(self, db: SQLDatabase):
        self.db = db

    def list_tables(self) -> list[str]:
        return self.db.get_usable_table_names()

    def get_table_schema(self, table_name: str) -> str:
        return self.db.get_table_info(table_names=[table_name])

