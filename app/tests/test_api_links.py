"""API integration tests for Link endpoints."""

from fastapi.testclient import TestClient


def test_create_and_list_links(client: TestClient) -> None:
    """Test POST /api/v1/links and GET /api/v1/links."""
    n1 = client.post("/api/v1/nodes", json={"name": "LinkTest1"}).json()
    n2 = client.post("/api/v1/nodes", json={"name": "LinkTest2"}).json()

    resp = client.post(
        "/api/v1/links",
        json={"source_node_id": n1["id"], "destination_node_id": n2["id"]},
    )
    assert resp.status_code == 201
    link = resp.json()
    assert link["source_node_id"] == n1["id"]
    assert link["destination_node_id"] == n2["id"]
    assert link["status"] == "active"

    # List links
    list_resp = client.get("/api/v1/links")
    assert list_resp.status_code == 200
    assert any(l["id"] == link["id"] for l in list_resp.json()["links"])


def test_create_link_errors(client: TestClient) -> None:
    """Test self-loop and missing node errors return proper status codes."""
    n1 = client.post("/api/v1/nodes", json={"name": "SelfNode"}).json()

    # Self-loop
    resp1 = client.post(
        "/api/v1/links",
        json={"source_node_id": n1["id"], "destination_node_id": n1["id"]},
    )
    assert resp1.status_code == 500  # SimulatorError

    # Missing node
    resp2 = client.post(
        "/api/v1/links",
        json={"source_node_id": n1["id"], "destination_node_id": "missing-id"},
    )
    assert resp2.status_code == 404


def test_enable_disable_and_delete_link(client: TestClient) -> None:
    """Test link enable, disable, and delete endpoints."""
    n1 = client.post("/api/v1/nodes", json={"name": "N1"}).json()
    n2 = client.post("/api/v1/nodes", json={"name": "N2"}).json()

    link = client.post(
        "/api/v1/links",
        json={"source_node_id": n1["id"], "destination_node_id": n2["id"]},
    ).json()

    link_id = link["id"]

    # Disable
    dis_resp = client.post(f"/api/v1/links/{link_id}/disable")
    assert dis_resp.status_code == 200
    assert dis_resp.json()["status"] == "down"

    # Enable
    en_resp = client.post(f"/api/v1/links/{link_id}/enable")
    assert en_resp.status_code == 200
    assert en_resp.json()["status"] == "active"

    # Delete
    del_resp = client.delete(f"/api/v1/links/{link_id}")
    assert del_resp.status_code == 204
