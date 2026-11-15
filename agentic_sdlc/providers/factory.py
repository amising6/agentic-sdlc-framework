"""Factory for creating configured LLM providers."""

from agentic_sdlc.providers.base import LLMProvider
from agentic_sdlc.providers.ollama_provider import (
    OllamaProvider,
)


def create_provider(
    name: str,
    model: str | None = None,
) -> LLMProvider:

    if name == "ollama":
        return OllamaProvider(
            model=model or "qwen2.5-coder:3b"
        )

    raise ValueError(
        f"Unsupported LLM provider: {name}"
    )
