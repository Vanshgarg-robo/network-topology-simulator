"""Pydantic schemas for Node API request/response validation."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import NodeStatus


class NodeCreate(BaseModel):
    """Schema for creating a new node."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="Unique alphanumeric node name",
        examples=["RouterA", "Switch-1"],
    )


class NodeUpdate(BaseModel):
    """Schema for updating an existing node."""

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="New node name",
        examples=["RouterB"],
    )


class NodeResponse(BaseModel):
    """Schema for node API responses."""

    id: str = Field(..., description="Unique node identifier")
    name: str = Field(..., description="Node name")
    status: NodeStatus = Field(..., description="Operational status")
    cpu_usage: float = Field(..., description="Current CPU usage percentage")
    created_at: datetime = Field(..., description="Creation timestamp")

    model_config = {"from_attributes": True}


class NodeListResponse(BaseModel):
    """Schema for listing multiple nodes."""

    nodes: list[NodeResponse] = Field(..., description="List of nodes")
    count: int = Field(..., description="Total number of nodes")
