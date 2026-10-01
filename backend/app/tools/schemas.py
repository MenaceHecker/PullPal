from datetime import datetime

from pydantic import BaseModel, Field


class QueryLogsInput(BaseModel):
    service: str
    start_time: datetime | None = None
    end_time: datetime | None = None
    level: str | None = None
    limit: int = Field(default=50, le=500)


class GetMetricsInput(BaseModel):
    service: str
    metric_name: str
    start_time: datetime | None = None
    end_time: datetime | None = None


class GetRecentDeploysInput(BaseModel):
    service: str
    start_time: datetime | None = None
    end_time: datetime | None = None
    limit: int = Field(default=10, le=100)


class SearchRunbooksInput(BaseModel):
    query: str
    top_k: int = Field(default=5, le=20)


class GetServiceStatusInput(BaseModel):
    service: str


class RestartServiceInput(BaseModel):
    service: str
    reason: str


class RollbackDeployInput(BaseModel):
    service: str
    target_sha: str
    reason: str


class PostStatusUpdateInput(BaseModel):
    message: str
