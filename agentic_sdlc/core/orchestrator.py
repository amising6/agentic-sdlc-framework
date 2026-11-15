"""Core orchestration engine."""

from collections.abc import Callable

from agentic_sdlc.core.state import (
    Status,
    WorkflowState,
)


class Orchestrator:
    def __init__(self):
        self.stages = []

    def register(
        self,
        name: str,
        handler: Callable[[WorkflowState], None],
    ):
        self.stages.append((name, handler))

    def run(
        self,
        state: WorkflowState,
    ) -> WorkflowState:

        state.status = Status.RUNNING

        for name, handler in self.stages:
            state.current_stage = name
            state.record_event(name, "Stage started")

            try:
                handler(state)

                if state.status in (
                    Status.FAILED,
                    Status.APPROVAL_REQUIRED,
                ):
                    state.record_event(
                        name, state.status.value
                    )
                    return state

                state.record_event(
                    name, "Stage completed"
                )

            # Capture stage failures at the workflow boundary.
            except Exception as exc:  # noqa: BLE001
                state.status = Status.FAILED
                state.errors.append(str(exc))
                state.record_event(name, "Stage failed")
                return state

        state.status = Status.COMPLETED
        state.current_stage = "finished"
        return state
