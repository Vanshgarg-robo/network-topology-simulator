"""Unit tests for NodeService."""

import pytest

from app.core.exceptions import DuplicateNodeError, NodeNotFoundError
from app.models.enums import NodeStatus
from app.services.node_service import NodeService


def test_create_node(node_service: NodeService) -> None:
    """Test standard node creation."""
    node = node_service.create_node("Router1")
    assert node.name == "Router1"
    assert node.status == NodeStatus.ONLINE
    assert node.id is not None


def test_create_duplicate_node_error(node_service: NodeService) -> None:
    """Test duplicate node name raises DuplicateNodeError."""
    node_service.create_node("Router1")
    with pytest.raises(DuplicateNodeError):
        node_service.create_node("Router1")


def test_get_node(node_service: NodeService) -> None:
    """Test retrieving node by ID."""
    node = node_service.create_node("Router1")
    fetched = node_service.get_node(node.id)
    assert fetched.id == node.id
    assert fetched.name == "Router1"


def test_get_node_not_found(node_service: NodeService) -> None:
    """Test lookup with invalid ID raises NodeNotFoundError."""
    with pytest.raises(NodeNotFoundError):
        node_service.get_node("non-existent-id")


def test_get_node_by_name(node_service: NodeService) -> None:
    """Test lookup by node name."""
    node = node_service.create_node("SwitchA")
    found = node_service.get_node_by_name("SwitchA")
    assert found is not None
    assert found.id == node.id

    not_found = node_service.get_node_by_name("Unknown")
    assert not_found is None


def test_list_nodes(node_service: NodeService) -> None:
    """Test listing all nodes."""
    assert len(node_service.list_nodes()) == 0
    node_service.create_node("Node1")
    node_service.create_node("Node2")
    assert len(node_service.list_nodes()) == 2


def test_update_node(node_service: NodeService) -> None:
    """Test updating node name."""
    node = node_service.create_node("OldName")
    updated = node_service.update_node(node.id, name="NewName")
    assert updated.name == "NewName"


def test_update_node_duplicate_name_error(node_service: NodeService) -> None:
    """Test updating to an already taken name raises DuplicateNodeError."""
    node1 = node_service.create_node("Node1")
    node_service.create_node("Node2")
    with pytest.raises(DuplicateNodeError):
        node_service.update_node(node1.id, name="Node2")


def test_delete_node(node_service: NodeService) -> None:
    """Test deleting node by ID."""
    node = node_service.create_node("Node1")
    node_service.delete_node(node.id)
    with pytest.raises(NodeNotFoundError):
        node_service.get_node(node.id)


def test_delete_node_not_found(node_service: NodeService) -> None:
    """Test deleting non-existent node raises NodeNotFoundError."""
    with pytest.raises(NodeNotFoundError):
        node_service.delete_node("bad-id")


def test_enable_disable_node(node_service: NodeService) -> None:
    """Test toggling node status between online and offline."""
    node = node_service.create_node("Node1")
    assert node.status == NodeStatus.ONLINE

    disabled = node_service.disable_node(node.id)
    assert disabled.status == NodeStatus.OFFLINE
    assert disabled.cpu_usage == 0.0

    enabled = node_service.enable_node(node.id)
    assert enabled.status == NodeStatus.ONLINE
