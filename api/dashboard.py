from fastapi import APIRouter
from pydantic import BaseModel
import logging
from services.dashboard_service import build_dashboard

logger = logging.getLogger(__name__)

router = APIRouter()


class DashboardRequest(BaseModel):
    kpis: list[str]


@router.post("/generate-dashboard")
def generate_dashboard(request: DashboardRequest):
    dashboard = build_dashboard(request.kpis)
    logger.info("Dashboard generation completed - Response: %s", dashboard)

    return dashboard