import os

# Keep the background tick loop from firing mid-test. Startup still runs one
# tick immediately (see app/main.py), which is all tests rely on.
os.environ.setdefault("TICK_INTERVAL_SECONDS", "999")

from collections.abc import Generator  # noqa: E402

import pytest  # noqa: E402
from app.main import app  # noqa: E402
from app.state import store  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    # store is a module-level singleton, so wipe it before each test rather
    # than after: that way lifespan startup (seed + first tick) always runs
    # against a clean slate.
    for service_state in store.services.values():
        service_state.active_scenario = None
        service_state.logs.clear()
        service_state.metrics.clear()
        service_state.deploys.clear()

    with TestClient(app) as test_client:
        yield test_client
