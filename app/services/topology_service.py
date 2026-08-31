"""Topology service implementation.

Provides complete network topology snapshots aggregating nodes, active/inactive links, and graph dimensions.
"""

from app.schemas.topology_schemas import (
    TopologyEdge,
    TopologyNode,
    TopologyResponse,
)
from app.services.link_service import LinkService
from app.services.node_service import NodeService


class TopologyService:
    """Service computing global topology views."""

    def __init__(
        self,
        node_service: NodeService,
        link_service: LinkService,
    ) -> None:
        self._node_service = node_service
        self._link_service = link_service

    def get_topology(self) -> TopologyResponse:
        """Construct the complete topology graph of the network."""
        nodes = self._node_service.list_nodes()
        links = self._link_service.list_links()

        topology_nodes = [
            TopologyNode(
                id=n.id,
                name=n.name,
                status=n.status,
            )
            for n in nodes
        ]

        topology_edges = [
            TopologyEdge(
                id=l.id,
                source_node_id=l.source_node_id,
                destination_node_id=l.destination_node_id,
                status=l.status,
            )
            for l in links
        ]

        return TopologyResponse(
            nodes=topology_nodes,
            edges=topology_edges,
            node_count=len(topology_nodes),
            edge_count=len(topology_edges),
        )
