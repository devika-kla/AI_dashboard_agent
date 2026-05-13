from services.spec_generator import generate_dashboard_spec
from services.sql_executor import run_widget_queries
import logging

logger = logging.getLogger(__name__)


def build_dashboard(kpis: list[str]):
    logger.info("Starting dashboard generation")

    logger.info(f"KPI list: {kpis}")
    spec = generate_dashboard_spec(kpis)

    spec = run_widget_queries(spec)
    logger.info("LLM response received")
    return spec