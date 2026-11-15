"""Generate a technical specification from workflow state."""

from agentic_sdlc.core.state import WorkflowState


def generate_specification(state: WorkflowState):
    analysis = state.artifacts["analysis"]
    plan = state.artifacts["plan"]

    lines = [
        f"# Technical Specification: {analysis['project']}",
        "",
        "## Business Objective",
        "",
        analysis["objective"],
        "",
        "## Functional Requirements",
        "",
    ]

    for requirement in analysis["requirements"]:
        lines.append(
            f"- {requirement['id']}: "
            f"{requirement['description']}"
        )

    lines.extend([
        "",
        "## Implementation Plan",
        "",
    ])

    for task in plan["tasks"]:
        lines.extend([
            f"### {task['task_id']}",
            "",
            f"Requirement: {task['requirement_id']}",
            "",
            task["implementation"],
            "",
            task["validation"],
            "",
        ])

    lines.extend([
        "## Governance",
        "",
        "- Human review before implementation.",
        "- Automated testing before delivery.",
        "- Traceable validation evidence.",
        "",
    ])

    if "ai_analysis" in state.artifacts:
        insights = state.artifacts["ai_analysis"]

        lines.extend([
            "",
            "## AI Advisory Analysis",
            "",
            "The following findings require human review.",
            "",
            "### Recommended Technical Approach",
            "",
            insights["technical_approach"],
            "",
        ])

        for field, heading in (
            ("recommended_components", "Components"),
            ("risks", "Risks"),
            ("edge_cases", "Edge Cases"),
            ("assumptions", "Unapproved Assumptions"),
            ("open_questions", "Open Questions"),
        ):
            lines.extend([f"### {heading}", ""])

            for item in insights[field]:
                lines.append(f"- {item}")

            lines.append("")

    state.artifacts["specification"] = "\n".join(lines)
