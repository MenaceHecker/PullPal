from fastapi import HTTPException, status

from app.state import ServiceState, store


def get_service_or_404(service_name: str) -> ServiceState:
    service_state = store.get(service_name)
    if service_state is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Unknown service: {service_name}")
    return service_state
