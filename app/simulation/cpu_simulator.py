"""CPU usage simulator.

Generates realistic simulated CPU usage values for network nodes.
"""

import random

from app.core.logger import get_logger
from app.models.node import Node

logger = get_logger("simulation.cpu")


class CPUSimulator:
    """Simulates CPU usage for network nodes.

    Online nodes receive a random CPU usage between the configured
    minimum and maximum bounds. Offline nodes always report 0%.
    """

    def __init__(
        self,
        min_usage: int = 5,
        max_usage: int = 30,
    ) -> None:
        self._min_usage = min_usage
        self._max_usage = max_usage

    def generate_cpu(self, node: Node) -> float:
        """Generate a simulated CPU usage value.

        Args:
            node: The node to generate CPU usage for.

        Returns:
            CPU usage percentage. 0 if the node is offline.
        """
        if not node.is_online:
            return 0.0
        return float(random.randint(self._min_usage, self._max_usage))

    def update_node_cpu(self, node: Node) -> None:
        """Update a node's CPU usage with a newly generated value.

        Args:
            node: The node whose CPU usage to update.
        """
        previous = node.cpu_usage
        node.cpu_usage = self.generate_cpu(node)
        logger.debug(
            "CPU updated: node=%s, previous=%.1f%%, current=%.1f%%",
            node.name,
            previous,
            node.cpu_usage,
        )
