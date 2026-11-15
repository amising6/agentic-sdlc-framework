"""Persist workflow artifacts for each execution."""

import json
from pathlib import Path

from agentic_sdlc.core.state import WorkflowState


def save_artifacts(state: WorkflowState):
    output = Path("artifacts") / state.run_id
    output.mkdir(parents=True, exist_ok=True)

    for name, content in state.artifacts.items():
        if name == "specification":
            (output / "spec.md").write_text(
                content, encoding="utf-8"
            )
        elif isinstance(content, str):
            (output / f"{name}.md").write_text(
                content, encoding="utf-8"
            )
        else:
            (output / f"{name}.json").write_text(
                json.dumps(content, indent=2),
                encoding="utf-8",
            )

    summary = {
        "run_id": state.run_id,
        "status": state.status.value,
        "history": state.history,
        "errors": state.errors,
    }

    (output / "execution.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )

    return output
