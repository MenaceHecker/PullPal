from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.embeddings import EmbeddingProvider
from app.models import RunbookChunk, RunbookDocument


@dataclass
class RunbookSearchResult:
    document_title: str
    chunk: RunbookChunk
    distance: float


def search_runbooks(
    db: Session, embedding_provider: EmbeddingProvider, query: str, top_k: int = 5
) -> list[RunbookSearchResult]:
    query_embedding = embedding_provider.embed(query)
    distance = RunbookChunk.embedding.cosine_distance(query_embedding)

    stmt = (
        select(RunbookChunk, RunbookDocument.title, distance.label("distance"))
        .join(RunbookDocument, RunbookChunk.document_id == RunbookDocument.id)
        .order_by(distance)
        .limit(top_k)
    )

    return [
        RunbookSearchResult(document_title=title, chunk=chunk, distance=dist)
        for chunk, title, dist in db.execute(stmt).all()
    ]
