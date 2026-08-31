"""Node service implementation.

Handles business logic and thread-safe in-memory state management for nodes.
"""

import threading
from typing import Optional

from app.core.exceptions import DuplicateNodeError, NodeNotFoundError
from app.core.logger import get_logger
from app.models.node import Node

logger = get_logger("service.node")


class NodeService:
    """Service managing node lifecycle and storage."""

    def __init__(self) -> None:
        self._nodes: dict[str, Node] = {}  # id -> Node
        self._lock = threading.Lock()

    def create_node(self, name: str) -> Node:
        """Create and store a new node.

        Args:
            name: Human-readable unique node name.

        Returns:
            The created Node instance.

        Raises:
            DuplicateNodeError: If a node with the same name already exists.
        """
        with self._lock:
            for node in self._nodes.values():
                if node.name == name:
                    logger.warning("Attempted to create duplicate node with name '%s'", name)
                    raise DuplicateNodeError(name=name)

            node = Node(name=name)
            self._nodes[node.id] = node
            logger.info("Node created: id=%s, name=%s", node.id, node.name)
            return node

    def get_node(self, node_id: str) -> Node:
        """Retrieve a node by its ID.

        Args:
            node_id: Unique node identifier.

        Returns:
            The matching Node instance.

        Raises:
            NodeNotFoundError: If no node matches the ID.
        """
        with self._lock:
            node = self._nodes.get(node_id)
            if not node:
                logger.warning("Node not found: id=%s", node_id)
                raise NodeNotFoundError(node_id=node_id)
            return node

    def get_node_by_name(self, name: str) -> Optional[Node]:
        """Find a node by its name if present."""
        with self._lock:
            for node in self._nodes.values():
                if node.name == name:
                    return node
            return None

    def list_nodes(self) -> list[Node]:
        """Retrieve all registered nodes."""
        with self._lock:
            return list(self._nodes.values())

    def update_node(self, node_id: str, name: Optional[str] = None) -> Node:
        """Update node attributes.

        Args:
            node_id: Target node ID.
            name: Optional new node name.

        Returns:
            The updated Node instance.

        Raises:
            NodeNotFoundError: If the node does not exist.
            DuplicateNodeError: If the new name is already taken by another node.
        """
        with self._lock:
            node = self._nodes.get(node_id)
            if not node:
                raise NodeNotFoundError(node_id=node_id)

            if name is not None and name != node.name:
                for existing_node in self._nodes.values():
                    if existing_node.id != node_id and existing_node.name == name:
                        raise DuplicateNodeError(name=name)
                old_name = node.name
                node.name = name
                logger.info("Node renamed: id=%s, old=%s, new=%s", node_id, old_name, name)

            return node

    def delete_node(self, node_id: str) -> None:
        """Delete a node from storage.

        Args:
            node_id: Target node ID.

        Raises:
            NodeNotFoundError: If the node does not exist.
        """
        with self._lock:
            if node_id not in self._nodes:
                raise NodeNotFoundError(node_id=node_id)
            node = self._nodes.pop(node_id)
            logger.info("Node deleted: id=%s, name=%s", node.id, node.name)

    def enable_node(self, node_id: str) -> Node:
        """Enable an offline node.

        Args:
            node_id: Target node ID.

        Returns:
            The updated Node instance.

        Raises:
            NodeNotFoundError: If the node does not exist.
        """
        with self._lock:
            node = self._nodes.get(node_id)
            if not node:
                raise NodeNotFoundError(node_id=node_id)
            node.enable()
            logger.info("Node enabled: id=%s, name=%s", node.id, node.name)
            return node

    def disable_node(self, node_id: str) -> Node:
        """Disable an online node.

        Args:
            node_id: Target node ID.

        Returns:
            The updated Node instance.

        Raises:
            NodeNotFoundError: If the node does not exist.
        """
        with self._lock:
            node = self._nodes.get(node_id)
            if not node:
                raise NodeNotFoundError(node_id=node_id)
            node.disable()
            logger.info("Node disabled: id=%s, name=%s", node.id, node.name)
            return node

    def clear(self) -> None:
        """Clear all stored nodes (primarily for testing)."""
        with self._lock:
            self._nodes.clear()
