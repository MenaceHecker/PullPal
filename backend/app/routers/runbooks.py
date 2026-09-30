from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_current_user
from app.embeddings import get_embedding_provider
from app.models import RunbookDocument, User
from app.schemas import RunbookDocumentOut, RunbookSearchResultOut
from app.search import search_runbooks

router = APIRouter(prefix="/api/runbooks", tags=["runbooks"])


@router.get("", response_model=list[RunbookDocumentOut])
def list_runbooks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[RunbookDocument]:
    return db.query(RunbookDocument).order_by(RunbookDocument.title).all()


@router.get("/search", response_model=list[RunbookSearchResultOut])
def search(
    q: str = Query(min_length=1),
    top_k: int = Query(default=5, le=20),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[RunbookSearchResultOut]:
    results = search_runbooks(db, get_embedding_provider(), q, top_k=top_k)
    return [
        RunbookSearchResultOut(
            document_title=result.document_title,
            start_line=result.chunk.start_line,
            end_line=result.chunk.end_line,
            content=result.chunk.content,
            distance=result.distance,
        )
        for result in results
    ]
