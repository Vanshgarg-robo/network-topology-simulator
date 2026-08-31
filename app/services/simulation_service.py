"""Simulation aggregation service implementation.

Aggregates CPU workloads, packet latency distributions, and comprehensive simulation statistics.
"""

from app.models.enums import PacketStatus
from app.schemas.metrics_schemas import (
    CpuMetricsResponse,
    LatencyMetricsResponse,
    NodeCpuMetric,
    PacketLatencyMetric,
    StatisticsResponse,
)
from app.services.link_service import LinkService
from app.services.node_service import NodeService
from app.services.packet_service import PacketService


class SimulationService:
    """Service computing aggregated performance metrics and operational statistics."""

    def __init__(
        self,
        node_service: NodeService,
        link_service: LinkService,
        packet_service: PacketService,
    ) -> None:
        self._node_service = node_service
        self._link_service = link_service
        self._packet_service = packet_service

    def get_cpu_metrics(self) -> CpuMetricsResponse:
        """Gather CPU metrics for all nodes in the network."""
        nodes = self._node_service.list_nodes()
        metrics = [
            NodeCpuMetric(
                node_id=node.id,
                node_name=node.name,
                cpu_usage=round(node.cpu_usage, 2),
            )
            for node in nodes
        ]
        avg_cpu = (
            round(sum(m.cpu_usage for m in metrics) / len(metrics), 2)
            if metrics
            else 0.0
        )
        return CpuMetricsResponse(metrics=metrics, average_cpu=avg_cpu)

    def get_latency_metrics(self) -> LatencyMetricsResponse:
        """Gather latency metrics across all successfully delivered packets."""
        packets = self._packet_service.list_packets()
        delivered = [p for p in packets if p.status == PacketStatus.DELIVERED]

        metrics = [
            PacketLatencyMetric(
                packet_id=p.id,
                sequence=p.sequence,
                source_node_id=p.source_node_id,
                destination_node_id=p.destination_node_id,
                latency=round(p.latency, 2),
            )
            for p in delivered
        ]

        if metrics:
            latencies = [m.latency for m in metrics]
            avg_lat = round(sum(latencies) / len(latencies), 2)
            min_lat = min(latencies)
            max_lat = max(latencies)
        else:
            avg_lat = 0.0
            min_lat = 0.0
            max_lat = 0.0

        return LatencyMetricsResponse(
            metrics=metrics,
            average_latency=avg_lat,
            min_latency=min_lat,
            max_latency=max_lat,
        )

    def get_statistics(self) -> StatisticsResponse:
        """Calculate high-level network transmission summary and delivery ratios."""
        nodes = self._node_service.list_nodes()
        links = self._link_service.list_links()
        packets = self._packet_service.list_packets()

        total_packets = len(packets)
        total_delivered = sum(1 for p in packets if p.status == PacketStatus.DELIVERED)
        total_dropped = sum(1 for p in packets if p.status == PacketStatus.DROPPED)

        delivery_rate = (
            round((total_delivered / total_packets) * 100.0, 2)
            if total_packets > 0
            else 0.0
        )

        return StatisticsResponse(
            total_nodes=len(nodes),
            total_links=len(links),
            total_packets=total_packets,
            total_sent=total_packets,
            total_received=total_delivered,
            total_dropped=total_dropped,
            delivery_rate_percent=delivery_rate,
        )
