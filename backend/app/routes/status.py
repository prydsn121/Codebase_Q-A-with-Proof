from fastapi import APIRouter
from sqlalchemy import text
from app.database import engine
from app.config import settings

router = APIRouter(prefix="/status", tags=["Status"])


@router.get("/")
def system_status():

    # -------------------------
    # Database Health Check
    # -------------------------
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "error"

    # -------------------------
    # LLM / Mode Check
    # -------------------------
    if not settings.USE_OPENAI:
        llm_status = "disabled (local mode)"
    else:
        try:
            from openai import OpenAI

            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            client.models.list()
            llm_status = "ok"
        except Exception:
            llm_status = "error"

    return {
        "backend": "ok",
        "database": db_status,
        "llm": llm_status,
        "mode": "openai" if settings.USE_OPENAI else "local"
    }
