"""Packet service implementation.

Handles packet transmission orchestration, pathfinding resolution, node CPU updates, and lifecycle tracking.
"""

import threading
from typing import Optional

from app.core.exceptions import PacketNotFoundError
from app.core.logger import get_logger
from app.models.enums import DropReason
from app.models.packet import Packet
from app.services.link_service import LinkService
from app.services.node_service import NodeService
from app.simulation.cpu_simulator import CPUSimulator
from app.simulation.packet_simulator import PacketSimulator
from app.simulation.path_finder import PathFinder

logger = get_logger("service.packet")


class PacketService:
    """Service managing packet creation, transmission, routing, and history."""

    def __init__(
        self,
        node_service: NodeService,
        link_service: LinkService,
        packet_simulator: Optional[PacketSimulator] = None,
        cpu_simulator: Optional[CPUSimulator] = None,
    ) -> None:
        self._node_service = node_service
        self._link_service = link_service
        self._packet_simulator = packet_simulator or PacketSimulator()
        self._cpu_simulator = cpu_simulator or CPUSimulator()

        self._packets: dict[str, Packet] = {}  # id -> Packet
        self._sequence_counter = 0
        self._lock = threading.Lock()

    def send_packet(
        self,
        source_node_id: str,
        destination_node_id: str,
        payload: str,
    ) -> Packet:
        """Process and transmit a packet through the network.

        Validates node existence, checks operational states, resolves the shortest
        path via active links, computes latency, and updates node CPU workloads.

        Args:
            source_node_id: Source node identifier.
            destination_node_id: Destination node identifier.
            payload: Payload message data.

        Returns:
            The processed Packet instance with final status and metrics.

        Raises:
            NodeNotFoundError: If source or destination node does not exist.
        """
        # Node lookup validation (raises NodeNotFoundError if missing)
        source_node = self._node_service.get_node(source_node_id)
        dest_node = self._node_service.get_node(destination_node_id)

        with self._lock:
            self._sequence_counter += 1
            packet = Packet(
                sequence=self._sequence_counter,
                source_node_id=source_node_id,
                destination_node_id=destination_node_id,
                payload=payload,
            )
            self._packets[packet.id] = packet

            # Check source node online status
            if not source_node.is_online:
                packet.mark_dropped(DropReason.SOURCE_OFFLINE)
                logger.warning(
                    "Packet #%d dropped: Source node %s is offline",
                    packet.sequence,
                    source_node.name,
                )
                return packet

            # Check destination node online status
            if not dest_node.is_online:
                packet.mark_dropped(DropReason.DESTINATION_OFFLINE)
                logger.warning(
                    "Packet #%d dropped: Destination node %s is offline",
                    packet.sequence,
                    dest_node.name,
                )
                return packet

            # Compute shortest route via active graph
            graph = self._link_service.get_active_adjacency_graph()
            path = PathFinder.find_path(graph, source_node_id, destination_node_id)

            if path:
                latency = self._packet_simulator.transmit(packet)
                packet.mark_delivered(path=path, latency=latency)

                # Update CPU for every node participating in the route
                for node_id in path:
                    try:
                        node = self._node_service.get_node(node_id)
                        self._cpu_simulator.update_node_cpu(node)
                    except Exception as exc:
                        logger.error("Failed to update CPU for node %s: %s", node_id, exc)

                logger.info(
                    "Packet #%d delivered via %d hops in %.1fms",
                    packet.sequence,
                    len(path) - 1,
                    latency,
                )
            else:
                packet.mark_dropped(DropReason.NO_ROUTE)
                logger.warning(
                    "Packet #%d dropped: No active route between %s and %s",
                    packet.sequence,
                    source_node.name,
                    dest_node.name,
                )

            return packet

    def get_packet(self, packet_id: str) -> Packet:
        """Retrieve a packet by its unique ID."""
        with self._lock:
            packet = self._packets.get(packet_id)
            if not packet:
                logger.warning("Packet not found: id=%s", packet_id)
                raise PacketNotFoundError(packet_id=packet_id)
            return packet

    def list_packets(self) -> list[Packet]:
        """Retrieve all recorded packets sorted by sequence number."""
        with self._lock:
            return sorted(self._packets.values(), key=lambda p: p.sequence)

    def clear(self) -> None:
        """Clear all stored packets and reset sequence counter (testing)."""
        with self._lock:
            self._packets.clear()
            self._sequence_counter = 0
