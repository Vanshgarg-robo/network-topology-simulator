"""Unit tests for PacketService."""

import pytest

from app.core.exceptions import NodeNotFoundError, PacketNotFoundError
from app.models.enums import DropReason, PacketStatus
from app.services.link_service import LinkService
from app.services.node_service import NodeService
from app.services.packet_service import PacketService


def test_send_packet_success(
    populated_network: dict,
    packet_service: PacketService,
    node_service: NodeService,
) -> None:
    """Test successful end-to-end packet transmission with route & CPU update."""
    node_a = populated_network["nodes"]["A"]
    node_e = populated_network["nodes"]["E"]

    packet = packet_service.send_packet(
        source_node_id=node_a.id,
        destination_node_id=node_e.id,
        payload="Ping E",
    )

    assert packet.status == PacketStatus.DELIVERED
    assert packet.drop_reason is None
    assert packet.latency > 0
    assert len(packet.path) >= 2
    assert packet.path[0] == node_a.id
    assert packet.path[-1] == node_e.id

    # Verify CPU workload was updated for nodes on the route
    for node_id in packet.path:
        node = node_service.get_node(node_id)
        assert node.cpu_usage > 0


def test_send_packet_source_offline(
    populated_network: dict,
    packet_service: PacketService,
    node_service: NodeService,
) -> None:
    """Test packet is dropped when source node is offline."""
    node_a = populated_network["nodes"]["A"]
    node_e = populated_network["nodes"]["E"]

    node_service.disable_node(node_a.id)

    packet = packet_service.send_packet(
        source_node_id=node_a.id,
        destination_node_id=node_e.id,
        payload="Ping from offline node",
    )

    assert packet.status == PacketStatus.DROPPED
    assert packet.drop_reason == DropReason.SOURCE_OFFLINE
    assert packet.path == []


def test_send_packet_destination_offline(
    populated_network: dict,
    packet_service: PacketService,
    node_service: NodeService,
) -> None:
    """Test packet is dropped when destination node is offline."""
    node_a = populated_network["nodes"]["A"]
    node_e = populated_network["nodes"]["E"]

    node_service.disable_node(node_e.id)

    packet = packet_service.send_packet(
        source_node_id=node_a.id,
        destination_node_id=node_e.id,
        payload="Ping to offline node",
    )

    assert packet.status == PacketStatus.DROPPED
    assert packet.drop_reason == DropReason.DESTINATION_OFFLINE
    assert packet.path == []


def test_send_packet_no_route(
    node_service: NodeService,
    link_service: LinkService,
    packet_service: PacketService,
) -> None:
    """Test packet is dropped when network islands exist (no connected path)."""
    n1 = node_service.create_node("Island1")
    n2 = node_service.create_node("Island2")

    packet = packet_service.send_packet(n1.id, n2.id, "No route message")

    assert packet.status == PacketStatus.DROPPED
    assert packet.drop_reason == DropReason.NO_ROUTE


def test_send_packet_missing_node_error(packet_service: PacketService) -> None:
    """Test sending packet with nonexistent node ID raises NodeNotFoundError."""
    with pytest.raises(NodeNotFoundError):
        packet_service.send_packet("bad-src", "bad-dst", "payload")


def test_get_packet_and_list(
    populated_network: dict,
    packet_service: PacketService,
) -> None:
    """Test listing packets and fetching single packet by ID."""
    node_a = populated_network["nodes"]["A"]
    node_b = populated_network["nodes"]["B"]

    p1 = packet_service.send_packet(node_a.id, node_b.id, "Msg 1")
    p2 = packet_service.send_packet(node_a.id, node_b.id, "Msg 2")

    packets = packet_service.list_packets()
    assert len(packets) == 2
    assert packets[0].sequence == 1
    assert packets[1].sequence == 2

    fetched = packet_service.get_packet(p1.id)
    assert fetched.id == p1.id


def test_get_packet_not_found(packet_service: PacketService) -> None:
    """Test get_packet raises PacketNotFoundError on bad ID."""
    with pytest.raises(PacketNotFoundError):
        packet_service.get_packet("non-existent-packet")
