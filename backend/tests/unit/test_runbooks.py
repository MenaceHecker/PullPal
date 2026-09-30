from pathlib import Path

from app.embeddings import FakeEmbeddingProvider
from app.models import RunbookChunk, RunbookDocument
from app.runbooks import RUNBOOKS_DIR, chunk_markdown, ingest_all_runbooks, ingest_runbook_file
from sqlalchemy.orm import Session


def test_chunk_markdown_splits_into_line_windows() -> None:
    content = "\n".join(f"line {i}" for i in range(1, 51))  # 50 lines

    chunks = chunk_markdown(content, chunk_size=20)

    assert [(start, end) for start, end, _ in chunks] == [(1, 20), (21, 40), (41, 50)]
    assert chunks[0][2].splitlines()[0] == "line 1"
    assert chunks[-1][2].splitlines()[-1] == "line 50"


def test_chunk_markdown_skips_blank_only_chunks() -> None:
    content = "real content\n" + ("\n" * 25)  # second chunk (size 20) would be all blank

    chunks = chunk_markdown(content, chunk_size=20)

    assert len(chunks) == 1


def test_ingest_runbook_file_creates_document_and_chunks(db_session: Session, tmp_path: Path) -> None:
    runbook_path = tmp_path / "test-service.md"
    runbook_path.write_text("# Test Service\n\nSome content about a known issue.\n")

    document = ingest_runbook_file(db_session, FakeEmbeddingProvider(), runbook_path)

    assert document.title == "Test Service"
    chunks = db_session.query(RunbookChunk).filter(RunbookChunk.document_id == document.id).all()
    assert len(chunks) == 1
    assert chunks[0].embedding is not None


def test_ingest_runbook_file_is_idempotent_when_content_unchanged(db_session: Session, tmp_path: Path) -> None:
    runbook_path = tmp_path / "test-service.md"
    runbook_path.write_text("# Test Service\n\nOriginal content.\n")

    first = ingest_runbook_file(db_session, FakeEmbeddingProvider(), runbook_path)
    second = ingest_runbook_file(db_session, FakeEmbeddingProvider(), runbook_path)

    assert first.id == second.id
    assert db_session.query(RunbookDocument).count() == 1


def test_ingest_runbook_file_rechunks_when_content_changes(db_session: Session, tmp_path: Path) -> None:
    runbook_path = tmp_path / "test-service.md"
    runbook_path.write_text("# Test Service\n\nOriginal content.\n")
    ingest_runbook_file(db_session, FakeEmbeddingProvider(), runbook_path)

    runbook_path.write_text("# Test Service\n\nCompletely different content now.\n")
    document = ingest_runbook_file(db_session, FakeEmbeddingProvider(), runbook_path)

    assert document.content == "# Test Service\n\nCompletely different content now.\n"
    assert db_session.query(RunbookDocument).count() == 1


def test_ingest_all_runbooks_picks_up_the_real_runbook_files(db_session: Session) -> None:
    assert RUNBOOKS_DIR.exists(), "backend/runbooks/ should contain the seeded runbook docs"

    documents = ingest_all_runbooks(db_session, FakeEmbeddingProvider())

    titles = {document.title for document in documents}
    assert titles == {"Checkout Service", "Payments Service", "Inventory Service"}
