from __future__ import annotations

from fastapi import BackgroundTasks, FastAPI, HTTPException, status

from agent.harness import AgentHarness
from agent.model import RuleBasedModel
from agent.skill_loader import SkillLoader
from app.config import PROJECT_ROOT, Settings, get_settings
from app.schemas import ApprovalRequest, RunCreate, RunCreated, RunView
from db.database import build_engine, build_session_factory, init_database
from db.repository import Repository
from tools.bohrium import BohriumCLI


def create_app(settings: Settings | None = None) -> FastAPI:
    runtime_settings = settings or get_settings()
    engine = build_engine(runtime_settings.database_url)
    init_database(engine)
    repository = Repository(build_session_factory(engine))
    bohrium = BohriumCLI(
        runtime_settings.mock_cli_path, runtime_settings.mock_state_path
    )
    harness = AgentHarness(
        repository=repository,
        model=RuleBasedModel(),
        skills=SkillLoader(PROJECT_ROOT / "skills"),
        bohrium=bohrium,
        poll_limit=runtime_settings.poll_limit,
    )

    api = FastAPI(title="Bohrium Agent Starter", version="0.1.0")
    api.state.repository = repository
    api.state.harness = harness
    api.state.engine = engine

    @api.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @api.post(
        "/v1/runs", response_model=RunCreated, status_code=status.HTTP_202_ACCEPTED
    )
    def create_run(payload: RunCreate, background_tasks: BackgroundTasks) -> RunCreated:
        run_id = harness.create_run(payload.message, payload.client_request_id)
        background_tasks.add_task(
            harness.execute, run_id, payload.message, payload.client_request_id
        )
        return RunCreated(run_id=run_id, status="PENDING")

    @api.get("/v1/runs/{run_id}", response_model=RunView)
    def get_run(run_id: str) -> RunView:
        run = repository.get_run(run_id)
        if run is None:
            raise HTTPException(status_code=404, detail="run not found")
        return RunView.model_validate(run)

    @api.post("/v1/runs/{run_id}/approve")
    def approve_run(run_id: str, payload: ApprovalRequest):
        if repository.get_run(run_id) is None:
            raise HTTPException(status_code=404, detail="run not found")
        raise HTTPException(
            status_code=501,
            detail={
                "message": "approval flow is not implemented in the starter",
                "approved": payload.approved,
            },
        )

    @api.post("/v1/runs/{run_id}/resume")
    def resume_run(run_id: str, background_tasks: BackgroundTasks):
        if repository.get_run(run_id) is None:
            raise HTTPException(status_code=404, detail="run not found")
        background_tasks.add_task(harness.resume, run_id)
        return {"run_id": run_id, "status": "RESUME_REQUESTED"}

    return api


app = create_app()

