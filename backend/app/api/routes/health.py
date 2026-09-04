from fastapi import APIRouter

from app.core.config import get_settings
from app.schemas.health import HealthRead

router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthRead)
def health() -> HealthRead:
    """Liveness probe. Does not touch the database."""
    settings = get_settings()
    return HealthRead(
        status="healthy",
        service=settings.service_name,
        version=settings.app_version,
    )
