"""Create a traceable implementation plan."""

from agentic_sdlc.core.state import WorkflowState


def create_plan(state: WorkflowState):
    analysis = state.artifacts["analysis"]

    tasks = []

    for index, requirement in enumerate(
        analysis["requirements"], 1
    ):
        tasks.append({
            "task_id": f"TASK-{index:03d}",
            "requirement_id": requirement["id"],
            "description": requirement["description"],
            "implementation": (
                f"Implement: {requirement['description']}"
            ),
            "validation": (
                f"Verify: {requirement['description']}"
            ),
            "status": "pending",
        })

    state.artifacts["plan"] = {
        "project": analysis["project"],
        "objective": analysis["objective"],
        "tasks": tasks,
        "total_tasks": len(tasks),
        "planning_mode": "offline",
    }

    state.record_event(
        "planning",
        f"Created {len(tasks)} implementation tasks",
    )
