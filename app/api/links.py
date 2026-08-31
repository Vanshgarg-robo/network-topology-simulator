"""Link management endpoints."""

from fastapi import APIRouter, Depends, status

from app.dependencies import get_link_service
from app.schemas.link_schemas import (
    LinkCreate,
    LinkListResponse,
    LinkResponse,
)
from app.services.link_service import LinkService

router = APIRouter()


@router.get(
    "",
    response_model=LinkListResponse,
    summary="List all links",
    description="Retrieve all network links and their active/down status.",
)
def list_links(
    link_service: LinkService = Depends(get_link_service),
) -> LinkListResponse:
    """List all registered network connections."""
    links = link_service.list_links()
    return LinkListResponse(
        links=[LinkResponse.model_validate(l) for l in links],
        count=len(links),
    )


@router.post(
    "",
    response_model=LinkResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new link",
    description="Establish an undirected link between two existing nodes.",
)
def create_link(
    payload: LinkCreate,
    link_service: LinkService = Depends(get_link_service),
) -> LinkResponse:
    """Create a new bidirectional link between two nodes."""
    link = link_service.create_link(
        source_node_id=payload.source_node_id,
        destination_node_id=payload.destination_node_id,
    )
    return LinkResponse.model_validate(link)


@router.delete(
    "/{link_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a link",
    description="Remove a network link between two nodes.",
)
def delete_link(
    link_id: str,
    link_service: LinkService = Depends(get_link_service),
) -> None:
    """Delete a link by ID."""
    link_service.delete_link(link_id)


@router.post(
    "/{link_id}/enable",
    response_model=LinkResponse,
    summary="Enable a link",
    description="Restore an inactive link to the active routing graph.",
)
def enable_link(
    link_id: str,
    link_service: LinkService = Depends(get_link_service),
) -> LinkResponse:
    """Set link status to ACTIVE."""
    link = link_service.enable_link(link_id)
    return LinkResponse.model_validate(link)


@router.post(
    "/{link_id}/disable",
    response_model=LinkResponse,
    summary="Disable a link",
    description="Simulate a link cut/failure by setting its status to DOWN.",
)
def disable_link(
    link_id: str,
    link_service: LinkService = Depends(get_link_service),
) -> LinkResponse:
    """Set link status to DOWN."""
    link = link_service.disable_link(link_id)
    return LinkResponse.model_validate(link)
