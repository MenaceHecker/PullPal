from fastapi import APIRouter, Depends

from app.deps import get_service_or_404
from app.schemas import ServiceOut
from app.state import ServiceState, store

router = APIRouter(prefix="/services", tags=["services"])


def _to_service_out(service_state: ServiceState) -> ServiceOut:
    return ServiceOut(
        name=service_state.name,
        description=service_state.description,
        status="degraded" if service_state.active_scenario else "healthy",
        active_scenario_id=service_state.active_scenario.scenario_id if service_state.active_scenario else None,
    )


@router.get("", response_model=list[ServiceOut])
def list_services() -> list[ServiceOut]:
    return [_to_service_out(service_state) for service_state in store.services.values()]


@router.get("/{service_name}", response_model=ServiceOut)
def get_service(service_state: ServiceState = Depends(get_service_or_404)) -> ServiceOut:
    return _to_service_out(service_state)
