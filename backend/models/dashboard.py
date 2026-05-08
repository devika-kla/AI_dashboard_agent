from pydantic import BaseModel
from typing import Optional


class DashboardRequest(BaseModel):
    kpis: list[str]
    verbose: bool = False


class DashboardResponse(BaseModel):
    html: str
    panel_count: int
    execution_time_ms: int
