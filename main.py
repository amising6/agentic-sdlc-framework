"""Command-line entry point for Agentic SDLC."""

import argparse
import json
from pathlib import Path

from agentic_sdlc.core.orchestrator import Orchestrator
from agentic_sdlc.core.state import WorkflowState


def initialize(state: WorkflowState):
    if not state.requirement.strip():
        raise ValueError("Requirement cannot be empty")

    state.artifacts["requirement"] = state.requirement


def main():
    parser = argparse.ArgumentParser(
        description="Agentic SDLC Framework"
    )

    parser.add_argument(
        "--requirement",
        required=True,
        help="Path to a requirement file",
    )

    args = parser.parse_args()

    requirement = Path(
        args.requirement
    ).read_text(encoding="utf-8")

    state = WorkflowState(requirement=requirement)

    orchestrator = Orchestrator()
    orchestrator.register("initialization", initialize)

    result = orchestrator.run(state)

    print(json.dumps({
        "run_id": result.run_id,
        "status": result.status.value,
        "stage": result.current_stage,
        "artifacts": result.artifacts,
        "history": result.history,
        "errors": result.errors,
    }, indent=2))

    return 0 if result.status.value == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
