from sqlalchemy.orm import Session

from app.tools.schemas import PostStatusUpdateInput, RestartServiceInput, RollbackDeployInput

# These describe what the action would do. None of them actually touch the
# simulated system yet, that's Phase 6 (the approval workflow), once a
# human has approved the proposal this function's output represents. The
# executor never even calls these for a side-effecting tool, they exist so
# Phase 6 has a single place to call once approval is wired up.


def restart_service(db: Session, params: RestartServiceInput) -> dict:
    return {
        "action": "restart_service",
        "service": params.service,
        "reason": params.reason,
    }


def rollback_deploy(db: Session, params: RollbackDeployInput) -> dict:
    return {
        "action": "rollback_deploy",
        "service": params.service,
        "target_sha": params.target_sha,
        "reason": params.reason,
    }


def post_status_update(db: Session, params: PostStatusUpdateInput) -> dict:
    return {
        "action": "post_status_update",
        "message": params.message,
    }
