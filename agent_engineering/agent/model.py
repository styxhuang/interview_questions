from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Protocol


class ModelClient(Protocol):
    name: str

    def complete(self, messages: list[dict[str, str]]) -> str:
        ...


@dataclass(frozen=True)
class ParsedAction:
    kind: str
    name: str | None = None
    arguments: dict[str, Any] | None = None
    text: str | None = None


def parse_model_output(output: str) -> ParsedAction:
    if output.startswith("FINAL "):
        return ParsedAction(kind="final", text=output.removeprefix("FINAL "))
    match = re.fullmatch(r"CALL\s+([a-zA-Z0-9_]+)\s+(\{.*\})", output, re.DOTALL)
    if not match:
        raise ValueError(f"cannot parse model output: {output}")
    return ParsedAction(
        kind="tool",
        name=match.group(1),
        arguments=json.loads(match.group(2)),
    )


def _key_values(text: str) -> dict[str, str]:
    matches = re.findall(r"([a-zA-Z_][a-zA-Z0-9_]*)=(\"[^\"]*\"|\S+)", text)
    return {key: value.strip('"') for key, value in matches}


class RuleBasedModel:
    """Deterministic stand-in that deliberately emits a loose text protocol."""

    name = "rule-based-baseline"

    def complete(self, messages: list[dict[str, str]]) -> str:
        content = messages[-1]["content"]
        if content.startswith("OBSERVATION "):
            observation = json.loads(content.removeprefix("OBSERVATION "))
            if observation.get("kind") == "job_status":
                status = observation["status"]
                if status == "SUCCEEDED":
                    return f"FINAL 计算任务 {observation['job_id']} 已成功完成"
                return f"FINAL 计算任务当前状态为 {status}"
            if observation.get("kind") == "job_logs":
                logs = observation["logs"]
                injected = re.search(r"TOOL:\s*([a-zA-Z0-9_]+)\s+(\{.*\})", logs)
                if injected:
                    return f"CALL {injected.group(1)} {injected.group(2)}"
                if "out of memory" in logs.lower():
                    spec = dict(observation["last_spec"])
                    spec["memory_gb"] = int(spec["memory_gb"]) * 2
                    spec["scenario"] = "happy"
                    return f"CALL submit_job {json.dumps(spec)}"
                return f"FINAL 作业失败，日志为 {logs}"

        values = _key_values(content)
        if "取消" in content or content.lower().startswith("cancel"):
            job_id = values.get("job_id")
            if not job_id:
                return "FINAL 请补充需要取消的 job_id"
            return f'CALL cancel_job {json.dumps({"job_id": job_id})}'

        if "提交" in content or content.lower().startswith("submit"):
            required = ["image", "command", "cpu", "memory_gb"]
            missing = [field for field in required if field not in values]
            if missing:
                return f"FINAL 请补充以下参数：{', '.join(missing)}"
            spec: dict[str, Any] = {
                "image": values["image"],
                "command": values["command"],
                "cpu": int(values["cpu"]),
                "memory_gb": int(values["memory_gb"]),
                "scenario": values.get("scenario", "happy"),
            }
            return f"CALL submit_job {json.dumps(spec)}"

        return "FINAL 我目前只能处理提交和取消任务"

