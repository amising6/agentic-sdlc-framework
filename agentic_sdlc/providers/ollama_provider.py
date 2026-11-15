"""Local language model integration through Ollama."""

import json
import time
from urllib.error import URLError
from urllib.request import Request, urlopen

from agentic_sdlc.providers.base import (
    LLMProvider,
    LLMResponse,
)


class OllamaProvider(LLMProvider):

    def __init__(
        self,
        model: str = "qwen2.5-coder:3b",
        base_url: str = "http://127.0.0.1:11434",
        timeout: int = 300,
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def generate(
        self,
        prompt: str,
        system: str = "",
        json_mode: bool = False,
    ) -> LLMResponse:

        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_ctx": 4096,
            },
        }

        if json_mode:
            payload["format"] = "json"

        request = Request(
            f"{self.base_url}/api/generate",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json"
            },
            method="POST",
        )

        start = time.monotonic()

        try:
            with urlopen(
                request, timeout=self.timeout
            ) as response:
                result = json.loads(response.read())

        except URLError as exc:
            raise RuntimeError(
                f"Ollama request failed: {exc}"
            ) from exc

        if not result.get("response", "").strip():
            raise RuntimeError(
                "Ollama returned an empty response"
            )

        return LLMResponse(
            content=result["response"],
            model=self.model,
            provider="ollama",
            duration_seconds=round(
                time.monotonic() - start, 3
            ),
            input_tokens=result.get(
                "prompt_eval_count", 0
            ),
            output_tokens=result.get(
                "eval_count", 0
            ),
        )
