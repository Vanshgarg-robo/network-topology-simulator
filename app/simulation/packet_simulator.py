"""Packet transmission simulator.

Orchestrates the latency simulation for packet transmissions.
"""

from app.core.logger import get_logger
from app.models.packet import Packet
from app.simulation.latency_simulator import LatencySimulator

logger = get_logger("simulation.packet")


class PacketSimulator:
    """Simulates the transmission of packets across the network.

    Computes latency for each packet transmission using the
    injected LatencySimulator.
    """

    def __init__(self, latency_simulator: LatencySimulator | None = None) -> None:
        self._latency_simulator = latency_simulator or LatencySimulator()

    def transmit(self, packet: Packet) -> float:
        """Simulate transmitting a packet and compute its latency.

        Args:
            packet: The packet being transmitted.

        Returns:
            The computed latency in milliseconds.
        """
        latency = self._latency_simulator.calculate_latency(
            packet.source_node_id,
            packet.destination_node_id,
        )
        logger.info(
            "Packet transmitted: seq=%d, %s->%s, latency=%.1fms",
            packet.sequence,
            packet.source_node_id,
            packet.destination_node_id,
            latency,
        )
        return latency
