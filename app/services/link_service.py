"""Link service implementation.

Handles business logic, graph construction, and thread-safe in-memory state management for links.
"""

import threading
from typing import Optional

from app.core.exceptions import (
    DuplicateLinkError,
    LinkNotFoundError,
    NodeNotFoundError,
    SimulatorError,
)
from app.core.logger import get_logger
from app.models.link import Link
from app.services.node_service import NodeService
from app.simulation.path_finder import PathFinder

logger = get_logger("service.link")


class LinkService:
    """Service managing link lifecycle, network connectivity, and adjacency."""

    def __init__(self, node_service: NodeService) -> None:
        self._node_service = node_service
        self._links: dict[str, Link] = {}  # id -> Link
        self._lock = threading.Lock()

    def create_link(self, source_node_id: str, destination_node_id: str) -> Link:
        """Create and store a new link between two existing nodes.

        Args:
            source_node_id: ID of the source node.
            destination_node_id: ID of the destination node.

        Returns:
            The created Link instance.

        Raises:
            NodeNotFoundError: If source or destination node does not exist.
            SimulatorError: If attempting to link a node to itself.
            DuplicateLinkError: If a link already exists between these nodes.
        """
        if source_node_id == destination_node_id:
            raise SimulatorError(
                message="Cannot create self-loop link",
                detail=f"Source and destination cannot both be '{source_node_id}'",
            )

        # Validate nodes exist
        self._node_service.get_node(source_node_id)
        self._node_service.get_node(destination_node_id)

        with self._lock:
            for link in self._links.values():
                if (
                    link.source_node_id == source_node_id
                    and link.destination_node_id == destination_node_id
                ) or (
                    link.source_node_id == destination_node_id
                    and link.destination_node_id == source_node_id
                ):
                    logger.warning(
                        "Attempted to create duplicate link: %s <-> %s",
                        source_node_id,
                        destination_node_id,
                    )
                    raise DuplicateLinkError(source=source_node_id, destination=destination_node_id)

            link = Link(
                source_node_id=source_node_id,
                destination_node_id=destination_node_id,
            )
            self._links[link.id] = link
            logger.info(
                "Link created: id=%s, %s <-> %s",
                link.id,
                source_node_id,
                destination_node_id,
            )
            return link

    def get_link(self, link_id: str) -> Link:
        """Retrieve a link by its ID."""
        with self._lock:
            link = self._links.get(link_id)
            if not link:
                logger.warning("Link not found: id=%s", link_id)
                raise LinkNotFoundError(link_id=link_id)
            return link

    def list_links(self) -> list[Link]:
        """Retrieve all registered links."""
        with self._lock:
            return list(self._links.values())

    def delete_link(self, link_id: str) -> None:
        """Delete a link from storage."""
        with self._lock:
            if link_id not in self._links:
                raise LinkNotFoundError(link_id=link_id)
            link = self._links.pop(link_id)
            logger.info(
                "Link deleted: id=%s, %s <-> %s",
                link.id,
                link.source_node_id,
                link.destination_node_id,
            )

    def delete_links_for_node(self, node_id: str) -> list[str]:
        """Delete all links connected to a specific node (cascade cleanup)."""
        deleted_ids: list[str] = []
        with self._lock:
            to_delete = [
                lid for lid, link in self._links.items()
                if link.source_node_id == node_id or link.destination_node_id == node_id
            ]
            for lid in to_delete:
                del self._links[lid]
                deleted_ids.append(lid)
        if deleted_ids:
            logger.info("Cleaned up %d links connected to deleted node %s", len(deleted_ids), node_id)
        return deleted_ids

    def enable_link(self, link_id: str) -> Link:
        """Enable a downed link."""
        with self._lock:
            link = self._links.get(link_id)
            if not link:
                raise LinkNotFoundError(link_id=link_id)
            link.enable()
            logger.info("Link enabled: id=%s", link.id)
            return link

    def disable_link(self, link_id: str) -> Link:
        """Disable an active link."""
        with self._lock:
            link = self._links.get(link_id)
            if not link:
                raise LinkNotFoundError(link_id=link_id)
            link.disable()
            logger.info("Link disabled: id=%s", link.id)
            return link

    def get_active_adjacency_graph(self) -> dict[str, list[str]]:
        """Build the adjacency graph for all currently active links."""
        with self._lock:
            edges = [
                (link.source_node_id, link.destination_node_id)
                for link in self._links.values()
                if link.is_active
            ]
            return PathFinder.build_adjacency_graph(edges)

    def clear(self) -> None:
        """Clear all stored links (primarily for testing)."""
        with self._lock:
            self._links.clear()
