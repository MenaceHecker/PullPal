from app.tools.base import Tool
from app.tools.read_only import get_metrics, get_recent_deploys, get_service_status, query_logs, search_runbooks
from app.tools.schemas import (
    GetMetricsInput,
    GetRecentDeploysInput,
    GetServiceStatusInput,
    PostStatusUpdateInput,
    QueryLogsInput,
    RestartServiceInput,
    RollbackDeployInput,
    SearchRunbooksInput,
)
from app.tools.side_effecting import post_status_update, restart_service, rollback_deploy

_TOOL_LIST = [
    Tool(
        name="query_logs",
        description="Fetch log lines for a service within a time range.",
        is_side_effecting=False,
        input_model=QueryLogsInput,
        run=query_logs,
    ),
    Tool(
        name="get_metrics",
        description="Fetch metric data points for a service within a time range.",
        is_side_effecting=False,
        input_model=GetMetricsInput,
        run=get_metrics,
    ),
    Tool(
        name="get_recent_deploys",
        description="Fetch recent deploy history for a service.",
        is_side_effecting=False,
        input_model=GetRecentDeploysInput,
        run=get_recent_deploys,
    ),
    Tool(
        name="search_runbooks",
        description="Search runbook docs for content relevant to a query.",
        is_side_effecting=False,
        input_model=SearchRunbooksInput,
        run=search_runbooks,
    ),
    Tool(
        name="get_service_status",
        description="Get a service's current health, derived from its latest ingested error rate.",
        is_side_effecting=False,
        input_model=GetServiceStatusInput,
        run=get_service_status,
    ),
    Tool(
        name="restart_service",
        description="Propose restarting a service. Requires human approval before it executes.",
        is_side_effecting=True,
        input_model=RestartServiceInput,
        run=restart_service,
    ),
    Tool(
        name="rollback_deploy",
        description="Propose rolling a service back to a previous deploy. Requires human approval before it executes.",
        is_side_effecting=True,
        input_model=RollbackDeployInput,
        run=rollback_deploy,
    ),
    Tool(
        name="post_status_update",
        description="Propose posting a status update. Requires human approval before it executes.",
        is_side_effecting=True,
        input_model=PostStatusUpdateInput,
        run=post_status_update,
    ),
]

TOOLS: dict[str, Tool] = {tool.name: tool for tool in _TOOL_LIST}
