"""Health and readiness check endpoints."""

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.core.config import get_settings

router = APIRouter(tags=["Health"])


class HealthResponse(BaseModel):
    """Health check response payload."""

    status: str = Field(..., examples=["healthy"])
    app_name: str = Field(..., examples=["Network Topology Simulator"])
    version: str = Field(..., examples=["1.0.0"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Service Health Check",
    description="Returns the current operational status and version of the API service.",
)
def get_health() -> HealthResponse:
    """Return service status and version metadata."""
    settings = get_settings()
    return HealthResponse(
        status="healthy",
        app_name=settings.app_name,
        version=settings.app_version,
    )
