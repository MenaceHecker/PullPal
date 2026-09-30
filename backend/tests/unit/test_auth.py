from collections.abc import Callable

from fastapi.testclient import TestClient


def test_register_returns_access_token(client: TestClient) -> None:
    response = client.post(
        "/api/auth/register",
        json={"email": "alice@example.com", "password": "password123"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["access_token"]
    assert body["token_type"] == "bearer"


def test_register_rejects_duplicate_email(client: TestClient) -> None:
    payload = {"email": "bob@example.com", "password": "password123"}
    first = client.post("/api/auth/register", json=payload)
    assert first.status_code == 201

    second = client.post("/api/auth/register", json=payload)
    assert second.status_code == 409


def test_register_rejects_short_password(client: TestClient) -> None:
    response = client.post(
        "/api/auth/register",
        json={"email": "short@example.com", "password": "short"},
    )
    assert response.status_code == 422


def test_login_with_correct_credentials_succeeds(client: TestClient) -> None:
    client.post(
        "/api/auth/register",
        json={"email": "carol@example.com", "password": "password123"},
    )

    response = client.post(
        "/api/auth/login",
        json={"email": "carol@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    assert response.json()["access_token"]


def test_login_with_wrong_password_rejected(client: TestClient) -> None:
    client.post(
        "/api/auth/register",
        json={"email": "dave@example.com", "password": "password123"},
    )

    response = client.post(
        "/api/auth/login",
        json={"email": "dave@example.com", "password": "wrong-password"},
    )
    assert response.status_code == 401


def test_login_with_unknown_email_rejected(client: TestClient) -> None:
    response = client.post(
        "/api/auth/login",
        json={"email": "ghost@example.com", "password": "password123"},
    )
    assert response.status_code == 401


def test_me_requires_authentication(client: TestClient) -> None:
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_me_rejects_garbage_token(client: TestClient) -> None:
    response = client.get("/api/auth/me", headers={"Authorization": "Bearer not-a-real-token"})
    assert response.status_code == 401


def test_me_returns_current_user(client: TestClient, register: Callable[[str, str], dict[str, str]]) -> None:
    headers = register("erin@example.com")

    response = client.get("/api/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == "erin@example.com"
