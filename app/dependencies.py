"""FastAPI dependency injection providers.

Wired singletons for all application services, allowing easy swapping or mocking in tests.
"""

from functools import lru_cache

from app.services.link_service import LinkService
from app.services.node_service import NodeService
from app.services.packet_service import PacketService
from app.services.simulation_service import SimulationService
from app.services.topology_service import TopologyService
from app.simulation.cpu_simulator import CPUSimulator
from app.simulation.latency_simulator import LatencySimulator
from app.simulation.packet_simulator import PacketSimulator


# Shared singletons
@lru_cache(maxsize=1)
def get_cpu_simulator() -> CPUSimulator:
    """Provide CPUSimulator singleton."""
    return CPUSimulator()


@lru_cache(maxsize=1)
def get_latency_simulator() -> LatencySimulator:
    """Provide LatencySimulator singleton."""
    return LatencySimulator()


@lru_cache(maxsize=1)
def get_packet_simulator() -> PacketSimulator:
    """Provide PacketSimulator singleton."""
    return PacketSimulator(latency_simulator=get_latency_simulator())


@lru_cache(maxsize=1)
def get_node_service() -> NodeService:
    """Provide NodeService singleton."""
    return NodeService()


@lru_cache(maxsize=1)
def get_link_service() -> LinkService:
    """Provide LinkService singleton."""
    return LinkService(node_service=get_node_service())


@lru_cache(maxsize=1)
def get_packet_service() -> PacketService:
    """Provide PacketService singleton."""
    return PacketService(
        node_service=get_node_service(),
        link_service=get_link_service(),
        packet_simulator=get_packet_simulator(),
        cpu_simulator=get_cpu_simulator(),
    )


@lru_cache(maxsize=1)
def get_topology_service() -> TopologyService:
    """Provide TopologyService singleton."""
    return TopologyService(
        node_service=get_node_service(),
        link_service=get_link_service(),
    )


@lru_cache(maxsize=1)
def get_simulation_service() -> SimulationService:
    """Provide SimulationService singleton."""
    return SimulationService(
        node_service=get_node_service(),
        link_service=get_link_service(),
        packet_service=get_packet_service(),
    )
