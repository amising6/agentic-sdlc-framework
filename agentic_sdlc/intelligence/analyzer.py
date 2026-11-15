"""Extract structured information from business requirements."""

import re

from agentic_sdlc.core.state import WorkflowState


def analyze_requirement(state: WorkflowState):
    content = state.requirement

    title = re.search(r"^#\s+(.+)$", content, re.MULTILINE)

    sections = {}
    current_section = None

    for line in content.splitlines():
        if line.startswith("## "):
            current_section = line[3:].strip().lower()
            sections[current_section] = []
        elif current_section:
            sections[current_section].append(line)

    objective = "\n".join(
        sections.get("business requirement", [])
    ).strip()

    criteria = [
        line.strip()[2:].strip()
        for line in sections.get("acceptance criteria", [])
        if line.strip().startswith("- ")
    ]

    if not objective:
        raise ValueError("Business requirement is missing")

    if not criteria:
        raise ValueError("Acceptance criteria are missing")

    state.artifacts["analysis"] = {
        "project": title.group(1) if title else "Untitled",
        "objective": objective,
        "requirements": [
            {
                "id": f"REQ-{index:03d}",
                "description": criterion,
            }
            for index, criterion in enumerate(criteria, 1)
        ],
        "analysis_mode": "offline",
    }

    state.record_event(
        "intelligence",
        f"Extracted {len(criteria)} acceptance criteria",
    )
