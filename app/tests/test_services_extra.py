"""Unit tests for TopologyService and SimulationService."""

from app.models.enums import NodeStatus
from app.services.node_service import NodeService
from app.services.packet_service import PacketService
from app.services.simulation_service import SimulationService
from app.services.topology_service import TopologyService


def test_topology_service(
    populated_network: dict,
    topology_service: TopologyService,
) -> None:
    """Test topology generation returns expected node and edge counts."""
    topo = topology_service.get_topology()
    assert topo.node_count == 5
    assert topo.edge_count == 6
    assert len(topo.nodes) == 5
    assert len(topo.edges) == 6


def test_simulation_service_empty(simulation_service: SimulationService) -> None:
    """Test metrics and stats on an empty network."""
    cpu = simulation_service.get_cpu_metrics()
    assert cpu.metrics == []
    assert cpu.average_cpu == 0.0

    lat = simulation_service.get_latency_metrics()
    assert lat.metrics == []
    assert lat.average_latency == 0.0

    stats = simulation_service.get_statistics()
    assert stats.total_nodes == 0
    assert stats.total_links == 0
    assert stats.total_packets == 0
    assert stats.delivery_rate_percent == 0.0


def test_simulation_service_populated(
    populated_network: dict,
    packet_service: PacketService,
    node_service: NodeService,
    simulation_service: SimulationService,
) -> None:
    """Test metrics and statistics calculation after packet transmissions."""
    node_a = populated_network["nodes"]["A"]
    node_b = populated_network["nodes"]["B"]
    node_e = populated_network["nodes"]["E"]

    # 2 delivered packets
    packet_service.send_packet(node_a.id, node_b.id, "msg1")
    packet_service.send_packet(node_a.id, node_e.id, "msg2")

    # 1 dropped packet (disable node E first)
    node_service.disable_node(node_e.id)
    packet_service.send_packet(node_a.id, node_e.id, "msg3")

    stats = simulation_service.get_statistics()
    assert stats.total_nodes == 5
    assert stats.total_links == 6
    assert stats.total_packets == 3
    assert stats.total_sent == 3
    assert stats.total_received == 2
    assert stats.total_dropped == 1
    assert round(stats.delivery_rate_percent, 1) == 66.7

    # CPU metrics check
    cpu = simulation_service.get_cpu_metrics()
    assert len(cpu.metrics) == 5

    # Latency metrics check
    lat = simulation_service.get_latency_metrics()
    assert len(lat.metrics) == 2
    assert lat.average_latency > 0
    assert lat.min_latency <= lat.max_latency
