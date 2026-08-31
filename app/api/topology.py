"""Topology discovery endpoints."""

from fastapi import APIRouter, Depends

from app.dependencies import get_topology_service
from app.schemas.topology_schemas import TopologyResponse
from app.services.topology_service import TopologyService

router = APIRouter()


@router.get(
    "",
    response_model=TopologyResponse,
    summary="Get network topology",
    description="Retrieve the complete topology graph containing all nodes and links.",
)
def get_topology(
    topology_service: TopologyService = Depends(get_topology_service),
) -> TopologyResponse:
    """Return the entire network topology graph with connection statuses."""
    return topology_service.get_topology()
