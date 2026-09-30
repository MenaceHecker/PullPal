from app.embeddings import FakeEmbeddingProvider
from app.runbooks import ingest_all_runbooks
from app.search import search_runbooks
from sqlalchemy.orm import Session


def test_search_finds_the_matching_runbook_section(db_session: Session) -> None:
    ingest_all_runbooks(db_session, FakeEmbeddingProvider())

    results = search_runbooks(
        db_session,
        FakeEmbeddingProvider(),
        "shipping_method 500 error checkout",
        top_k=3,
    )

    assert results, "expected at least one search result"
    assert results[0].document_title == "Checkout Service"
    assert "shipping_method" in results[0].chunk.content


def test_search_respects_top_k(db_session: Session) -> None:
    ingest_all_runbooks(db_session, FakeEmbeddingProvider())

    results = search_runbooks(db_session, FakeEmbeddingProvider(), "checkout", top_k=2)

    assert len(results) == 2


def test_search_with_no_runbooks_returns_empty(db_session: Session) -> None:
    results = search_runbooks(db_session, FakeEmbeddingProvider(), "anything", top_k=5)
    assert results == []
