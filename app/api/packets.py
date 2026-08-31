"""Packet transmission and history endpoints."""

from fastapi import APIRouter, Depends, status

from app.dependencies import get_packet_service
from app.schemas.packet_schemas import (
    PacketCreate,
    PacketListResponse,
    PacketResponse,
)
from app.services.packet_service import PacketService

router = APIRouter()


@router.post(
    "/send",
    response_model=PacketResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Send a packet",
    description="Transmit a packet across the network from source to destination node.",
)
def send_packet(
    payload: PacketCreate,
    packet_service: PacketService = Depends(get_packet_service),
) -> PacketResponse:
    """Send and route a packet through the simulated network topology."""
    packet = packet_service.send_packet(
        source_node_id=payload.source_node_id,
        destination_node_id=payload.destination_node_id,
        payload=payload.payload,
    )
    return PacketResponse.model_validate(packet)


@router.get(
    "",
    response_model=PacketListResponse,
    summary="List all packets",
    description="Retrieve transmission logs and status for all processed packets.",
)
def list_packets(
    packet_service: PacketService = Depends(get_packet_service),
) -> PacketListResponse:
    """Retrieve full packet transmission history."""
    packets = packet_service.list_packets()
    return PacketListResponse(
        packets=[PacketResponse.model_validate(p) for p in packets],
        count=len(packets),
    )


@router.get(
    "/{packet_id}",
    response_model=PacketResponse,
    summary="Get packet details",
    description="Retrieve routing, latency, and status details for a single packet.",
)
def get_packet(
    packet_id: str,
    packet_service: PacketService = Depends(get_packet_service),
) -> PacketResponse:
    """Fetch a packet record by its ID."""
    packet = packet_service.get_packet(packet_id)
    return PacketResponse.model_validate(packet)
