from fastapi import APIRouter, HTTPException
from core.dependencies import get_sql_service

router = APIRouter()

@router.get("/")
def list_tables():
    sql_service = get_sql_service()
    tables = sql_service.list_tables()
    return {"tables": tables, "count": len(tables)}


@router.get("/schema/{table_name}")
def get_table_schema(table_name: str):
    sql_service = get_sql_service()
    try:
        info = sql_service.get_table_schema(table_name)
        return {"table": table_name, "schema": info}
    except Exception as error:
        raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found: {error}")
