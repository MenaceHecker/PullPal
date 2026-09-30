from datetime import UTC, datetime, timedelta

from app.ingestion.pipeline import ingest_deploys, ingest_logs, ingest_metrics, run_ingestion_cycle
from app.models import Deploy, LogEntry, MetricPoint, Service
from app.seed import seed_services
from sqlalchemy.orm import Session

from tests.fakes import FakeSimSystemClient

T0 = datetime(2026, 9, 30, 12, 0, 0, tzinfo=UTC)


def _checkout_service(db_session: Session) -> Service:
    seed_services(db_session)
    return db_session.query(Service).filter(Service.name == "checkout-service").one()


def test_ingest_logs_inserts_new_entries(db_session: Session) -> None:
    service = _checkout_service(db_session)
    client = FakeSimSystemClient(
        logs_by_service={
            "checkout-service": [
                {
                    "timestamp": T0.isoformat(),
                    "level": "INFO",
                    "message": "request completed",
                    "trace_id": "abc",
                }
            ]
        }
    )

    inserted = ingest_logs(db_session, client, service)

    assert inserted == 1
    assert db_session.query(LogEntry).filter(LogEntry.service_id == service.id).count() == 1


def test_ingest_logs_does_not_duplicate_on_a_second_run(db_session: Session) -> None:
    service = _checkout_service(db_session)
    client = FakeSimSystemClient(
        logs_by_service={
            "checkout-service": [
                {"timestamp": T0.isoformat(), "level": "INFO", "message": "a", "trace_id": "1"},
            ]
        }
    )

    ingest_logs(db_session, client, service)
    db_session.commit()

    # Same data offered again, as if a second ingestion cycle ran before
    # anything new happened.
    inserted_again = ingest_logs(db_session, client, service)

    assert inserted_again == 0
    assert db_session.query(LogEntry).filter(LogEntry.service_id == service.id).count() == 1


def test_ingest_logs_picks_up_only_newer_entries(db_session: Session) -> None:
    service = _checkout_service(db_session)
    client = FakeSimSystemClient(
        logs_by_service={
            "checkout-service": [
                {"timestamp": T0.isoformat(), "level": "INFO", "message": "old", "trace_id": "1"},
            ]
        }
    )
    ingest_logs(db_session, client, service)
    db_session.commit()

    newer = T0 + timedelta(seconds=5)
    client.logs_by_service["checkout-service"].append(
        {"timestamp": newer.isoformat(), "level": "ERROR", "message": "new", "trace_id": "2"}
    )

    inserted = ingest_logs(db_session, client, service)

    assert inserted == 1
    assert db_session.query(LogEntry).filter(LogEntry.service_id == service.id).count() == 2


def test_ingest_metrics_inserts_new_points(db_session: Session) -> None:
    service = _checkout_service(db_session)
    client = FakeSimSystemClient(
        metrics_by_service={
            "checkout-service": [
                {"timestamp": T0.isoformat(), "metric_name": "error_rate", "value": 0.01},
            ]
        }
    )

    inserted = ingest_metrics(db_session, client, service)

    assert inserted == 1
    assert db_session.query(MetricPoint).filter(MetricPoint.service_id == service.id).count() == 1


def test_ingest_deploys_dedupes_by_sha_even_when_backdated(db_session: Session) -> None:
    service = _checkout_service(db_session)
    client = FakeSimSystemClient(
        deploys_by_service={
            "checkout-service": [
                {
                    "sha": "abc123",
                    "message": "a normal deploy",
                    "deployed_at": T0.isoformat(),
                    "deployed_by": "alice",
                },
            ]
        }
    )
    ingest_deploys(db_session, client, service)
    db_session.commit()

    # A scenario injection backdates its deploy, so it can land *before* the
    # latest deploy timestamp already ingested. Sha-based dedup has to catch
    # this even though a timestamp cursor wouldn't.
    client.deploys_by_service["checkout-service"].append(
        {
            "sha": "def456",
            "message": "backdated incident-causing deploy",
            "deployed_at": (T0 - timedelta(minutes=3)).isoformat(),
            "deployed_by": "ci-bot",
        }
    )
    # Re-offer the original deploy too, to prove it doesn't get inserted twice.
    inserted = ingest_deploys(db_session, client, service)

    assert inserted == 1
    shas = {sha for (sha,) in db_session.query(Deploy.sha).filter(Deploy.service_id == service.id).all()}
    assert shas == {"abc123", "def456"}


def test_run_ingestion_cycle_covers_every_seeded_service(db_session: Session) -> None:
    seed_services(db_session)
    client = FakeSimSystemClient(
        logs_by_service={
            "checkout-service": [{"timestamp": T0.isoformat(), "level": "INFO", "message": "a", "trace_id": "1"}],
            "payments-service": [{"timestamp": T0.isoformat(), "level": "INFO", "message": "b", "trace_id": "2"}],
            "inventory-service": [{"timestamp": T0.isoformat(), "level": "INFO", "message": "c", "trace_id": "3"}],
        }
    )

    counts = run_ingestion_cycle(db_session, client)

    assert counts["logs"] == 3
    assert db_session.query(LogEntry).count() == 3
