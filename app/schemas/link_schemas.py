"""Pydantic schemas for Link API request/response validation."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import LinkStatus


class LinkCreate(BaseModel):
    """Schema for creating a new link between two nodes."""

    source_node_id: str = Field(
        ...,
        min_length=1,
        description="ID of the source node",
    )
    destination_node_id: str = Field(
        ...,
        min_length=1,
        description="ID of the destination node",
    )


class LinkResponse(BaseModel):
    """Schema for link API responses."""

    id: str = Field(..., description="Unique link identifier")
    source_node_id: str = Field(..., description="Source node ID")
    destination_node_id: str = Field(..., description="Destination node ID")
    status: LinkStatus = Field(..., description="Operational status")
    created_at: datetime = Field(..., description="Creation timestamp")

    model_config = {"from_attributes": True}


class LinkListResponse(BaseModel):
    """Schema for listing multiple links."""

    links: list[LinkResponse] = Field(..., description="List of links")
    count: int = Field(..., description="Total number of links")
