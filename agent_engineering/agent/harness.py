from __future__ import annotations

import json
from typing import Any
from uuid import uuid4

from agent.model import ModelClient, parse_model_output
from agent.skill_loader import SkillLoader
from db.repository import Repository
from tools.bohrium import BohriumCLI, ToolExecutionError


class AgentHarness:
    """A runnable baseline with intentional reliability gaps for the exercise."""

    def __init__(
        self,
        repository: Repository,
        model: ModelClient,
        skills: SkillLoader,
        bohrium: BohriumCLI,
        poll_limit: int = 3,
    ):
        self.repository = repository
        self.model = model
        self.skills = skills
        self.bohrium = bohrium
        self.poll_limit = poll_limit

    def create_run(self, message: str, client_request_id: str | None = None) -> str:
        return self.repository.create_run(message, client_request_id)

    def start(self, message: str, client_request_id: str | None = None) -> str:
        run_id = self.create_run(message, client_request_id)
        self.execute(run_id, message, client_request_id)
        return run_id

    def execute(
        self, run_id: str, message: str, client_request_id: str | None = None
    ) -> None:
        request_id = client_request_id or str(uuid4())
        self.repository.update_run(run_id, "RUNNING")

        loaded_skills = self.skills.load_all()
        self.repository.add_event(
            run_id,
            "skills_loaded",
            {
                "skills": [
                    {"name": skill.name, "version": skill.version}
                    for skill in loaded_skills
                ]
            },
        )
        skill_prompt = "\n\n".join(skill.content for skill in loaded_skills)
        messages = [
            {"role": "system", "content": skill_prompt},
            {"role": "user", "content": message},
        ]
        last_spec: dict[str, Any] | None = None
        step = 0

        try:
            while True:
                step += 1
                if step > 12:
                    raise RuntimeError("baseline safety stop after 12 steps")
                model_output = self.model.complete(messages)
                self.repository.add_event(
                    run_id,
                    "model_output",
                    {"model": self.model.name, "step": step, "output": model_output},
                )
                action = parse_model_output(model_output)
                if action.kind == "final":
                    answer = action.text or ""
                    status = "NEEDS_INPUT" if "请补充" in answer else "COMPLETED"
                    self.repository.update_run(run_id, status, answer)
                    return

                arguments = action.arguments or {}
                if action.name == "submit_job":
                    last_spec = dict(arguments)
                    result = self._submit_with_naive_retry(
                        run_id, request_id, last_spec
                    )
                    job_id = result["job_id"]
                    self.repository.add_job(
                        run_id,
                        job_id,
                        request_id,
                        result["status"],
                        last_spec,
                    )
                    terminal = self._poll_job(run_id, job_id)
                    if terminal == "FAILED":
                        log_result = self.bohrium.logs(job_id)
                        self.repository.add_event(run_id, "tool_result", log_result)
                        messages.append(
                            {
                                "role": "system",
                                "content": "OBSERVATION "
                                + json.dumps(
                                    {
                                        "kind": "job_logs",
                                        "job_id": job_id,
                                        "logs": log_result["logs"],
                                        "last_spec": last_spec,
                                    }
                                ),
                            }
                        )
                        continue
                    if terminal in {"SUCCEEDED", "CANCELLED"}:
                        messages.append(
                            {
                                "role": "user",
                                "content": "OBSERVATION "
                                + json.dumps(
                                    {
                                        "kind": "job_status",
                                        "job_id": job_id,
                                        "status": terminal,
                                    }
                                ),
                            }
                        )
                        continue
                    self.repository.update_run(
                        run_id, "RUNNING", f"任务 {job_id} 仍在运行"
                    )
                    return

                if action.name == "cancel_job":
                    job_id = str(arguments["job_id"])
                    result = self.bohrium.cancel(job_id)
                    self.repository.add_event(run_id, "tool_result", result)
                    self.repository.update_job(job_id, "CANCELLED")
                    self.repository.update_run(
                        run_id, "CANCELLED", f"任务 {job_id} 已取消"
                    )
                    return

                raise ValueError(f"unknown tool requested by model: {action.name}")
        except Exception as exc:
            self.repository.add_event(
                run_id,
                "run_failed",
                {"error_type": type(exc).__name__, "message": str(exc)},
            )
            self.repository.update_run(run_id, "FAILED", str(exc))

    def _submit_with_naive_retry(
        self, run_id: str, request_id: str, spec: dict[str, Any]
    ) -> dict[str, Any]:
        self.repository.add_event(
            run_id, "tool_call", {"tool": "submit_job", "arguments": spec}
        )
        try:
            result = self.bohrium.submit(spec, request_id)
        except ToolExecutionError as exc:
            self.repository.add_event(
                run_id,
                "tool_error",
                {"tool": "submit_job", "kind": exc.kind, "message": str(exc)},
            )
            result = self.bohrium.submit(spec, request_id)
        self.repository.add_event(run_id, "tool_result", result)
        return result

    def _poll_job(self, run_id: str, job_id: str) -> str:
        status = "QUEUED"
        for _ in range(self.poll_limit):
            result = self.bohrium.status(job_id)
            status = result["status"]
            self.repository.add_event(run_id, "tool_result", result)
            self.repository.update_job(job_id, status)
            if status in {"SUCCEEDED", "FAILED", "CANCELLED"}:
                return status
        return status

    def resume(self, run_id: str) -> None:
        self.repository.add_event(run_id, "resume_requested", {})
        raise NotImplementedError("resume is not implemented in the starter harness")
