from datetime import datetime

from fastapi import APIRouter, Depends, Query

from app.deps import get_service_or_404
from app.schemas import MetricPointOut
from app.state import ServiceState

router = APIRouter(prefix="/services/{service_name}/metrics", tags=["metrics"])


@router.get("", response_model=list[MetricPointOut])
def query_metrics(
    metric_name: str | None = Query(default=None, description="e.g. error_rate, latency_p50_ms, request_count"),
    start_time: datetime | None = Query(default=None),
    end_time: datetime | None = Query(default=None),
    limit: int = Query(default=500, le=5000),
    service_state: ServiceState = Depends(get_service_or_404),
) -> list[MetricPointOut]:
    points = list(service_state.metrics)

    if metric_name is not None:
        points = [point for point in points if point.metric_name == metric_name]
    if start_time is not None:
        points = [point for point in points if point.timestamp >= start_time]
    if end_time is not None:
        points = [point for point in points if point.timestamp <= end_time]

    points.sort(key=lambda point: point.timestamp)
    return points[-limit:]
