from collections.abc import Callable

from fastapi.testclient import TestClient


def test_create_incident_requires_authentication(client: TestClient) -> None:
    response = client.post("/api/incidents", json={"title": "Checkout returning 500s"})
    assert response.status_code == 401


def test_user_can_create_and_fetch_own_incident(
    client: TestClient, register: Callable[[str, str], dict[str, str]]
) -> None:
    headers = register("alice@example.com")

    create_response = client.post(
        "/api/incidents",
        json={"title": "Checkout returning 500s", "description": "Spiking since 14:32"},
        headers=headers,
    )
    assert create_response.status_code == 201
    incident_id = create_response.json()["id"]

    get_response = client.get(f"/api/incidents/{incident_id}", headers=headers)
    assert get_response.status_code == 200
    assert get_response.json()["title"] == "Checkout returning 500s"


def test_user_cannot_fetch_another_users_incident(
    client: TestClient, register: Callable[[str, str], dict[str, str]]
) -> None:
    alice_headers = register("alice@example.com")
    bob_headers = register("bob@example.com")

    create_response = client.post(
        "/api/incidents",
        json={"title": "Alice's incident"},
        headers=alice_headers,
    )
    incident_id = create_response.json()["id"]

    # A 404, not a 403: Bob shouldn't be able to tell the incident exists at all.
    response = client.get(f"/api/incidents/{incident_id}", headers=bob_headers)
    assert response.status_code == 404


def test_list_incidents_is_scoped_to_the_current_user(
    client: TestClient, register: Callable[[str, str], dict[str, str]]
) -> None:
    alice_headers = register("alice@example.com")
    bob_headers = register("bob@example.com")

    client.post("/api/incidents", json={"title": "Alice's incident"}, headers=alice_headers)
    client.post("/api/incidents", json={"title": "Bob's incident"}, headers=bob_headers)

    alice_incidents = client.get("/api/incidents", headers=alice_headers).json()
    titles = [incident["title"] for incident in alice_incidents]

    assert "Alice's incident" in titles
    assert "Bob's incident" not in titles


def test_list_incidents_requires_authentication(client: TestClient) -> None:
    response = client.get("/api/incidents")
    assert response.status_code == 401


def test_fetching_nonexistent_incident_returns_404(
    client: TestClient, register: Callable[[str, str], dict[str, str]]
) -> None:
    headers = register("alice@example.com")

    response = client.get("/api/incidents/00000000-0000-0000-0000-000000000000", headers=headers)
    assert response.status_code == 404
