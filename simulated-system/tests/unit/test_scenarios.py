from fastapi.testclient import TestClient


def test_list_scenarios_returns_all_inactive_at_baseline(client: TestClient) -> None:
    response = client.get("/scenarios")
    assert response.status_code == 200

    scenarios = response.json()
    assert len(scenarios) >= 3
    assert all(scenario["active"] is False for scenario in scenarios)


def test_inject_unknown_scenario_returns_404(client: TestClient) -> None:
    response = client.post("/scenarios/does-not-exist/inject")
    assert response.status_code == 404


def test_inject_marks_service_degraded_and_creates_a_deploy(client: TestClient) -> None:
    response = client.post("/scenarios/checkout-500s/inject")
    assert response.status_code == 201

    body = response.json()
    assert body["service"] == "checkout-service"
    assert body["deploy"] is not None
    assert body["deploy"]["deployed_at"] < body["injected_at"]

    service = client.get("/services/checkout-service").json()
    assert service["status"] == "degraded"
    assert service["active_scenario_id"] == "checkout-500s"


def test_inject_produces_the_incident_signature(client: TestClient) -> None:
    client.post("/scenarios/checkout-500s/inject")

    # The generator only ticks once at startup plus once more here, but that's
    # enough for the elevated error rate and matching error logs to show up.
    from app.generator import tick
    from app.state import store

    tick(store)

    error_rate_points = client.get("/services/checkout-service/metrics?metric_name=error_rate").json()
    latest_error_rate = error_rate_points[-1]["value"]
    assert latest_error_rate > 0.2  # baseline is ~0.01, this scenario targets ~0.35

    error_logs = client.get("/services/checkout-service/logs?level=ERROR").json()
    assert len(error_logs) > 0
    assert any("shipping_method" in entry["message"] for entry in error_logs)


def test_reset_returns_service_to_healthy(client: TestClient) -> None:
    client.post("/scenarios/checkout-500s/inject")
    assert client.get("/services/checkout-service").json()["status"] == "degraded"

    reset_response = client.post("/scenarios/checkout-500s/reset")
    assert reset_response.status_code == 204

    service = client.get("/services/checkout-service").json()
    assert service["status"] == "healthy"
    assert service["active_scenario_id"] is None


def test_reset_unknown_scenario_returns_404(client: TestClient) -> None:
    response = client.post("/scenarios/does-not-exist/reset")
    assert response.status_code == 404


def test_injecting_one_scenario_does_not_affect_other_services(client: TestClient) -> None:
    client.post("/scenarios/checkout-500s/inject")

    payments = client.get("/services/payments-service").json()
    inventory = client.get("/services/inventory-service").json()
    assert payments["status"] == "healthy"
    assert inventory["status"] == "healthy"
