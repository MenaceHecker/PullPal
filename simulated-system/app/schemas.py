from datetime import datetime

from pydantic import BaseModel


class ServiceOut(BaseModel):
    name: str
    description: str
    status: str  # healthy | degraded
    active_scenario_id: str | None = None


class LogEntryOut(BaseModel):
    timestamp: datetime
    service: str
    level: str
    message: str
    trace_id: str


class MetricPointOut(BaseModel):
    timestamp: datetime
    service: str
    metric_name: str
    value: float


class DeployOut(BaseModel):
    sha: str
    service: str
    message: str
    deployed_at: datetime
    deployed_by: str


class ScenarioOut(BaseModel):
    id: str
    title: str
    service: str
    description: str
    active: bool


class InjectScenarioResponse(BaseModel):
    scenario_id: str
    service: str
    injected_at: datetime
    deploy: DeployOut | None = None
