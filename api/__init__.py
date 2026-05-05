"""API layer package."""

from fastapi import APIRouter
from api.dashboard import router as dashboard_router
from api.tables import router as tables_router
from api.health import router as health_router

api_router = APIRouter()

api_router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(tables_router, prefix="/tables", tags=["tables"])
api_router.include_router(health_router, prefix="/health", tags=["health"])