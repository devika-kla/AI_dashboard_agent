"""API layer package."""

from fastapi import APIRouter
from api.dashboard import router as dashboard_router

api_router = APIRouter()

api_router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
