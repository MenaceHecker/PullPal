import random
import string
from collections import deque
from dataclasses import dataclass, field
from datetime import UTC, datetime

from app.config import get_settings

settings = get_settings()

SERVICE_NAMES = ["checkout-service", "payments-service", "inventory-service"]


@dataclass
class LogEntry:
    timestamp: datetime
    service: str
    level: str
    message: str
    trace_id: str


@dataclass
class MetricPoint:
    timestamp: datetime
    service: str
    metric_name: str
    value: float


@dataclass
class Deploy:
    sha: str
    service: str
    message: str
    deployed_at: datetime
    deployed_by: str


@dataclass
class ActiveScenario:
    scenario_id: str
    injected_at: datetime


@dataclass
class ServiceState:
    name: str
    description: str
    logs: deque[LogEntry] = field(default_factory=lambda: deque(maxlen=settings.log_buffer_size))
    metrics: deque[MetricPoint] = field(default_factory=lambda: deque(maxlen=settings.metric_buffer_size))
    deploys: list[Deploy] = field(default_factory=list)
    active_scenario: ActiveScenario | None = None


def random_sha(length: int = 7) -> str:
    return "".join(random.choices(string.hexdigits.lower()[:16], k=length))


class Store:
    """Holds everything in memory. This is a live demo system, not a database,
    so a restart just goes back to a fresh healthy baseline."""

    def __init__(self) -> None:
        self.services: dict[str, ServiceState] = {
            "checkout-service": ServiceState(
                name="checkout-service",
                description="Handles cart checkout and order creation.",
            ),
            "payments-service": ServiceState(
                name="payments-service",
                description="Talks to the payment provider and records charges.",
            ),
            "inventory-service": ServiceState(
                name="inventory-service",
                description="Tracks stock levels and reserves inventory for orders.",
            ),
        }

    def get(self, service_name: str) -> ServiceState | None:
        return self.services.get(service_name)


store = Store()


def now() -> datetime:
    return datetime.now(UTC)
