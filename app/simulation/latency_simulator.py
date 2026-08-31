"""Latency simulator.

Generates simulated network latency values for packet transmissions.
"""

import random

from app.core.logger import get_logger

logger = get_logger("simulation.latency")


class LatencySimulator:
    """Simulates network latency between nodes.

    Generates random latency values within configurable bounds
    to simulate real-world network conditions.
    """

    def __init__(
        self,
        min_latency_ms: int = 10,
        max_latency_ms: int = 100,
    ) -> None:
        self._min_latency_ms = min_latency_ms
        self._max_latency_ms = max_latency_ms

    def calculate_latency(self, source_node_id: str, destination_node_id: str) -> float:
        """Calculate simulated latency between two nodes.

        Args:
            source_node_id: ID of the source node.
            destination_node_id: ID of the destination node.

        Returns:
            Latency in milliseconds.
        """
        latency = float(random.randint(self._min_latency_ms, self._max_latency_ms))
        logger.debug(
            "Latency calculated: %s->%s = %.1fms",
            source_node_id,
            destination_node_id,
            latency,
        )
        return latency
