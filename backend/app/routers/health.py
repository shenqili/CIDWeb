from fastapi import APIRouter

from ..config import get_settings
from ..db import check_database
from ..schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def get_health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(status="ok", app_env=settings.app_env, database=check_database())
