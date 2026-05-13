import json

from core.llm import llm
from db.connection import SCHEMA
from core.prompts import DASHBOARD_SPEC_PROMPT



def generate_dashboard_spec(kpis: list[str]):
    prompt = DASHBOARD_SPEC_PROMPT.format(
        schema=SCHEMA,
        kpis=", ".join(kpis),
    )

    response = llm.invoke(prompt)

    content = response.content.strip()

    content = content.replace("```json", "")
    content = content.replace("```", "")

    return json.loads(content)