from dataclasses import dataclass


@dataclass(frozen=True)
class Scenario:
    id: str
    title: str
    service: str
    description: str
    error_rate: float
    latency_multiplier: float
    error_log_messages: list[str]
    deploy_message: str | None


SCENARIOS: dict[str, Scenario] = {
    "checkout-500s": Scenario(
        id="checkout-500s",
        title="Checkout returning 500s",
        service="checkout-service",
        description=(
            "A bad deploy ships without validating the new shipping_method field, "
            "so any checkout request missing it blows up with a 500."
        ),
        error_rate=0.35,
        latency_multiplier=1.1,
        error_log_messages=[
            "500 Internal Server Error handling POST /checkout: KeyError: 'shipping_method'",
            "Unhandled exception in checkout flow: 'shipping_method' not found in request body",
            "OrderCreationError: missing required field shipping_method for order {order_id}",
        ],
        deploy_message="Add shipping method to checkout request schema",
    ),
    "payments-timeout": Scenario(
        id="payments-timeout",
        title="Payments provider timing out",
        service="payments-service",
        description=(
            "A connection pool size change leaves payments-service unable to keep up "
            "with the payment provider, so a growing share of requests time out."
        ),
        error_rate=0.22,
        latency_multiplier=4.5,
        error_log_messages=[
            "Timeout calling payment-provider after 30000ms for charge {order_id}",
            "ConnectionPoolExhausted: no available connections to payment-provider",
            "Retry limit exceeded charging card for order {order_id}, giving up",
        ],
        deploy_message="Reduce payment-provider connection pool size",
    ),
    "inventory-oom": Scenario(
        id="inventory-oom",
        title="Inventory service getting OOM killed",
        service="inventory-service",
        description=(
            "A memory leak introduced in the stock-reservation cache causes the "
            "process to slowly grow until it gets killed and restarted under load."
        ),
        error_rate=0.18,
        latency_multiplier=1.6,
        error_log_messages=[
            "OOMKilled: inventory-worker exceeded memory limit (512Mi)",
            "Process restarted unexpectedly while reserving stock for order {order_id}",
            "Failed to reserve inventory for order {order_id}: worker unavailable",
        ],
        deploy_message="Cache stock-reservation lookups in memory",
    ),
}
