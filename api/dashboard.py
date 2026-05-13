"""
routers/dashboard.py

Single endpoint:

  POST /dashboard
    Body : { "kpis": ["revenue", "churn", "top customers"], "session_id": "..." }
    Returns:
      200 { "html": "...", "panel_count": N, "execution_time_ms": N }
      On error: 500 { "detail": "..." }

  GET /dashboard/preview/{session_id}
    Returns the raw HTML so the caller can open it directly in a browser
    or embed it in an <iframe>.
"""

from __future__ import annotations

import traceback
import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from core.dashboard_agent import run_dashboard
from models.agent_models import DashboardResponse, DashboardRequest
from core.utils import save_output

router = APIRouter()

# In-memory store: session_id → last HTML (for /preview)
_html_store: dict[str, str] = {}

# ── endpoints ───────────────────────────────────────────────

@router.post("/", response_model=DashboardResponse)
def create_dashboard(request: DashboardRequest):
    """
    Build a KPI dashboard from keywords.

    The agent runs three tools in sequence:
      1. kpi_planner      — maps keywords to metric definitions + chart types
      2. sql_executor     — generates + runs SQL for each panel
      3. dashboard_builder — assembles a self-contained Chart.js HTML dashboard

    Returns the full dashboard HTML plus metadata.
    To view the dashboard: open the 'html' field content in any browser,
    or use GET /dashboard/preview/{session_id} after this call.
    """
    try:
        result = run_dashboard(
            kpis=request.kpis,
            verbose=request.verbose,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={"error": str(exc), "trace": traceback.format_exc()[-2000:]},
        )

    # Store HTML for preview endpoint
    if request.session_id and result.get("html"):
        _html_store[request.session_id] = result["html"]
     
    # save outputs
    save_output(request.session_id, request, result)
    
    return DashboardResponse(
        html=result["html"],
        panel_count=result["panel_count"],
        execution_time_ms=result["execution_time_ms"],
        session_id=request.session_id,
    )


@router.get("/preview/{session_id}", response_class=HTMLResponse)
def preview_dashboard(session_id: str):
    """
    Return the last dashboard HTML for a session as a raw HTML response.
    Open this URL in a browser to see the rendered dashboard.

    Example: http://localhost:8000/dashboard/preview/user-abc-123
    """
    html = _html_store.get(session_id)
    if not html:
        raise HTTPException(
            status_code=404,
            detail=f"No dashboard found for session '{session_id}'. "
                   f"Call POST /dashboard first with the same session_id.",
        )
    return HTMLResponse(content=html)