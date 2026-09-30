from collections.abc import Callable

from app.embeddings import FakeEmbeddingProvider
from app.runbooks import ingest_all_runbooks
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def test_list_runbooks_requires_authentication(client: TestClient) -> None:
    response = client.get("/api/runbooks")
    assert response.status_code == 401


def test_search_requires_authentication(client: TestClient) -> None:
    response = client.get("/api/runbooks/search?q=checkout")
    assert response.status_code == 401


def test_list_runbooks_returns_seeded_documents(
    client: TestClient, db_session: Session, register: Callable[[str, str], dict[str, str]]
) -> None:
    ingest_all_runbooks(db_session, FakeEmbeddingProvider())
    headers = register("alice@example.com")

    response = client.get("/api/runbooks", headers=headers)

    assert response.status_code == 200
    titles = {doc["title"] for doc in response.json()}
    assert titles == {"Checkout Service", "Payments Service", "Inventory Service"}


def test_search_returns_the_matching_section(
    client: TestClient, db_session: Session, register: Callable[[str, str], dict[str, str]]
) -> None:
    ingest_all_runbooks(db_session, FakeEmbeddingProvider())
    headers = register("alice@example.com")

    response = client.get("/api/runbooks/search?q=shipping_method+checkout+500", headers=headers)

    assert response.status_code == 200
    results = response.json()
    assert results[0]["document_title"] == "Checkout Service"
