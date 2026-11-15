"""AI-assisted requirement analysis."""

import json

from agentic_sdlc.core.state import WorkflowState
from agentic_sdlc.providers.base import LLMProvider


def analyze_with_ai(
    state: WorkflowState,
    provider: LLMProvider,
):
    analysis = state.artifacts["analysis"]

    system = (
        "You are a senior software architect. "
        "Analyze the supplied requirements. "
        "Do not invent confirmed business requirements. "
        "Treat additional findings as recommendations. "
        "Return only valid JSON."
    )

    prompt = f"""
Analyze this structured requirement:

{json.dumps(analysis, indent=2)}

Return a JSON object with these fields:

- technical_approach: string
- recommended_components: list of strings
- risks: list of strings
- edge_cases: list of strings
- assumptions: list of strings
- open_questions: list of strings

Be concise and specific to the supplied requirements.
"""

    response = provider.generate(
        prompt=prompt,
        system=system,
        json_mode=True,
    )

    insights = json.loads(response.content)

    if not isinstance(insights, dict):
        raise TypeError("Expected a JSON object")

    if not isinstance(
        insights.get("technical_approach"), str
    ):
        raise TypeError("Expected technical approach as a string")

    for field in (
        "recommended_components",
        "risks",
        "edge_cases",
        "assumptions",
        "open_questions",
    ):
        values = insights.get(field)

        if not isinstance(values, list) or not all(
            isinstance(value, str) for value in values
        ):
            raise TypeError(f"Invalid AI field: {field}")

    state.artifacts["ai_analysis"] = insights

    state.artifacts.setdefault(
        "llm_usage", []
    ).append({
        "agent": "intelligence",
        "provider": response.provider,
        "model": response.model,
        "duration_seconds": response.duration_seconds,
        "input_tokens": response.input_tokens,
        "output_tokens": response.output_tokens,
    })

    state.record_event(
        "ai_intelligence",
        "AI requirement analysis completed",
    )
