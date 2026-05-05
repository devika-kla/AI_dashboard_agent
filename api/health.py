from fastapi import APIRouter
from db.connection import get_database
from config import settings

router = APIRouter()


@router.get("/")
def health_check():
    try:
        db = get_database(settings.DB_PATH)
        tables = db.get_usable_table_names()
        return {
            "status": "healthy",
            "database": settings.DB_PATH,
            "tables_found": len(tables),
            "model": settings.OPENAI_MODEL,
        }
    except Exception as error:
        return {"status": "degraded", "error": str(error)}