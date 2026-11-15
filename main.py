"""Command-line entry point for Agentic SDLC."""

import argparse
import json
from functools import partial
from pathlib import Path

from agentic_sdlc.core.artifacts import save_artifacts
from agentic_sdlc.core.orchestrator import Orchestrator
from agentic_sdlc.core.state import WorkflowState
from agentic_sdlc.intelligence.ai_analyzer import analyze_with_ai
from agentic_sdlc.intelligence.analyzer import analyze_requirement
from agentic_sdlc.planning.ai_planner import plan_with_ai
from agentic_sdlc.planning.planner import create_plan
from agentic_sdlc.planning.specification import generate_specification
from agentic_sdlc.providers.factory import create_provider


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

    parser.add_argument(
        "--provider",
        choices=["offline", "ollama"],
        default="offline",
    )

    parser.add_argument(
        "--model",
        default=None,
    )

    args = parser.parse_args()

    requirement = Path(
        args.requirement
    ).read_text(encoding="utf-8")

    state = WorkflowState(requirement=requirement)

    orchestrator = Orchestrator()
    orchestrator.register("initialization", initialize)
    orchestrator.register("intelligence", analyze_requirement)
    if args.provider != "offline":
        provider = create_provider(
            args.provider, args.model
        )
        orchestrator.register(
            "ai_intelligence",
            partial(analyze_with_ai, provider=provider),
        )

    if args.provider == "offline":
        orchestrator.register("planning", create_plan)
    else:
        orchestrator.register(
            "ai_planning",
            partial(plan_with_ai, provider=provider),
        )
    orchestrator.register("specification", generate_specification)

    result = orchestrator.run(state)
    output = save_artifacts(result)
    print(f"Artifacts saved to: {output}")

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
