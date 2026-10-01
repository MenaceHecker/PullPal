from sqlalchemy import select
from sqlalchemy.orm import Session

from app.embeddings import get_embedding_provider
from app.models import Deploy, LogEntry, MetricPoint, Service
from app.search import search_runbooks as run_runbook_search
from app.tools.schemas import (
    GetMetricsInput,
    GetRecentDeploysInput,
    GetServiceStatusInput,
    QueryLogsInput,
    SearchRunbooksInput,
)

# Above this, a service is treated as degraded. Matches the baseline vs.
# scenario error rates from the simulated system (healthy ~1%, an injected
# scenario is 18%+), so this sits comfortably between the two.
DEGRADED_ERROR_RATE_THRESHOLD = 0.1


def _get_service(db: Session, name: str) -> Service:
    service = db.query(Service).filter(Service.name == name).first()
    if service is None:
        raise ValueError(f"Unknown service: {name}")
    return service


def query_logs(db: Session, params: QueryLogsInput) -> dict:
    service = _get_service(db, params.service)

    stmt = select(LogEntry).where(LogEntry.service_id == service.id)
    if params.start_time is not None:
        stmt = stmt.where(LogEntry.timestamp >= params.start_time)
    if params.end_time is not None:
        stmt = stmt.where(LogEntry.timestamp <= params.end_time)
    if params.level is not None:
        stmt = stmt.where(LogEntry.level == params.level.upper())
    stmt = stmt.order_by(LogEntry.timestamp.desc()).limit(params.limit)

    entries = db.scalars(stmt).all()
    return {
        "service": service.name,
        "count": len(entries),
        "logs": [
            {
                "timestamp": entry.timestamp.isoformat(),
                "level": entry.level,
                "message": entry.message,
                "trace_id": entry.trace_id,
            }
            for entry in entries
        ],
    }


def get_metrics(db: Session, params: GetMetricsInput) -> dict:
    service = _get_service(db, params.service)

    stmt = select(MetricPoint).where(
        MetricPoint.service_id == service.id,
        MetricPoint.metric_name == params.metric_name,
    )
    if params.start_time is not None:
        stmt = stmt.where(MetricPoint.timestamp >= params.start_time)
    if params.end_time is not None:
        stmt = stmt.where(MetricPoint.timestamp <= params.end_time)
    stmt = stmt.order_by(MetricPoint.timestamp.asc())

    points = db.scalars(stmt).all()
    return {
        "service": service.name,
        "metric_name": params.metric_name,
        "count": len(points),
        "points": [{"timestamp": point.timestamp.isoformat(), "value": point.value} for point in points],
    }


def get_recent_deploys(db: Session, params: GetRecentDeploysInput) -> dict:
    service = _get_service(db, params.service)

    stmt = select(Deploy).where(Deploy.service_id == service.id)
    if params.start_time is not None:
        stmt = stmt.where(Deploy.deployed_at >= params.start_time)
    if params.end_time is not None:
        stmt = stmt.where(Deploy.deployed_at <= params.end_time)
    stmt = stmt.order_by(Deploy.deployed_at.desc()).limit(params.limit)

    deploys = db.scalars(stmt).all()
    return {
        "service": service.name,
        "count": len(deploys),
        "deploys": [
            {
                "sha": deploy.sha,
                "message": deploy.message,
                "deployed_at": deploy.deployed_at.isoformat(),
                "deployed_by": deploy.deployed_by,
            }
            for deploy in deploys
        ],
    }


def search_runbooks(db: Session, params: SearchRunbooksInput) -> dict:
    results = run_runbook_search(db, get_embedding_provider(), params.query, top_k=params.top_k)
    return {
        "query": params.query,
        "count": len(results),
        "results": [
            {
                "document_title": result.document_title,
                "start_line": result.chunk.start_line,
                "end_line": result.chunk.end_line,
                "content": result.chunk.content,
                "distance": result.distance,
            }
            for result in results
        ],
    }


def get_service_status(db: Session, params: GetServiceStatusInput) -> dict:
    service = _get_service(db, params.service)

    latest = db.scalars(
        select(MetricPoint)
        .where(MetricPoint.service_id == service.id, MetricPoint.metric_name == "error_rate")
        .order_by(MetricPoint.timestamp.desc())
        .limit(1)
    ).first()

    if latest is None:
        return {"service": service.name, "status": "unknown", "latest_error_rate": None, "as_of": None}

    status = "degraded" if latest.value > DEGRADED_ERROR_RATE_THRESHOLD else "healthy"
    return {
        "service": service.name,
        "status": status,
        "latest_error_rate": latest.value,
        "as_of": latest.timestamp.isoformat(),
    }
