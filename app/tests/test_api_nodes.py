"""API integration tests for Node endpoints."""

from fastapi.testclient import TestClient


def test_create_and_get_node(client: TestClient) -> None:
    """Test POST /api/v1/nodes and GET /api/v1/nodes/{id}."""
    resp = client.post("/api/v1/nodes", json={"name": "Router-X"})
    assert resp.status_code == 201
    node_data = resp.json()
    assert node_data["name"] == "Router-X"
    assert node_data["status"] == "online"
    node_id = node_data["id"]

    # Get by ID
    get_resp = client.get(f"/api/v1/nodes/{node_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == node_id


def test_create_duplicate_node(client: TestClient) -> None:
    """Test duplicate node name returns 409 Conflict."""
    client.post("/api/v1/nodes", json={"name": "Duplicate"})
    resp = client.post("/api/v1/nodes", json={"name": "Duplicate"})
    assert resp.status_code == 409


def test_get_node_not_found(client: TestClient) -> None:
    """Test non-existent node returns 404."""
    resp = client.get("/api/v1/nodes/invalid-id")
    assert resp.status_code == 404


def test_list_nodes(client: TestClient) -> None:
    """Test GET /api/v1/nodes lists all created nodes."""
    client.post("/api/v1/nodes", json={"name": "Node-1"})
    client.post("/api/v1/nodes", json={"name": "Node-2"})

    resp = client.get("/api/v1/nodes")
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] >= 2
    assert len(data["nodes"]) >= 2


def test_update_node(client: TestClient) -> None:
    """Test PUT /api/v1/nodes/{id}."""
    resp = client.post("/api/v1/nodes", json={"name": "Initial"})
    node_id = resp.json()["id"]

    put_resp = client.put(f"/api/v1/nodes/{node_id}", json={"name": "Renamed"})
    assert put_resp.status_code == 200
    assert put_resp.json()["name"] == "Renamed"


def test_delete_node(client: TestClient) -> None:
    """Test DELETE /api/v1/nodes/{id} returns 204."""
    resp = client.post("/api/v1/nodes", json={"name": "ToDelete"})
    node_id = resp.json()["id"]

    del_resp = client.delete(f"/api/v1/nodes/{node_id}")
    assert del_resp.status_code == 204

    get_resp = client.get(f"/api/v1/nodes/{node_id}")
    assert get_resp.status_code == 404


def test_enable_disable_node_api(client: TestClient) -> None:
    """Test POST enable and disable endpoints."""
    resp = client.post("/api/v1/nodes", json={"name": "ToggleNode"})
    node_id = resp.json()["id"]

    dis_resp = client.post(f"/api/v1/nodes/{node_id}/disable")
    assert dis_resp.status_code == 200
    assert dis_resp.json()["status"] == "offline"

    en_resp = client.post(f"/api/v1/nodes/{node_id}/enable")
    assert en_resp.status_code == 200
    assert en_resp.json()["status"] == "online"
