"""Simulation telemetry and performance metrics endpoints."""

from fastapi import APIRouter, Depends

from app.dependencies import get_simulation_service
from app.schemas.metrics_schemas import (
    CpuMetricsResponse,
    LatencyMetricsResponse,
    StatisticsResponse,
)
from app.services.simulation_service import SimulationService

router = APIRouter()


@router.get(
    "/cpu",
    response_model=CpuMetricsResponse,
    summary="Get CPU metrics",
    description="Retrieve per-node CPU usage percentages and network average load.",
)
def get_cpu_metrics(
    simulation_service: SimulationService = Depends(get_simulation_service),
) -> CpuMetricsResponse:
    """Return CPU load metrics for all active nodes."""
    return simulation_service.get_cpu_metrics()


@router.get(
    "/latency",
    response_model=LatencyMetricsResponse,
    summary="Get latency metrics",
    description="Retrieve latency distribution for all delivered packets (average, min, max).",
)
def get_latency_metrics(
    simulation_service: SimulationService = Depends(get_simulation_service),
) -> LatencyMetricsResponse:
    """Return transmission latency distribution."""
    return simulation_service.get_latency_metrics()


@router.get(
    "/statistics",
    response_model=StatisticsResponse,
    summary="Get network statistics",
    description="Retrieve aggregated throughput summary, packet loss counts, and delivery rates.",
)
def get_statistics(
    simulation_service: SimulationService = Depends(get_simulation_service),
) -> StatisticsResponse:
    """Return global simulation statistics and success ratios."""
    return simulation_service.get_statistics()
