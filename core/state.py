from typing import TypedDict, Dict, Any, List, Optional


class DashboardState(TypedDict):
    kpis: List[str]
    schema: str
    dashboard: Dict[str, Any]
    error: Optional[str]
