"""Node management endpoints."""

from fastapi import APIRouter, Depends, status

from app.dependencies import get_link_service, get_node_service
from app.schemas.node_schemas import (
    NodeCreate,
    NodeListResponse,
    NodeResponse,
    NodeUpdate,
)
from app.services.link_service import LinkService
from app.services.node_service import NodeService

router = APIRouter()


@router.get(
    "",
    response_model=NodeListResponse,
    summary="List all nodes",
    description="Retrieve all network nodes and their current operational status.",
)
def list_nodes(
    node_service: NodeService = Depends(get_node_service),
) -> NodeListResponse:
    """List all registered network nodes."""
    nodes = node_service.list_nodes()
    return NodeListResponse(
        nodes=[NodeResponse.model_validate(n) for n in nodes],
        count=len(nodes),
    )


@router.get(
    "/{node_id}",
    response_model=NodeResponse,
    summary="Get node by ID",
    description="Retrieve detailed information for a specific node by its identifier.",
)
def get_node(
    node_id: str,
    node_service: NodeService = Depends(get_node_service),
) -> NodeResponse:
    """Fetch a single node by its ID."""
    node = node_service.get_node(node_id)
    return NodeResponse.model_validate(node)


@router.post(
    "",
    response_model=NodeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new node",
    description="Register a new node in the network simulator with an initial online state.",
)
def create_node(
    payload: NodeCreate,
    node_service: NodeService = Depends(get_node_service),
) -> NodeResponse:
    """Create a new network node."""
    node = node_service.create_node(name=payload.name)
    return NodeResponse.model_validate(node)


@router.put(
    "/{node_id}",
    response_model=NodeResponse,
    summary="Update a node",
    description="Modify the configuration or name of an existing node.",
)
def update_node(
    node_id: str,
    payload: NodeUpdate,
    node_service: NodeService = Depends(get_node_service),
) -> NodeResponse:
    """Update node metadata."""
    node = node_service.update_node(node_id=node_id, name=payload.name)
    return NodeResponse.model_validate(node)


@router.delete(
    "/{node_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a node",
    description="Remove a node and automatically clean up any connected links.",
)
def delete_node(
    node_id: str,
    node_service: NodeService = Depends(get_node_service),
    link_service: LinkService = Depends(get_link_service),
) -> None:
    """Delete a node and cascade-remove connected links."""
    link_service.delete_links_for_node(node_id)
    node_service.delete_node(node_id)


@router.post(
    "/{node_id}/enable",
    response_model=NodeResponse,
    summary="Enable a node",
    description="Set the status of an offline node back to online.",
)
def enable_node(
    node_id: str,
    node_service: NodeService = Depends(get_node_service),
) -> NodeResponse:
    """Set node status to ONLINE."""
    node = node_service.enable_node(node_id)
    return NodeResponse.model_validate(node)


@router.post(
    "/{node_id}/disable",
    response_model=NodeResponse,
    summary="Disable a node",
    description="Simulate a node outage or failure by setting its status to offline.",
)
def disable_node(
    node_id: str,
    node_service: NodeService = Depends(get_node_service),
) -> NodeResponse:
    """Set node status to OFFLINE and reset CPU."""
    node = node_service.disable_node(node_id)
    return NodeResponse.model_validate(node)
