from pathlib import Path

from sqlalchemy.orm import Session

from app.embeddings import EmbeddingProvider
from app.models import RunbookChunk, RunbookDocument

RUNBOOKS_DIR = Path(__file__).resolve().parent.parent / "runbooks"
CHUNK_SIZE_LINES = 20


def chunk_markdown(content: str, chunk_size: int = CHUNK_SIZE_LINES) -> list[tuple[int, int, str]]:
    """Splits markdown into fixed-size, non-overlapping line windows.
    Returns a list of (start_line, end_line), both 1-indexed and inclusive,
    alongside the chunk's text. Simple on purpose: a real system might chunk
    on headings instead, but line ranges are what the citation format in
    the spec expects (LINES: 12-40), so this keeps that honest."""
    lines = content.splitlines()
    chunks: list[tuple[int, int, str]] = []

    for start in range(0, len(lines), chunk_size):
        end = min(start + chunk_size, len(lines))
        chunk_lines = lines[start:end]
        if not any(line.strip() for line in chunk_lines):
            continue  # skip chunks that are only blank lines
        chunks.append((start + 1, end, "\n".join(chunk_lines)))

    return chunks


def _title_from_filename(path: Path) -> str:
    return path.stem.replace("-", " ").replace("_", " ").title()


def ingest_runbook_file(db: Session, embedding_provider: EmbeddingProvider, path: Path) -> RunbookDocument:
    title = _title_from_filename(path)
    content = path.read_text()

    existing = db.query(RunbookDocument).filter(RunbookDocument.title == title).first()
    if existing is not None and existing.content == content:
        return existing  # nothing changed, don't re-chunk or re-embed

    if existing is not None:
        db.query(RunbookChunk).filter(RunbookChunk.document_id == existing.id).delete()
        existing.content = content
        document = existing
    else:
        document = RunbookDocument(title=title, content=content)
        db.add(document)
        db.flush()  # need document.id before creating chunks

    for index, (start_line, end_line, chunk_text) in enumerate(chunk_markdown(content)):
        db.add(
            RunbookChunk(
                document_id=document.id,
                chunk_index=index,
                start_line=start_line,
                end_line=end_line,
                content=chunk_text,
                embedding=embedding_provider.embed(chunk_text),
            )
        )

    db.commit()
    return document


def ingest_all_runbooks(db: Session, embedding_provider: EmbeddingProvider) -> list[RunbookDocument]:
    if not RUNBOOKS_DIR.exists():
        return []
    return [ingest_runbook_file(db, embedding_provider, path) for path in sorted(RUNBOOKS_DIR.glob("*.md"))]
