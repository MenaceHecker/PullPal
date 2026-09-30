import random
import uuid

from app.scenarios import SCENARIOS
from app.state import LogEntry, MetricPoint, ServiceState, Store, now

BASELINE_ERROR_RATE = 0.01
BASELINE_LATENCY_P50_MS = 110.0
BASELINE_REQUEST_COUNT_RANGE = (30, 70)

INFO_MESSAGES = [
    "request completed",
    "healthcheck ok",
    "processed order {order_id}",
    "cache hit for key order:{order_id}",
]

BASELINE_ERROR_MESSAGES = [
    "request to downstream dependency failed, retrying",
    "validation error on request body",
]


def _fake_order_id() -> str:
    return str(random.randint(10000, 99999))


def _pick_message(templates: list[str]) -> str:
    return random.choice(templates).format(order_id=_fake_order_id())


def _tick_service(service_state: ServiceState) -> None:
    timestamp = now()
    scenario = SCENARIOS[service_state.active_scenario.scenario_id] if service_state.active_scenario else None

    error_rate = scenario.error_rate if scenario else BASELINE_ERROR_RATE
    latency_multiplier = scenario.latency_multiplier if scenario else 1.0

    request_count = random.randint(*BASELINE_REQUEST_COUNT_RANGE)
    # Small jitter so the line isn't perfectly flat, but stays close to the target.
    jittered_error_rate = max(0.0, min(1.0, error_rate + random.uniform(-0.02, 0.02)))
    latency_p50_ms = BASELINE_LATENCY_P50_MS * latency_multiplier * random.uniform(0.9, 1.1)

    service_state.metrics.append(
        MetricPoint(timestamp=timestamp, service=service_state.name, metric_name="request_count", value=request_count)
    )
    service_state.metrics.append(
        MetricPoint(
            timestamp=timestamp, service=service_state.name, metric_name="error_rate", value=jittered_error_rate
        )
    )
    service_state.metrics.append(
        MetricPoint(timestamp=timestamp, service=service_state.name, metric_name="latency_p50_ms", value=latency_p50_ms)
    )

    error_log_count = round(request_count * jittered_error_rate)
    info_log_count = max(1, round(request_count * 0.05))

    for _ in range(info_log_count):
        service_state.logs.append(
            LogEntry(
                timestamp=timestamp,
                service=service_state.name,
                level="INFO",
                message=_pick_message(INFO_MESSAGES),
                trace_id=str(uuid.uuid4()),
            )
        )

    error_templates = scenario.error_log_messages if scenario else BASELINE_ERROR_MESSAGES
    for _ in range(error_log_count):
        service_state.logs.append(
            LogEntry(
                timestamp=timestamp,
                service=service_state.name,
                level="ERROR",
                message=_pick_message(error_templates),
                trace_id=str(uuid.uuid4()),
            )
        )


def tick(store: Store) -> None:
    """Generates one batch of logs and metrics for every service. Called on a
    timer by the background loop in main.py."""
    for service_state in store.services.values():
        _tick_service(service_state)
