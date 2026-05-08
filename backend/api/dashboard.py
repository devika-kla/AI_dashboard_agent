import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from fastapi import APIRouter, HTTPException
from models.dashboard import DashboardRequest, DashboardResponse
from services.dashboard import generate_dashboard

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/healthz", tags=["health"])
async def health_check():
    return {"status": "ok"}


@router.post("/dashboard", response_model=DashboardResponse, tags=["dashboard"])
async def dashboard_endpoint(request: DashboardRequest):
    try:
        return await generate_dashboard(request)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Dashboard generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
