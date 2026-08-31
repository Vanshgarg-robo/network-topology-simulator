"""Node domain model.

Represents a network node with a unique identity, operational status,
and simulated CPU usage.
"""

import uuid
from datetime import datetime, timezone

from app.models.enums import NodeStatus


class Node:
    """A network node in the simulation.

    Attributes:
        id: Unique identifier (UUID4).
        name: Human-readable node name.
        status: Current operational status.
        cpu_usage: Simulated CPU usage percentage (0-100).
        created_at: Timestamp when the node was created.
    """

    def __init__(self, name: str) -> None:
        self.id: str = str(uuid.uuid4())
        self.name: str = name
        self.status: NodeStatus = NodeStatus.ONLINE
        self.cpu_usage: float = 0.0
        self.created_at: datetime = datetime.now(timezone.utc)

    def enable(self) -> None:
        """Set the node status to online."""
        self.status = NodeStatus.ONLINE

    def disable(self) -> None:
        """Set the node status to offline and reset CPU usage."""
        self.status = NodeStatus.OFFLINE
        self.cpu_usage = 0.0

    @property
    def is_online(self) -> bool:
        """Check whether the node is currently online."""
        return self.status == NodeStatus.ONLINE

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Node):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return (
            f"Node(id={self.id!r}, name={self.name!r}, "
            f"status={self.status.value}, cpu={self.cpu_usage}%)"
        )
