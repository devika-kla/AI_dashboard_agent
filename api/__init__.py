"""API layer package."""

from fastapi import APIRouter
from api.query import router as query_router
from api.tables import router as tables_router
from api.health import router as health_router

api_router = APIRouter()

api_router.include_router(query_router, prefix="/query", tags=["query"])
api_router.include_router(tables_router, prefix="/tables", tags=["tables"])
api_router.include_router(health_router, prefix="/health", tags=["health"])