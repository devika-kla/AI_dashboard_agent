"""Dependency providers for API handlers."""

from __future__ import annotations

from fastapi import HTTPException

from config import settings
from core.agent import build_agent
from services.sql_service import SQLService

_agent_executor = None
_db = None


def get_agent_context():
    global _agent_executor, _db
    if _agent_executor is None or _db is None:
        try:
            _agent_executor, _db = build_agent(db_path=settings.DB_PATH)
        except Exception as error:
            raise HTTPException(
                status_code=503,
                detail=f"Agent initialization failed: {error}",
            )
    return _agent_executor, _db


def get_sql_service() -> SQLService:
    _, db = get_agent_context()
    return SQLService(db)
