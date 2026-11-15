"""Shared state for the Agentic SDLC workflow."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from uuid import uuid4


class Status(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    APPROVAL_REQUIRED = "approval_required"


@dataclass
class WorkflowState:
    requirement: str
    run_id: str = field(
        default_factory=lambda: str(uuid4())
    )
    status: Status = Status.PENDING
    current_stage: str = "initialization"
    artifacts: dict = field(default_factory=dict)
    history: list = field(default_factory=list)
    errors: list = field(default_factory=list)

    def record_event(self, stage: str, message: str):
        self.history.append({
            "timestamp": datetime.now(
                UTC
            ).isoformat(),
            "stage": stage,
            "message": message,
        })
