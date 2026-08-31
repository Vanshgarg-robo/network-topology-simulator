"""Unit tests for LinkService."""

import pytest

from app.core.exceptions import (
    DuplicateLinkError,
    LinkNotFoundError,
    NodeNotFoundError,
    SimulatorError,
)
from app.models.enums import LinkStatus
from app.services.link_service import LinkService
from app.services.node_service import NodeService


def test_create_link(node_service: NodeService, link_service: LinkService) -> None:
    """Test standard link creation."""
    n1 = node_service.create_node("NodeA")
    n2 = node_service.create_node("NodeB")

    link = link_service.create_link(n1.id, n2.id)
    assert link.source_node_id == n1.id
    assert link.destination_node_id == n2.id
    assert link.status == LinkStatus.ACTIVE


def test_create_link_self_loop_error(node_service: NodeService, link_service: LinkService) -> None:
    """Test linking a node to itself raises error."""
    n1 = node_service.create_node("NodeA")
    with pytest.raises(SimulatorError):
        link_service.create_link(n1.id, n1.id)


def test_create_link_missing_node_error(link_service: LinkService) -> None:
    """Test creating link with non-existent nodes raises NodeNotFoundError."""
    with pytest.raises(NodeNotFoundError):
        link_service.create_link("fake-1", "fake-2")


def test_create_duplicate_link_error(node_service: NodeService, link_service: LinkService) -> None:
    """Test duplicate links in either direction raise DuplicateLinkError."""
    n1 = node_service.create_node("NodeA")
    n2 = node_service.create_node("NodeB")

    link_service.create_link(n1.id, n2.id)

    # Same direction
    with pytest.raises(DuplicateLinkError):
        link_service.create_link(n1.id, n2.id)

    # Reverse direction
    with pytest.raises(DuplicateLinkError):
        link_service.create_link(n2.id, n1.id)


def test_get_link(node_service: NodeService, link_service: LinkService) -> None:
    """Test retrieving link by ID."""
    n1 = node_service.create_node("NodeA")
    n2 = node_service.create_node("NodeB")
    link = link_service.create_link(n1.id, n2.id)

    fetched = link_service.get_link(link.id)
    assert fetched.id == link.id


def test_get_link_not_found(link_service: LinkService) -> None:
    """Test get_link with invalid ID raises LinkNotFoundError."""
    with pytest.raises(LinkNotFoundError):
        link_service.get_link("non-existent-link")


def test_delete_link(node_service: NodeService, link_service: LinkService) -> None:
    """Test deleting link removes it."""
    n1 = node_service.create_node("NodeA")
    n2 = node_service.create_node("NodeB")
    link = link_service.create_link(n1.id, n2.id)

    link_service.delete_link(link.id)
    with pytest.raises(LinkNotFoundError):
        link_service.get_link(link.id)


def test_delete_links_for_node_cascade(node_service: NodeService, link_service: LinkService) -> None:
    """Test cascade deletion of links when a node is removed."""
    n1 = node_service.create_node("NodeA")
    n2 = node_service.create_node("NodeB")
    n3 = node_service.create_node("NodeC")

    l1 = link_service.create_link(n1.id, n2.id)
    l2 = link_service.create_link(n1.id, n3.id)
    l3 = link_service.create_link(n2.id, n3.id)

    deleted = link_service.delete_links_for_node(n1.id)
    assert len(deleted) == 2
    assert l1.id in deleted and l2.id in deleted

    remaining = link_service.list_links()
    assert len(remaining) == 1
    assert remaining[0].id == l3.id


def test_enable_disable_link(node_service: NodeService, link_service: LinkService) -> None:
    """Test toggling link status."""
    n1 = node_service.create_node("NodeA")
    n2 = node_service.create_node("NodeB")
    link = link_service.create_link(n1.id, n2.id)

    disabled = link_service.disable_link(link.id)
    assert disabled.status == LinkStatus.DOWN

    graph = link_service.get_active_adjacency_graph()
    assert n1.id not in graph or n2.id not in graph.get(n1.id, [])

    enabled = link_service.enable_link(link.id)
    assert enabled.status == LinkStatus.ACTIVE
    graph2 = link_service.get_active_adjacency_graph()
    assert n2.id in graph2[n1.id]
