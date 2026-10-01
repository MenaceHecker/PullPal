from app.tools.schemas import PostStatusUpdateInput, RestartServiceInput, RollbackDeployInput
from app.tools.side_effecting import post_status_update, restart_service, rollback_deploy
from sqlalchemy.orm import Session


def test_restart_service_describes_the_action_without_doing_anything(db_session: Session) -> None:
    result = restart_service(db_session, RestartServiceInput(service="checkout-service", reason="error spike"))
    assert result == {
        "action": "restart_service",
        "service": "checkout-service",
        "reason": "error spike",
    }


def test_rollback_deploy_describes_the_action(db_session: Session) -> None:
    result = rollback_deploy(
        db_session,
        RollbackDeployInput(service="checkout-service", target_sha="abc123", reason="bad deploy"),
    )
    assert result == {
        "action": "rollback_deploy",
        "service": "checkout-service",
        "target_sha": "abc123",
        "reason": "bad deploy",
    }


def test_post_status_update_describes_the_action(db_session: Session) -> None:
    result = post_status_update(db_session, PostStatusUpdateInput(message="investigating checkout errors"))
    assert result == {
        "action": "post_status_update",
        "message": "investigating checkout errors",
    }
