from agentic_sdlc.core.orchestrator import Orchestrator
from agentic_sdlc.core.state import Status, WorkflowState


def test_successful_workflow():
    engine = Orchestrator()

    def handler(state):
        state.artifacts["result"] = "success"

    engine.register("test", handler)
    result = engine.run(WorkflowState("Test requirement"))

    assert result.status == Status.COMPLETED
    assert result.artifacts["result"] == "success"


def test_failed_workflow():
    engine = Orchestrator()

    def handler(state):
        raise ValueError("Test failure")

    engine.register("test", handler)
    result = engine.run(WorkflowState("Test requirement"))

    assert result.status == Status.FAILED
    assert "Test failure" in result.errors


def test_approval_gate():
    engine = Orchestrator()

    def approval(state):
        state.status = Status.APPROVAL_REQUIRED

    def execution(state):
        state.artifacts["executed"] = True

    engine.register("approval", approval)
    engine.register("execution", execution)

    result = engine.run(WorkflowState("Test requirement"))

    assert result.status == Status.APPROVAL_REQUIRED
    assert "executed" not in result.artifacts
