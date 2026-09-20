from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class RunCreate(BaseModel):
    message: str = Field(min_length=1)
    client_request_id: Optional[str] = None


class RunCreated(BaseModel):
    run_id: str
    status: str


class ApprovalRequest(BaseModel):
    approved: bool
    note: Optional[str] = None


class RunView(BaseModel):
    id: str
    client_request_id: Optional[str]
    message: str
    status: str
    final_answer: Optional[str]
    events: list[dict[str, Any]]
    jobs: list[dict[str, Any]]
    approvals: list[dict[str, Any]]
