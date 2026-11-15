import json
from unittest.mock import Mock

import pytest

from agentic_sdlc.core.state import WorkflowState
from agentic_sdlc.planning.ai_planner import plan_with_ai
from agentic_sdlc.providers.base import LLMResponse


def create_state():
    state = WorkflowState("Sample requirement")

    state.artifacts["analysis"] = {
        "project": "Sample",
        "objective": "Validate input",
        "requirements": [
            {
                "id": "REQ-001",
                "description": "Reject negative values",
            }
        ],
    }

    state.artifacts["ai_analysis"] = {
        "technical_approach": "Input validation"
    }

    return state


def create_provider(tasks):
    provider = Mock()

    provider.generate.return_value = LLMResponse(
        content=json.dumps({"tasks": tasks}),
        model="test-model",
        provider="mock",
        duration_seconds=0.1,
    )

    return provider


def sample_task(requirement_id="REQ-001"):
    return {
        "requirement_id": requirement_id,
        "implementation": "Raise ValueError for negatives",
        "validation": "Verify negative input is rejected",
    }


def test_valid_ai_plan():
    state = create_state()

    plan_with_ai(
        state,
        create_provider([sample_task()]),
    )

    plan = state.artifacts["plan"]

    assert plan["planning_mode"] == "ai"
    assert plan["total_tasks"] == 1
    assert plan["tasks"][0]["requirement_id"] == "REQ-001"


def test_unknown_requirement():
    state = create_state()

    with pytest.raises(ValueError, match="Unknown"):
        plan_with_ai(
            state,
            create_provider([sample_task("REQ-999")]),
        )


def test_missing_requirement():
    state = create_state()

    with pytest.raises(ValueError, match="Missing"):
        plan_with_ai(state, create_provider([]))


def test_duplicate_requirement():
    state = create_state()

    with pytest.raises(ValueError, match="Duplicate"):
        plan_with_ai(
            state,
            create_provider([
                sample_task(),
                sample_task(),
            ]),
        )
