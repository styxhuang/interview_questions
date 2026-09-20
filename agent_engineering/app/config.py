from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Settings:
    database_url: str
    mock_cli_path: Path
    mock_state_path: Path
    poll_limit: int = 3


def get_settings() -> Settings:
    var_dir = PROJECT_ROOT / "var"
    var_dir.mkdir(parents=True, exist_ok=True)
    return Settings(
        database_url=os.getenv(
            "DATABASE_URL", f"sqlite:///{(var_dir / 'agent.db').as_posix()}"
        ),
        mock_cli_path=Path(
            os.getenv("BOHRIUM_CLI_PATH", PROJECT_ROOT / "mock_boh_cli" / "boh.py")
        ),
        mock_state_path=Path(
            os.getenv("MOCK_BOH_STATE", var_dir / "mock_bohrium_state.json")
        ),
        poll_limit=int(os.getenv("AGENT_POLL_LIMIT", "3")),
    )

