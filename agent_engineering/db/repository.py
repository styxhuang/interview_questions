from __future__ import annotations

from typing import Any
from uuid import uuid4

from sqlalchemy import select

from db.models import AgentRun, Approval, ComputeJob, RunEvent


class Repository:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def create_run(self, message: str, client_request_id: str | None = None) -> str:
        run_id = str(uuid4())
        with self.session_factory.begin() as session:
            session.add(
                AgentRun(
                    id=run_id,
                    client_request_id=client_request_id,
                    message=message,
                    status="PENDING",
                )
            )
        return run_id

    def update_run(
        self, run_id: str, status: str, final_answer: str | None = None
    ) -> None:
        with self.session_factory.begin() as session:
            run = session.get(AgentRun, run_id)
            if run is None:
                raise KeyError(f"unknown run: {run_id}")
            run.status = status
            if final_answer is not None:
                run.final_answer = final_answer

    def add_event(self, run_id: str, event_type: str, payload: dict[str, Any]) -> None:
        with self.session_factory.begin() as session:
            session.add(RunEvent(run_id=run_id, event_type=event_type, payload=payload))

    def add_job(
        self,
        run_id: str,
        provider_job_id: str,
        client_request_id: str | None,
        status: str,
        spec: dict[str, Any],
    ) -> None:
        with self.session_factory.begin() as session:
            session.add(
                ComputeJob(
                    run_id=run_id,
                    provider_job_id=provider_job_id,
                    client_request_id=client_request_id,
                    status=status,
                    spec=spec,
                )
            )

    def update_job(self, provider_job_id: str, status: str) -> None:
        with self.session_factory.begin() as session:
            job = session.scalar(
                select(ComputeJob).where(
                    ComputeJob.provider_job_id == provider_job_id
                )
            )
            if job is not None:
                job.status = status

    def create_approval(
        self, run_id: str, action: str, payload: dict[str, Any]
    ) -> int:
        with self.session_factory.begin() as session:
            approval = Approval(run_id=run_id, action=action, payload=payload)
            session.add(approval)
            session.flush()
            return approval.id

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        with self.session_factory() as session:
            run = session.get(AgentRun, run_id)
            if run is None:
                return None
            events = list(
                session.scalars(
                    select(RunEvent)
                    .where(RunEvent.run_id == run_id)
                    .order_by(RunEvent.id)
                )
            )
            jobs = list(
                session.scalars(
                    select(ComputeJob)
                    .where(ComputeJob.run_id == run_id)
                    .order_by(ComputeJob.id)
                )
            )
            approvals = list(
                session.scalars(
                    select(Approval)
                    .where(Approval.run_id == run_id)
                    .order_by(Approval.id)
                )
            )
            return {
                "id": run.id,
                "client_request_id": run.client_request_id,
                "message": run.message,
                "status": run.status,
                "final_answer": run.final_answer,
                "events": [
                    {
                        "id": event.id,
                        "type": event.event_type,
                        "payload": event.payload,
                    }
                    for event in events
                ],
                "jobs": [
                    {
                        "provider_job_id": job.provider_job_id,
                        "client_request_id": job.client_request_id,
                        "status": job.status,
                        "spec": job.spec,
                    }
                    for job in jobs
                ],
                "approvals": [
                    {
                        "id": approval.id,
                        "action": approval.action,
                        "status": approval.status,
                        "payload": approval.payload,
                    }
                    for approval in approvals
                ],
            }

