import json
from langgraph.graph import StateGraph, END
from PIL import Image as PILImage
from io import BytesIO
import logging

from core.state import DashboardState
from core.prompts import DASHBOARD_SPEC_PROMPT
from core.llm import llm, parse_llm_json
from services.query_service import execute_query


logger = logging.getLogger(__name__)

# =====================================================
# NODE 1 - Generate Dashboard Spec
# =====================================================


def generate_dashboard_spec(state: DashboardState):

    try:
        logger.info("generate_dashboard_spec called with KPIs: %s", state["kpis"])
        kpis = ", ".join(state["kpis"])
        prompt = DASHBOARD_SPEC_PROMPT.format(schema=state["schema"], kpis=kpis)
        response = llm.invoke(prompt)
        dashboard = parse_llm_json(response.content)
        logger.info("Dashboard spec generated successfully")
        logger.info("Dashboard spec: %s", dashboard)

        return {"dashboard": dashboard, "error": None}

    except json.JSONDecodeError as e:
        logger.error("LLM returned invalid JSON: %s", e)
        return {"error": f"LLM returned invalid JSON: {e}"}
    except Exception as e:
        logger.error("Spec generation failed: %s", e)
        return {"error": f"Spec generation failed: {e}"}


# =====================================================
# NODE 2 - Execute SQL
# =====================================================


def execute_dashboard_queries(state: DashboardState):
    try:
        logger.info("execute_dashboard_queries called")
        dashboard = state["dashboard"]
        for section in dashboard["sections"]:
            for widget in section["widgets"]:
                sql = widget["sql"]
                data = execute_query(sql)
                widget["data"] = data

        logger.info("Dashboard queries executed successfully")
        logger.info("Dashboard data: %s", dashboard)
        return {"dashboard": dashboard, "error": None}
    except Exception as e:
        logger.error("Query execution failed: %s", e)   
        return {"error": f"Query execution failed: {e}"}


# =====================================================
# ROUTING — Skip execution if spec generation failed
# =====================================================
def should_execute(state: DashboardState) -> str:
    logger.info("should_execute called. Current state error: %s", state.get("error"))
    return "execute_queries" if not state.get("error") else "end"


# =====================================================
# BUILD GRAPH
# =====================================================

builder = StateGraph(DashboardState)

builder.add_node("generate_dashboard_spec", generate_dashboard_spec)
builder.add_node("execute_dashboard_queries", execute_dashboard_queries)
builder.set_entry_point("generate_dashboard_spec")
builder.add_conditional_edges(
    "generate_dashboard_spec",
    should_execute,
    {
        "execute": "execute_dashboard_queries",
        "end": END
    })
builder.add_edge("execute_dashboard_queries", END)
graph = builder.compile()

#Get the graph structure and visualize it
img_data = graph.get_graph().draw_mermaid_png()
image = PILImage.open(BytesIO(img_data))
image.save("langgraph_flow.png")
print("Graph saved as langgraph_flow.png")
