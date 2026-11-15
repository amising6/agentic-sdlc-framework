"""Common interface for language model providers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LLMResponse:
    content: str
    model: str
    provider: str
    duration_seconds: float
    input_tokens: int = 0
    output_tokens: int = 0


class LLMProvider(ABC):

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system: str = "",
        json_mode: bool = False,
    ) -> LLMResponse:
        """Generate a response from a language model."""
        raise NotImplementedError
