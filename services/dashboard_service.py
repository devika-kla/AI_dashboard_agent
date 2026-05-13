from core.graph import graph
from services.schema_service import get_schema
import logging

logger = logging.getLogger(__name__)


def build_dashboard(kpis: list[str]):

    initial_state = {
        "kpis": kpis,
        "schema": get_schema(),
        "dashboard": {},
        "error": None,
    }

    result = graph.invoke(initial_state)

    if result["error"]:
        logger.error("Dashboard generation failed: %s", result["error"])
    else:
        return result["dashboard"]
