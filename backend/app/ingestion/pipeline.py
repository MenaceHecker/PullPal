import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.ingestion.sim_client import SimSystemClientProtocol
from app.models import Deploy, LogEntry, MetricPoint, Service


def _latest_timestamp(db: Session, model: type[LogEntry] | type[MetricPoint], service_id: uuid.UUID) -> datetime | None:
    return db.scalar(select(func.max(model.timestamp)).where(model.service_id == service_id))


def ingest_logs(db: Session, client: SimSystemClientProtocol, service: Service) -> int:
    since = _latest_timestamp(db, LogEntry, service.id)
    inserted = 0

    for raw in client.get_logs(service.name, since=since):
        timestamp = datetime.fromisoformat(raw["timestamp"])
        if since is not None and timestamp <= since:
            continue  # already ingested on a previous cycle
        db.add(
            LogEntry(
                service_id=service.id,
                timestamp=timestamp,
                level=raw["level"],
                message=raw["message"],
                trace_id=raw["trace_id"],
            )
        )
        inserted += 1

    return inserted


def ingest_metrics(db: Session, client: SimSystemClientProtocol, service: Service) -> int:
    since = _latest_timestamp(db, MetricPoint, service.id)
    inserted = 0

    for raw in client.get_metrics(service.name, since=since):
        timestamp = datetime.fromisoformat(raw["timestamp"])
        if since is not None and timestamp <= since:
            continue
        db.add(
            MetricPoint(
                service_id=service.id,
                timestamp=timestamp,
                metric_name=raw["metric_name"],
                value=raw["value"],
            )
        )
        inserted += 1

    return inserted


def ingest_deploys(db: Session, client: SimSystemClientProtocol, service: Service) -> int:
    # Deploys can be backdated (a scenario injection backdates one by a few
    # minutes), so a timestamp cursor isn't safe here. Dedupe by sha instead.
    existing_shas = set(db.scalars(select(Deploy.sha).where(Deploy.service_id == service.id)))
    inserted = 0

    for raw in client.get_deploys(service.name):
        if raw["sha"] in existing_shas:
            continue
        db.add(
            Deploy(
                service_id=service.id,
                sha=raw["sha"],
                message=raw["message"],
                deployed_at=datetime.fromisoformat(raw["deployed_at"]),
                deployed_by=raw["deployed_by"],
            )
        )
        existing_shas.add(raw["sha"])
        inserted += 1

    return inserted


def run_ingestion_cycle(db: Session, client: SimSystemClientProtocol) -> dict[str, int]:
    counts = {"logs": 0, "metrics": 0, "deploys": 0}

    for service in db.scalars(select(Service)).all():
        counts["logs"] += ingest_logs(db, client, service)
        counts["metrics"] += ingest_metrics(db, client, service)
        counts["deploys"] += ingest_deploys(db, client, service)

    db.commit()
    return counts
