from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class ToolExecutionError(RuntimeError):
    command: list[str]
    exit_code: int
    stdout: str
    stderr: str

    @property
    def kind(self) -> str:
        return "timeout" if self.exit_code == 124 else "tool_error"

    def __str__(self) -> str:
        return f"{self.kind}: exit={self.exit_code} stderr={self.stderr.strip()}"


class BohriumCLI:
    def __init__(self, cli_path: Path, state_path: Path, timeout_seconds: int = 10):
        self.cli_path = Path(cli_path)
        self.state_path = Path(state_path)
        self.timeout_seconds = timeout_seconds

    def _invoke(self, arguments: list[str]) -> dict[str, Any]:
        command = [sys.executable, str(self.cli_path), *arguments]
        env = os.environ.copy()
        env["MOCK_BOH_STATE"] = str(self.state_path)
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=self.timeout_seconds,
            env=env,
            check=False,
        )
        if completed.returncode != 0:
            raise ToolExecutionError(
                command=command,
                exit_code=completed.returncode,
                stdout=completed.stdout,
                stderr=completed.stderr,
            )
        return json.loads(completed.stdout)

    def submit(self, spec: dict[str, Any], request_id: str) -> dict[str, Any]:
        return self._invoke(
            [
                "submit",
                "--request-id",
                request_id,
                "--image",
                str(spec["image"]),
                "--command",
                str(spec["command"]),
                "--cpu",
                str(spec["cpu"]),
                "--memory-gb",
                str(spec["memory_gb"]),
                "--scenario",
                str(spec.get("scenario", "happy")),
            ]
        )

    def status(self, job_id: str) -> dict[str, Any]:
        return self._invoke(["status", "--job-id", job_id])

    def logs(self, job_id: str) -> dict[str, Any]:
        return self._invoke(["logs", "--job-id", job_id])

    def cancel(self, job_id: str) -> dict[str, Any]:
        return self._invoke(["cancel", "--job-id", job_id])

    def find(self, request_id: str) -> dict[str, Any]:
        return self._invoke(["find", "--request-id", request_id])

    def dump(self) -> dict[str, Any]:
        return self._invoke(["dump"])

    def reset(self) -> dict[str, Any]:
        return self._invoke(["reset"])
