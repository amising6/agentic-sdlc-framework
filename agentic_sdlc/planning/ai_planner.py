"""AI-assisted implementation planning."""

import json

from agentic_sdlc.core.state import WorkflowState
from agentic_sdlc.providers.base import LLMProvider


def plan_with_ai(
    state: WorkflowState,
    provider: LLMProvider,
):
    analysis = state.artifacts["analysis"]
    insights = state.artifacts["ai_analysis"]

    system = (
        "You are a senior software engineer. "
        "Create an actionable implementation plan. "
        "Preserve every original requirement ID. "
        "Do not introduce unapproved business requirements. "
        "AI assumptions are advisory, not confirmed scope. "
        "Return only valid JSON."
    )

    prompt = f"""
Confirmed requirements:

{json.dumps(analysis, indent=2)}

Advisory technical analysis:

{json.dumps(insights, indent=2)}

Return a JSON object containing a tasks array.

Each task must contain:
- requirement_id: original requirement ID
- implementation: specific technical implementation
- validation: specific test scenario and expected result

Create exactly one task for each original requirement.
Do not omit or invent requirement IDs.
Keep the solution simple.
"""

    response = provider.generate(
        prompt=prompt,
        system=system,
        json_mode=True,
    )

    result = json.loads(response.content)

    if not isinstance(result, dict):
        raise TypeError("Expected a JSON object")

    tasks = result.get("tasks")

    if not isinstance(tasks, list):
        raise TypeError("Expected a tasks array")

    requirements = {
        item["id"]: item["description"]
        for item in analysis["requirements"]
    }

    validated_tasks = []
    seen = set()

    for task in tasks:
        if not isinstance(task, dict):
            raise TypeError("Expected a task object")

        requirement_id = task.get("requirement_id")

        if requirement_id not in requirements:
            raise ValueError(
                f"Unknown requirement: {requirement_id}"
            )

        if requirement_id in seen:
            raise ValueError(
                f"Duplicate requirement: {requirement_id}"
            )

        for field in ("implementation", "validation"):
            value = task.get(field)

            if not isinstance(value, str):
                raise TypeError(
                    f"Invalid task field: {field}"
                )

            if not value.strip():
                raise ValueError(
                    f"Empty task field: {field}"
                )

        seen.add(requirement_id)

        validated_tasks.append({
            "task_id": f"TASK-{len(validated_tasks) + 1:03d}",
            "requirement_id": requirement_id,
            "description": requirements[requirement_id],
            "implementation": task["implementation"],
            "validation": task["validation"],
            "status": "pending",
        })

    if seen != set(requirements):
        missing = set(requirements) - seen

        raise ValueError(
            f"Missing requirements: {sorted(missing)}"
        )

    state.artifacts["plan"] = {
        "project": analysis["project"],
        "objective": analysis["objective"],
        "tasks": validated_tasks,
        "total_tasks": len(validated_tasks),
        "planning_mode": "ai",
    }

    state.artifacts.setdefault(
        "llm_usage", []
    ).append({
        "agent": "planning",
        "provider": response.provider,
        "model": response.model,
        "duration_seconds": response.duration_seconds,
        "input_tokens": response.input_tokens,
        "output_tokens": response.output_tokens,
    })

    state.record_event(
        "ai_planning",
        f"Generated {len(validated_tasks)} validated tasks",
    )
