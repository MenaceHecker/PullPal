from datetime import datetime

from fastapi import APIRouter, Depends, Query

from app.deps import get_service_or_404
from app.schemas import DeployOut
from app.state import ServiceState

router = APIRouter(prefix="/services/{service_name}/deploys", tags=["deploys"])


@router.get("", response_model=list[DeployOut])
def list_deploys(
    start_time: datetime | None = Query(default=None),
    end_time: datetime | None = Query(default=None),
    service_state: ServiceState = Depends(get_service_or_404),
) -> list[DeployOut]:
    deploys = service_state.deploys

    if start_time is not None:
        deploys = [deploy for deploy in deploys if deploy.deployed_at >= start_time]
    if end_time is not None:
        deploys = [deploy for deploy in deploys if deploy.deployed_at <= end_time]

    return sorted(deploys, key=lambda deploy: deploy.deployed_at, reverse=True)
