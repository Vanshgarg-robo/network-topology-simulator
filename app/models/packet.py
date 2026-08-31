"""Packet domain model.

Represents a data packet transmitted across the simulated network.
"""

import uuid
from datetime import datetime, timezone

from app.models.enums import DropReason, PacketStatus


class Packet:
    """A network packet in the simulation.

    Attributes:
        id: Unique identifier (UUID4).
        sequence: Monotonically increasing sequence number.
        source_node_id: ID of the originating node.
        destination_node_id: ID of the target node.
        payload: Packet data payload.
        status: Current lifecycle status.
        drop_reason: Reason for dropping, if applicable.
        path: Ordered list of node IDs traversed.
        latency: Simulated transmission latency in milliseconds.
        created_at: Timestamp when the packet was created.
    """

    def __init__(
        self,
        sequence: int,
        source_node_id: str,
        destination_node_id: str,
        payload: str,
    ) -> None:
        self.id: str = str(uuid.uuid4())
        self.sequence: int = sequence
        self.source_node_id: str = source_node_id
        self.destination_node_id: str = destination_node_id
        self.payload: str = payload
        self.status: PacketStatus = PacketStatus.CREATED
        self.drop_reason: DropReason | None = None
        self.path: list[str] = []
        self.latency: float = 0.0
        self.created_at: datetime = datetime.now(timezone.utc)

    def mark_delivered(self, path: list[str], latency: float) -> None:
        """Mark the packet as successfully delivered."""
        self.status = PacketStatus.DELIVERED
        self.path = path
        self.latency = latency

    def mark_dropped(self, reason: DropReason) -> None:
        """Mark the packet as dropped with a specific reason."""
        self.status = PacketStatus.DROPPED
        self.drop_reason = reason

    @property
    def is_delivered(self) -> bool:
        """Check whether the packet was delivered."""
        return self.status == PacketStatus.DELIVERED

    @property
    def is_dropped(self) -> bool:
        """Check whether the packet was dropped."""
        return self.status == PacketStatus.DROPPED

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Packet):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        route = " -> ".join(self.path) if self.path else "N/A"
        return (
            f"Packet(id={self.id!r}, seq={self.sequence}, "
            f"{self.source_node_id}->{self.destination_node_id}, "
            f"status={self.status.value}, path={route}, "
            f"latency={self.latency}ms)"
        )
