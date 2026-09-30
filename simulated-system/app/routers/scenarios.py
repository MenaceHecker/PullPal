from datetime import timedelta

from fastapi import APIRouter, HTTPException, status

from app.scenarios import SCENARIOS, Scenario
from app.schemas import DeployOut, InjectScenarioResponse, ScenarioOut
from app.state import ActiveScenario, Deploy, now, random_sha, store

router = APIRouter(prefix="/scenarios", tags=["scenarios"])


def _get_scenario_or_404(scenario_id: str) -> Scenario:
    scenario = SCENARIOS.get(scenario_id)
    if scenario is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Unknown scenario: {scenario_id}")
    return scenario


@router.get("", response_model=list[ScenarioOut])
def list_scenarios() -> list[ScenarioOut]:
    return [
        ScenarioOut(
            id=scenario.id,
            title=scenario.title,
            service=scenario.service,
            description=scenario.description,
            active=(
                store.services[scenario.service].active_scenario is not None
                and store.services[scenario.service].active_scenario.scenario_id == scenario.id
            ),
        )
        for scenario in SCENARIOS.values()
    ]


@router.post("/{scenario_id}/inject", response_model=InjectScenarioResponse, status_code=status.HTTP_201_CREATED)
def inject_scenario(scenario_id: str) -> InjectScenarioResponse:
    scenario = _get_scenario_or_404(scenario_id)
    service_state = store.services[scenario.service]

    injected_at = now()
    service_state.active_scenario = ActiveScenario(scenario_id=scenario.id, injected_at=injected_at)

    deploy_out = None
    if scenario.deploy_message:
        # Backdate the deploy a few minutes before injection, so the deploy
        # that's "responsible" for the incident already shows up in history
        # by the time the error spike starts, same as a real incident.
        deploy = Deploy(
            sha=random_sha(),
            service=scenario.service,
            message=scenario.deploy_message,
            deployed_at=injected_at - timedelta(minutes=3),
            deployed_by="ci-bot",
        )
        service_state.deploys.append(deploy)
        deploy_out = DeployOut(
            sha=deploy.sha,
            service=deploy.service,
            message=deploy.message,
            deployed_at=deploy.deployed_at,
            deployed_by=deploy.deployed_by,
        )

    return InjectScenarioResponse(
        scenario_id=scenario.id,
        service=scenario.service,
        injected_at=injected_at,
        deploy=deploy_out,
    )


@router.post("/{scenario_id}/reset", status_code=status.HTTP_204_NO_CONTENT)
def reset_scenario(scenario_id: str) -> None:
    scenario = _get_scenario_or_404(scenario_id)
    service_state = store.services[scenario.service]

    if service_state.active_scenario is not None and service_state.active_scenario.scenario_id == scenario.id:
        service_state.active_scenario = None
