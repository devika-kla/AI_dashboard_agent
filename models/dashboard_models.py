from pydantic import BaseModel
from typing import List


class Widget(BaseModel):
    title: str
    chart_type: str
    sql: str


class Section(BaseModel):
    kpi: str
    widgets: List[Widget]


class DashboardSpec(BaseModel):
    dashboard_title: str
    sections: List[Section]