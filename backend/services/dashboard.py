import time
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from models.dashboard import DashboardRequest, DashboardResponse
from core.agent import run_agent

logger = logging.getLogger(__name__)


async def generate_dashboard(request: DashboardRequest) -> DashboardResponse:
    logger.info(f"Generating dashboard for KPIs: {request.kpis}")
    start = time.time()

    result = await run_agent(
        kpis=request.kpis,
        verbose=request.verbose,
    )

    elapsed_ms = int((time.time() - start) * 1000)
    logger.info(f"Dashboard generated in {elapsed_ms}ms")

    return DashboardResponse(
        html=result["html"],
        panel_count=result["panel_count"],
        execution_time_ms=elapsed_ms,
    )
