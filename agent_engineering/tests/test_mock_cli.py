from pathlib import Path

from app.config import PROJECT_ROOT
from tools.bohrium import BohriumCLI


def test_mock_cli_happy_path(tmp_path: Path):
    tool = BohriumCLI(
        PROJECT_ROOT / "mock_boh_cli" / "boh.py", tmp_path / "state.json"
    )
    tool.reset()
    submitted = tool.submit(
        {
            "image": "python:3.11",
            "command": "main.py",
            "cpu": 2,
            "memory_gb": 4,
            "scenario": "happy",
        },
        "request-1",
    )
    assert submitted["status"] == "QUEUED"
    assert tool.status(submitted["job_id"])["status"] == "QUEUED"
    assert tool.status(submitted["job_id"])["status"] == "RUNNING"
    assert tool.status(submitted["job_id"])["status"] == "SUCCEEDED"

