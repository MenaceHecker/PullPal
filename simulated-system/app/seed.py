from datetime import timedelta

from app.state import Deploy, Store, now, random_sha

DEPLOY_MESSAGES = [
    "Bump dependency versions",
    "Add request timeout metric",
    "Refactor retry logic",
    "Tune connection pool size",
    "Add structured logging for order events",
    "Improve error messages on validation failure",
    "Update health check thresholds",
    "Small perf tweak to hot path",
]

DEPLOYERS = ["alice", "bob", "carol", "dave", "erin"]


def seed_deploy_history(store: Store, deploys_per_service: int = 6) -> None:
    """Backfills each service with a handful of realistic-looking past deploys,
    spread over the last few days, so there's deploy history to correlate
    incidents against even before any failure scenario has been injected."""
    reference_time = now()

    for index, service_state in enumerate(store.services.values()):
        for deploy_index in range(deploys_per_service):
            hours_ago = (deploys_per_service - deploy_index) * 7 + index
            service_state.deploys.append(
                Deploy(
                    sha=random_sha(),
                    service=service_state.name,
                    message=DEPLOY_MESSAGES[(index + deploy_index) % len(DEPLOY_MESSAGES)],
                    deployed_at=reference_time - timedelta(hours=hours_ago),
                    deployed_by=DEPLOYERS[(index + deploy_index) % len(DEPLOYERS)],
                )
            )
