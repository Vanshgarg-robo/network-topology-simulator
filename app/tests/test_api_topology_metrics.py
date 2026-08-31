"""API integration tests for Topology and Metrics endpoints."""

from fastapi.testclient import TestClient


def test_topology_and_metrics_apis(client: TestClient) -> None:
    """Test /api/v1/topology and /api/v1/metrics/* endpoints end-to-end."""
    # Setup 2 nodes + 1 link
    n1 = client.post("/api/v1/nodes", json={"name": "MetricNode1"}).json()
    n2 = client.post("/api/v1/nodes", json={"name": "MetricNode2"}).json()
    client.post(
        "/api/v1/links",
        json={"source_node_id": n1["id"], "destination_node_id": n2["id"]},
    )

    # Send a packet
    client.post(
        "/api/v1/packets/send",
        json={"source_node_id": n1["id"], "destination_node_id": n2["id"], "payload": "Metrics test"},
    )

    # Topology
    topo_resp = client.get("/api/v1/topology")
    assert topo_resp.status_code == 200
    topo = topo_resp.json()
    assert topo["node_count"] >= 2
    assert topo["edge_count"] >= 1

    # CPU metrics
    cpu_resp = client.get("/api/v1/metrics/cpu")
    assert cpu_resp.status_code == 200
    cpu = cpu_resp.json()
    assert len(cpu["metrics"]) >= 2

    # Latency metrics
    lat_resp = client.get("/api/v1/metrics/latency")
    assert lat_resp.status_code == 200
    lat = lat_resp.json()
    assert len(lat["metrics"]) >= 1
    assert lat["average_latency"] > 0

    # Statistics
    stats_resp = client.get("/api/v1/metrics/statistics")
    assert stats_resp.status_code == 200
    stats = stats_resp.json()
    assert stats["total_packets"] >= 1
    assert stats["total_received"] >= 1
    assert stats["delivery_rate_percent"] > 0
