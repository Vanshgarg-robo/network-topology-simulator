"""Pydantic schemas for Topology API responses."""

from pydantic import BaseModel, Field

from app.models.enums import LinkStatus, NodeStatus


class TopologyNode(BaseModel):
    """A node in the topology graph."""

    id: str = Field(..., description="Node identifier")
    name: str = Field(..., description="Node name")
    status: NodeStatus = Field(..., description="Operational status")


class TopologyEdge(BaseModel):
    """An edge (link) in the topology graph."""

    id: str = Field(..., description="Link identifier")
    source_node_id: str = Field(..., description="Source node ID")
    destination_node_id: str = Field(..., description="Destination node ID")
    status: LinkStatus = Field(..., description="Link status")


class TopologyResponse(BaseModel):
    """Complete network topology representation."""

    nodes: list[TopologyNode] = Field(..., description="All nodes in the network")
    edges: list[TopologyEdge] = Field(..., description="All links in the network")
    node_count: int = Field(..., description="Total number of nodes")
    edge_count: int = Field(..., description="Total number of edges")
