from datetime import UTC, datetime, timedelta

import pytest
from app.embeddings import FakeEmbeddingProvider
from app.models import Deploy, LogEntry, MetricPoint, Service
from app.runbooks import ingest_all_runbooks
from app.seed import seed_services
from app.tools.read_only import (
    get_metrics,
    get_recent_deploys,
    get_service_status,
    query_logs,
    search_runbooks,
)
from app.tools.schemas import (
    GetMetricsInput,
    GetRecentDeploysInput,
    GetServiceStatusInput,
    QueryLogsInput,
    SearchRunbooksInput,
)
from sqlalchemy.orm import Session

T0 = datetime(2026, 9, 30, 12, 0, 0, tzinfo=UTC)


def _checkout_service(db_session: Session) -> Service:
    seed_services(db_session)
    return db_session.query(Service).filter(Service.name == "checkout-service").one()


def test_query_logs_returns_matching_entries(db_session: Session) -> None:
    service = _checkout_service(db_session)
    db_session.add_all(
        [
            LogEntry(service_id=service.id, timestamp=T0, level="INFO", message="ok", trace_id="1"),
            LogEntry(
                service_id=service.id, timestamp=T0 + timedelta(seconds=1), level="ERROR", message="bad", trace_id="2"
            ),
        ]
    )
    db_session.commit()

    result = query_logs(db_session, QueryLogsInput(service="checkout-service"))

    assert result["count"] == 2
    assert result["logs"][0]["message"] == "bad"  # newest first


def test_query_logs_filters_by_level(db_session: Session) -> None:
    service = _checkout_service(db_session)
    db_session.add_all(
        [
            LogEntry(service_id=service.id, timestamp=T0, level="INFO", message="ok", trace_id="1"),
            LogEntry(service_id=service.id, timestamp=T0, level="ERROR", message="bad", trace_id="2"),
        ]
    )
    db_session.commit()

    result = query_logs(db_session, QueryLogsInput(service="checkout-service", level="error"))

    assert result["count"] == 1
    assert result["logs"][0]["level"] == "ERROR"


def test_query_logs_raises_on_unknown_service(db_session: Session) -> None:
    seed_services(db_session)
    with pytest.raises(ValueError, match="Unknown service"):
        query_logs(db_session, QueryLogsInput(service="does-not-exist"))


def test_get_metrics_returns_points_in_chronological_order(db_session: Session) -> None:
    service = _checkout_service(db_session)
    db_session.add_all(
        [
            MetricPoint(
                service_id=service.id, timestamp=T0 + timedelta(seconds=2), metric_name="error_rate", value=0.02
            ),
            MetricPoint(service_id=service.id, timestamp=T0, metric_name="error_rate", value=0.01),
        ]
    )
    db_session.commit()

    result = get_metrics(db_session, GetMetricsInput(service="checkout-service", metric_name="error_rate"))

    assert result["count"] == 2
    assert result["points"][0]["value"] == 0.01  # oldest first


def test_get_recent_deploys_orders_newest_first_and_respects_limit(db_session: Session) -> None:
    service = _checkout_service(db_session)
    db_session.add_all(
        [
            Deploy(service_id=service.id, sha="a1", message="one", deployed_at=T0, deployed_by="alice"),
            Deploy(
                service_id=service.id,
                sha="a2",
                message="two",
                deployed_at=T0 + timedelta(hours=1),
                deployed_by="bob",
            ),
        ]
    )
    db_session.commit()

    result = get_recent_deploys(db_session, GetRecentDeploysInput(service="checkout-service", limit=1))

    assert result["count"] == 1
    assert result["deploys"][0]["sha"] == "a2"


def test_get_service_status_unknown_with_no_metrics(db_session: Session) -> None:
    _checkout_service(db_session)
    result = get_service_status(db_session, GetServiceStatusInput(service="checkout-service"))
    assert result["status"] == "unknown"


def test_get_service_status_healthy_below_threshold(db_session: Session) -> None:
    service = _checkout_service(db_session)
    db_session.add(MetricPoint(service_id=service.id, timestamp=T0, metric_name="error_rate", value=0.01))
    db_session.commit()

    result = get_service_status(db_session, GetServiceStatusInput(service="checkout-service"))
    assert result["status"] == "healthy"


def test_get_service_status_degraded_above_threshold(db_session: Session) -> None:
    service = _checkout_service(db_session)
    db_session.add(MetricPoint(service_id=service.id, timestamp=T0, metric_name="error_rate", value=0.35))
    db_session.commit()

    result = get_service_status(db_session, GetServiceStatusInput(service="checkout-service"))
    assert result["status"] == "degraded"


def test_search_runbooks_finds_the_matching_section(db_session: Session) -> None:
    ingest_all_runbooks(db_session, FakeEmbeddingProvider())

    result = search_runbooks(db_session, SearchRunbooksInput(query="shipping_method checkout 500", top_k=3))

    assert result["count"] == 3
    assert result["results"][0]["document_title"] == "Checkout Service"
