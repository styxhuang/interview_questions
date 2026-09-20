from pathlib import Path

from fastapi.testclient import TestClient

from app.config import PROJECT_ROOT, Settings
from app.main import create_app


def test_api_can_submit_and_read_a_run(tmp_path: Path):
    settings = Settings(
        database_url=f"sqlite:///{(tmp_path / 'api.db').as_posix()}",
        mock_cli_path=PROJECT_ROOT / "mock_boh_cli" / "boh.py",
        mock_state_path=tmp_path / "mock_state.json",
        poll_limit=3,
    )
    client = TestClient(create_app(settings))
    response = client.post(
        "/v1/runs",
        json={
            "message": "提交任务 image=python:3.11 command=main.py cpu=2 memory_gb=4 scenario=happy",
            "client_request_id": "api-test",
        },
    )
    assert response.status_code == 202
    run_id = response.json()["run_id"]
    run = client.get(f"/v1/runs/{run_id}")
    assert run.status_code == 200
    assert run.json()["status"] == "COMPLETED"
    assert len(run.json()["jobs"]) == 1

