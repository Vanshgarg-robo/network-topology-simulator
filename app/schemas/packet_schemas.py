"""Pydantic schemas for Packet API request/response validation."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import DropReason, PacketStatus


class PacketCreate(BaseModel):
    """Schema for sending a new packet."""

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
    payload: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Packet data payload",
        examples=["Hello from RouterA"],
    )


class PacketResponse(BaseModel):
    """Schema for packet API responses."""

    id: str = Field(..., description="Unique packet identifier")
    sequence: int = Field(..., description="Packet sequence number")
    source_node_id: str = Field(..., description="Source node ID")
    destination_node_id: str = Field(..., description="Destination node ID")
    payload: str = Field(..., description="Packet data payload")
    status: PacketStatus = Field(..., description="Packet lifecycle status")
    drop_reason: DropReason | None = Field(None, description="Reason for dropping")
    path: list[str] = Field(default_factory=list, description="Node IDs traversed")
    latency: float = Field(..., description="Transmission latency in ms")
    created_at: datetime = Field(..., description="Creation timestamp")

    model_config = {"from_attributes": True}


class PacketListResponse(BaseModel):
    """Schema for listing multiple packets."""

    packets: list[PacketResponse] = Field(..., description="List of packets")
    count: int = Field(..., description="Total number of packets")
