"""Link domain model.

Represents a directional network link between two nodes.
"""

import uuid
from datetime import datetime, timezone

from app.models.enums import LinkStatus


class Link:
    """A network link connecting two nodes.

    Attributes:
        id: Unique identifier (UUID4).
        source_node_id: ID of the source node.
        destination_node_id: ID of the destination node.
        status: Current operational status.
        created_at: Timestamp when the link was created.
    """

    def __init__(self, source_node_id: str, destination_node_id: str) -> None:
        self.id: str = str(uuid.uuid4())
        self.source_node_id: str = source_node_id
        self.destination_node_id: str = destination_node_id
        self.status: LinkStatus = LinkStatus.ACTIVE
        self.created_at: datetime = datetime.now(timezone.utc)

    def enable(self) -> None:
        """Set the link status to active."""
        self.status = LinkStatus.ACTIVE

    def disable(self) -> None:
        """Set the link status to down."""
        self.status = LinkStatus.DOWN

    @property
    def is_active(self) -> bool:
        """Check whether the link is currently active."""
        return self.status == LinkStatus.ACTIVE

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Link):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return (
            f"Link(id={self.id!r}, "
            f"{self.source_node_id}->{self.destination_node_id}, "
            f"status={self.status.value})"
        )
