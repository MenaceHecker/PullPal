from datetime import datetime

from fastapi import APIRouter, Depends, Query

from app.deps import get_service_or_404
from app.schemas import LogEntryOut
from app.state import ServiceState

router = APIRouter(prefix="/services/{service_name}/logs", tags=["logs"])


@router.get("", response_model=list[LogEntryOut])
def query_logs(
    start_time: datetime | None = Query(default=None),
    end_time: datetime | None = Query(default=None),
    level: str | None = Query(default=None, description="Filter to a single log level, e.g. ERROR"),
    limit: int = Query(default=200, le=2000),
    service_state: ServiceState = Depends(get_service_or_404),
) -> list[LogEntryOut]:
    entries = list(service_state.logs)

    if start_time is not None:
        entries = [entry for entry in entries if entry.timestamp >= start_time]
    if end_time is not None:
        entries = [entry for entry in entries if entry.timestamp <= end_time]
    if level is not None:
        entries = [entry for entry in entries if entry.level.lower() == level.lower()]

    # Newest first, capped to limit.
    entries.sort(key=lambda entry: entry.timestamp, reverse=True)
    return entries[:limit]
