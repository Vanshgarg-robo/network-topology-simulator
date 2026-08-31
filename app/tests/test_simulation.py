"""Unit tests for low-level simulation components (CPU, Latency, Packet, PathFinder)."""

from app.models.node import Node
from app.models.packet import Packet
from app.simulation.cpu_simulator import CPUSimulator
from app.simulation.latency_simulator import LatencySimulator
from app.simulation.packet_simulator import PacketSimulator
from app.simulation.path_finder import PathFinder


def test_cpu_simulator_online_node() -> None:
    """Test CPU generation within bounds for online node."""
    sim = CPUSimulator(min_usage=10, max_usage=20)
    node = Node("Node1")
    assert node.is_online

    usage = sim.generate_cpu(node)
    assert 10 <= usage <= 20

    sim.update_node_cpu(node)
    assert 10 <= node.cpu_usage <= 20


def test_cpu_simulator_offline_node() -> None:
    """Test CPU generation returns 0 for offline node."""
    sim = CPUSimulator(min_usage=10, max_usage=20)
    node = Node("Node1")
    node.disable()
    assert not node.is_online

    usage = sim.generate_cpu(node)
    assert usage == 0.0

    node.cpu_usage = 50.0
    sim.update_node_cpu(node)
    assert node.cpu_usage == 0.0


def test_latency_simulator_bounds() -> None:
    """Test LatencySimulator produces values within limits."""
    sim = LatencySimulator(min_latency_ms=15, max_latency_ms=45)
    for _ in range(50):
        lat = sim.calculate_latency("src", "dst")
        assert 15 <= lat <= 45


def test_packet_simulator_transmit() -> None:
    """Test PacketSimulator computes latency via injected LatencySimulator."""
    lat_sim = LatencySimulator(min_latency_ms=25, max_latency_ms=30)
    pkt_sim = PacketSimulator(latency_simulator=lat_sim)
    packet = Packet(sequence=1, source_node_id="A", destination_node_id="B", payload="test")

    latency = pkt_sim.transmit(packet)
    assert 25 <= latency <= 30


def test_path_finder_same_node() -> None:
    """Test pathfinding from node to itself returns single-node path."""
    graph = {"A": ["B"], "B": ["A"]}
    path = PathFinder.find_path(graph, "A", "A")
    assert path == ["A"]


def test_path_finder_simple_path() -> None:
    """Test shortest path in linear topology."""
    graph = {"A": ["B"], "B": ["A", "C"], "C": ["B"]}
    path = PathFinder.find_path(graph, "A", "C")
    assert path == ["A", "B", "C"]


def test_path_finder_multi_path_shortest() -> None:
    """Test pathfinder chooses the shortest path when multiple exist."""
    # A - B - C (2 hops) vs A - D - E - C (3 hops)
    graph = {
        "A": ["B", "D"],
        "B": ["A", "C"],
        "C": ["B", "E"],
        "D": ["A", "E"],
        "E": ["D", "C"],
    }
    path = PathFinder.find_path(graph, "A", "C")
    assert path == ["A", "B", "C"]


def test_path_finder_disconnected() -> None:
    """Test pathfinder returns None for disconnected nodes."""
    graph = {"A": ["B"], "B": ["A"], "C": ["D"], "D": ["C"]}
    path = PathFinder.find_path(graph, "A", "C")
    assert path is None


def test_build_adjacency_graph() -> None:
    """Test graph builder converts edge list to bidirectional adjacency dict."""
    edges = [("A", "B"), ("B", "C")]
    graph = PathFinder.build_adjacency_graph(edges)
    assert "A" in graph and graph["A"] == ["B"]
    assert "B" in graph and "A" in graph["B"] and "C" in graph["B"]
    assert "C" in graph and graph["C"] == ["B"]
