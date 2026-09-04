import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.database import engine
from app.schemas.health import ReadyRead

router = APIRouter(tags=["system"])
logger = logging.getLogger(__name__)


@router.get(
    "/ready",
    response_model=ReadyRead,
    responses={503: {"description": "Database unavailable"}},
)
def ready():
    """Readiness probe. Returns 200 only if the DB accepts a trivial query."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:
        logger.warning("readiness check failed: %s", exc)
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "database": "unavailable"},
        )
    return ReadyRead(status="ready", database="connected")
