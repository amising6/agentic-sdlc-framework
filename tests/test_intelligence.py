import pytest

from agentic_sdlc.core.state import WorkflowState
from agentic_sdlc.intelligence.analyzer import analyze_requirement
from agentic_sdlc.planning.planner import create_plan
from agentic_sdlc.planning.specification import generate_specification

REQUIREMENT = """
# Sample Project

## Business Requirement

Build a sample application.

## Acceptance Criteria

- Accept valid input.
- Reject invalid input.
"""


def test_requirement_analysis():
    state = WorkflowState(REQUIREMENT)
    analyze_requirement(state)

    analysis = state.artifacts["analysis"]

    assert analysis["project"] == "Sample Project"
    assert len(analysis["requirements"]) == 2
    assert analysis["requirements"][0]["id"] == "REQ-001"


def test_missing_requirement():
    state = WorkflowState("# Empty Project")

    with pytest.raises(ValueError):
        analyze_requirement(state)


def test_implementation_plan():
    state = WorkflowState(REQUIREMENT)

    analyze_requirement(state)
    create_plan(state)

    plan = state.artifacts["plan"]

    assert plan["total_tasks"] == 2
    assert plan["tasks"][0]["requirement_id"] == "REQ-001"


def test_specification_generation():
    state = WorkflowState(REQUIREMENT)

    analyze_requirement(state)
    create_plan(state)
    generate_specification(state)

    specification = state.artifacts["specification"]

    assert "REQ-001" in specification
    assert "TASK-001" in specification
    assert "Governance" in specification
