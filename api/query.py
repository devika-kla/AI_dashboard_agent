"""Dashboard query endpoint."""

from fastapi import APIRouter, HTTPException

from models.agent_models import DashboardQueryRequest, DashboardQueryResponse
from services.dashboard_service import run_dashboard_query

router = APIRouter()


@router.post("/", response_model=DashboardQueryResponse)
def query_dashboard(request: DashboardQueryRequest) -> DashboardQueryResponse:
    """Accept a natural language query and return an HTML dashboard.

    The agent will:
    1. Break the query into analytical sub-questions.
    2. Execute SQL for each question.
    3. Choose the best visualization per question.
    4. Generate business insights.
    5. Return a fully rendered HTML dashboard.
    """
    try:
        return run_dashboard_query(request.query)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc