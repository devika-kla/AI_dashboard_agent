from typing import Optional
from pydantic import BaseModel, field_validator
# ── request / response models ───────────────────────────────

class DashboardRequest(BaseModel):
    kpis: list[str]
    session_id: Optional[str] = None
    verbose: bool = False

    @field_validator("kpis")
    @classmethod
    def kpis_not_empty(cls, v: list[str]) -> list[str]:
        cleaned = [k.strip() for k in v if k.strip()]
        if not cleaned:
            raise ValueError("kpis must contain at least one non-empty keyword")
        return cleaned

    model_config = {
        "json_schema_extra": {
            "example": {
                "kpis": ["revenue", "top customers", "sales by country"],
                "session_id": "user-abc-123",
            }
        }
    }


class DashboardResponse(BaseModel):
    html: str
    panel_count: int
    execution_time_ms: int
    session_id: Optional[str] = None
