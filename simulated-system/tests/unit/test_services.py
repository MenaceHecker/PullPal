from fastapi.testclient import TestClient


def test_list_services_returns_all_three_healthy(client: TestClient) -> None:
    response = client.get("/services")
    assert response.status_code == 200

    services = response.json()
    names = {service["name"] for service in services}
    assert names == {"checkout-service", "payments-service", "inventory-service"}
    assert all(service["status"] == "healthy" for service in services)


def test_get_unknown_service_returns_404(client: TestClient) -> None:
    response = client.get("/services/does-not-exist")
    assert response.status_code == 404


def test_logs_are_generated_at_startup(client: TestClient) -> None:
    response = client.get("/services/checkout-service/logs")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_metrics_are_generated_at_startup(client: TestClient) -> None:
    response = client.get("/services/checkout-service/metrics?metric_name=error_rate")
    assert response.status_code == 200

    points = response.json()
    assert len(points) > 0
    assert all(point["metric_name"] == "error_rate" for point in points)


def test_deploy_history_is_seeded_at_startup(client: TestClient) -> None:
    response = client.get("/services/checkout-service/deploys")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_logs_for_unknown_service_returns_404(client: TestClient) -> None:
    response = client.get("/services/does-not-exist/logs")
    assert response.status_code == 404
