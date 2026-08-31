"""Pytest fixtures for unit and integration testing."""

from typing import Generator

import pytest
from fastapi.testclient import TestClient

from app.dependencies import (
    get_cpu_simulator,
    get_latency_simulator,
    get_link_service,
    get_node_service,
    get_packet_service,
    get_packet_simulator,
    get_simulation_service,
    get_topology_service,
)
from app.main import create_app
from app.services.link_service import LinkService
from app.services.node_service import NodeService
from app.services.packet_service import PacketService
from app.services.simulation_service import SimulationService
from app.services.topology_service import TopologyService
from app.simulation.cpu_simulator import CPUSimulator
from app.simulation.latency_simulator import LatencySimulator
from app.simulation.packet_simulator import PacketSimulator


@pytest.fixture
def cpu_simulator() -> CPUSimulator:
    """Provide isolated CPUSimulator fixture."""
    return CPUSimulator()


@pytest.fixture
def latency_simulator() -> LatencySimulator:
    """Provide isolated LatencySimulator fixture."""
    return LatencySimulator()


@pytest.fixture
def packet_simulator(latency_simulator: LatencySimulator) -> PacketSimulator:
    """Provide isolated PacketSimulator fixture."""
    return PacketSimulator(latency_simulator=latency_simulator)


@pytest.fixture
def node_service() -> NodeService:
    """Provide isolated NodeService with clean in-memory state."""
    service = NodeService()
    service.clear()
    return service


@pytest.fixture
def link_service(node_service: NodeService) -> LinkService:
    """Provide isolated LinkService."""
    service = LinkService(node_service=node_service)
    service.clear()
    return service


@pytest.fixture
def packet_service(
    node_service: NodeService,
    link_service: LinkService,
    packet_simulator: PacketSimulator,
    cpu_simulator: CPUSimulator,
) -> PacketService:
    """Provide isolated PacketService."""
    service = PacketService(
        node_service=node_service,
        link_service=link_service,
        packet_simulator=packet_simulator,
        cpu_simulator=cpu_simulator,
    )
    service.clear()
    return service


@pytest.fixture
def topology_service(
    node_service: NodeService,
    link_service: LinkService,
) -> TopologyService:
    """Provide isolated TopologyService."""
    return TopologyService(
        node_service=node_service,
        link_service=link_service,
    )


@pytest.fixture
def simulation_service(
    node_service: NodeService,
    link_service: LinkService,
    packet_service: PacketService,
) -> SimulationService:
    """Provide isolated SimulationService."""
    return SimulationService(
        node_service=node_service,
        link_service=link_service,
        packet_service=packet_service,
    )


@pytest.fixture
def populated_network(
    node_service: NodeService,
    link_service: LinkService,
) -> dict:
    """Set up a standard 5-node test topology (A, B, C, D, E).

    Topology:
        A --- B --- E
        |     |     |
        C --- D ----+
    """
    node_a = node_service.create_node("NodeA")
    node_b = node_service.create_node("NodeB")
    node_c = node_service.create_node("NodeC")
    node_d = node_service.create_node("NodeD")
    node_e = node_service.create_node("NodeE")

    link_ab = link_service.create_link(node_a.id, node_b.id)
    link_be = link_service.create_link(node_b.id, node_e.id)
    link_ac = link_service.create_link(node_a.id, node_c.id)
    link_cd = link_service.create_link(node_c.id, node_d.id)
    link_bd = link_service.create_link(node_b.id, node_d.id)
    link_de = link_service.create_link(node_d.id, node_e.id)

    return {
        "nodes": {
            "A": node_a,
            "B": node_b,
            "C": node_c,
            "D": node_d,
            "E": node_e,
        },
        "links": {
            "AB": link_ab,
            "BE": link_be,
            "AC": link_ac,
            "CD": link_cd,
            "BD": link_bd,
            "DE": link_de,
        },
    }


@pytest.fixture
def client(
    node_service: NodeService,
    link_service: LinkService,
    packet_service: PacketService,
    topology_service: TopologyService,
    simulation_service: SimulationService,
) -> Generator[TestClient, None, None]:
    """Provide a FastAPI TestClient with injected test services."""
    app = create_app()

    app.dependency_overrides[get_node_service] = lambda: node_service
    app.dependency_overrides[get_link_service] = lambda: link_service
    app.dependency_overrides[get_packet_service] = lambda: packet_service
    app.dependency_overrides[get_topology_service] = lambda: topology_service
    app.dependency_overrides[get_simulation_service] = lambda: simulation_service

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
