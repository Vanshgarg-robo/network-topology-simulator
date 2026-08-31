"""Pydantic schemas for Metrics API responses."""

from pydantic import BaseModel, Field


class NodeCpuMetric(BaseModel):
    """CPU usage metric for a single node."""

    node_id: str = Field(..., description="Node identifier")
    node_name: str = Field(..., description="Node name")
    cpu_usage: float = Field(..., description="CPU usage percentage")


class CpuMetricsResponse(BaseModel):
    """Aggregated CPU metrics across all nodes."""

    metrics: list[NodeCpuMetric] = Field(..., description="Per-node CPU metrics")
    average_cpu: float = Field(..., description="Average CPU usage across all nodes")


class PacketLatencyMetric(BaseModel):
    """Latency metric for a single delivered packet."""

    packet_id: str = Field(..., description="Packet identifier")
    sequence: int = Field(..., description="Packet sequence number")
    source_node_id: str = Field(..., description="Source node ID")
    destination_node_id: str = Field(..., description="Destination node ID")
    latency: float = Field(..., description="Latency in milliseconds")


class LatencyMetricsResponse(BaseModel):
    """Aggregated latency metrics across delivered packets."""

    metrics: list[PacketLatencyMetric] = Field(..., description="Per-packet latency")
    average_latency: float = Field(..., description="Average latency in ms")
    min_latency: float = Field(..., description="Minimum latency in ms")
    max_latency: float = Field(..., description="Maximum latency in ms")


class StatisticsResponse(BaseModel):
    """Overall simulation statistics."""

    total_nodes: int = Field(..., description="Total number of nodes")
    total_links: int = Field(..., description="Total number of links")
    total_packets: int = Field(..., description="Total packets processed")
    total_sent: int = Field(..., description="Successfully sent packets")
    total_received: int = Field(..., description="Successfully received packets")
    total_dropped: int = Field(..., description="Dropped packets")
    delivery_rate_percent: float = Field(..., description="Delivery success rate")
