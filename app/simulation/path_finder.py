"""BFS pathfinding engine.

Extracted from the original NetworkSimulator.find_path() into a
standalone, testable component with a clear single responsibility.
"""

from collections import defaultdict, deque

from app.core.logger import get_logger

logger = get_logger("simulation.pathfinder")

AdjacencyGraph = dict[str, list[str]]


class PathFinder:
    """Finds shortest paths in an undirected graph using BFS.

    The graph is represented as an adjacency list mapping node IDs
    to lists of neighbouring node IDs.
    """

    @staticmethod
    def find_path(
        graph: AdjacencyGraph,
        source: str,
        destination: str,
    ) -> list[str] | None:
        """Find the shortest path between two nodes using BFS.

        Args:
            graph: Adjacency list of the network graph.
            source: Starting node ID.
            destination: Target node ID.

        Returns:
            Ordered list of node IDs forming the path, or None if
            no path exists.
        """
        if source == destination:
            return [source]

        queue: deque[list[str]] = deque([[source]])
        visited: set[str] = set()

        while queue:
            path = queue.popleft()
            current_node = path[-1]

            if current_node == destination:
                logger.debug(
                    "Path found: %s (hops=%d)",
                    " -> ".join(path),
                    len(path) - 1,
                )
                return path

            if current_node not in visited:
                visited.add(current_node)
                for neighbour in graph.get(current_node, []):
                    new_path = [*path, neighbour]
                    queue.append(new_path)

        logger.debug("No path found: %s -> %s", source, destination)
        return None

    @staticmethod
    def build_adjacency_graph(
        edges: list[tuple[str, str]],
    ) -> AdjacencyGraph:
        """Build an undirected adjacency graph from a list of edges.

        Each edge (source, destination) creates bidirectional connections.

        Args:
            edges: List of (source_node_id, destination_node_id) tuples.

        Returns:
            Adjacency list mapping node IDs to neighbour lists.
        """
        graph: AdjacencyGraph = defaultdict(list)
        for source, destination in edges:
            graph[source].append(destination)
            graph[destination].append(source)
        return dict(graph)
