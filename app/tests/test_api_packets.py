"""API integration tests for Packet endpoints."""

from fastapi.testclient import TestClient


def test_send_and_get_packet(client: TestClient) -> None:
    """Test POST /api/v1/packets/send and GET /api/v1/packets/{id}."""
    n1 = client.post("/api/v1/nodes", json={"name": "SrcPkt"}).json()
    n2 = client.post("/api/v1/nodes", json={"name": "DstPkt"}).json()
    client.post(
        "/api/v1/links",
        json={"source_node_id": n1["id"], "destination_node_id": n2["id"]},
    )

    send_resp = client.post(
        "/api/v1/packets/send",
        json={
            "source_node_id": n1["id"],
            "destination_node_id": n2["id"],
            "payload": "Hello API packet",
        },
    )
    assert send_resp.status_code == 201
    pkt = send_resp.json()
    assert pkt["status"] == "delivered"
    assert pkt["payload"] == "Hello API packet"
    assert pkt["latency"] > 0

    # Get by ID
    get_resp = client.get(f"/api/v1/packets/{pkt['id']}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == pkt["id"]


def test_list_packets(client: TestClient) -> None:
    """Test GET /api/v1/packets."""
    n1 = client.post("/api/v1/nodes", json={"name": "ListPkt1"}).json()
    n2 = client.post("/api/v1/nodes", json={"name": "ListPkt2"}).json()
    client.post(
        "/api/v1/links",
        json={"source_node_id": n1["id"], "destination_node_id": n2["id"]},
    )

    client.post(
        "/api/v1/packets/send",
        json={"source_node_id": n1["id"], "destination_node_id": n2["id"], "payload": "P1"},
    )
    client.post(
        "/api/v1/packets/send",
        json={"source_node_id": n1["id"], "destination_node_id": n2["id"], "payload": "P2"},
    )

    resp = client.get("/api/v1/packets")
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] >= 2


def test_get_packet_not_found(client: TestClient) -> None:
    """Test invalid packet ID returns 404."""
    resp = client.get("/api/v1/packets/non-existent-id")
    assert resp.status_code == 404
