from fastapi import APIRouter

from models.dashboard_models import DashboardRequest

from services.dashboard_service import build_dashboard

router = APIRouter()


@router.post("/generate-dashboard")
def generate_dashboard(request: DashboardRequest):

    dashboard = build_dashboard(request.kpis)

    return dashboard
