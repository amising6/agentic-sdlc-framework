import json
from unittest.mock import Mock

import pytest

from agentic_sdlc.core.state import WorkflowState
from agentic_sdlc.intelligence.ai_analyzer import analyze_with_ai
from agentic_sdlc.providers.base import LLMResponse


def create_state():
    state = WorkflowState("Inventory requirement")

    state.artifacts["analysis"] = {
        "project": "Inventory",
        "objective": "Manage inventory",
        "requirements": [
            {
                "id": "REQ-001",
                "description": "Prevent negative quantities",
            }
        ],
    }

    return state


def create_provider(payload):
    provider = Mock()

    provider.generate.return_value = LLMResponse(
        content=json.dumps(payload),
        model="test-model",
        provider="mock",
        duration_seconds=0.1,
        input_tokens=100,
        output_tokens=50,
    )

    return provider


def test_valid_ai_analysis():
    state = create_state()

    provider = create_provider({
        "technical_approach": "Validate inventory updates",
        "recommended_components": ["inventory.py"],
        "risks": ["Invalid quantities"],
        "edge_cases": ["Zero quantity"],
        "assumptions": [],
        "open_questions": [],
    })

    analyze_with_ai(state, provider)

    assert "ai_analysis" in state.artifacts
    assert len(state.artifacts["llm_usage"]) == 1
    assert state.artifacts["llm_usage"][0]["input_tokens"] == 100

    provider.generate.assert_called_once()


def test_invalid_ai_response_type():
    state = create_state()
    provider = create_provider(["invalid"])

    with pytest.raises(TypeError):
        analyze_with_ai(state, provider)


def test_missing_technical_approach():
    state = create_state()
    provider = create_provider({})

    with pytest.raises(TypeError):
        analyze_with_ai(state, provider)


def test_invalid_ai_list_field():
    state = create_state()

    provider = create_provider({
        "technical_approach": "Validate inventory",
        "recommended_components": "inventory.py",
    })

    with pytest.raises(TypeError):
        analyze_with_ai(state, provider)
