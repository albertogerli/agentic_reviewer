from __future__ import annotations

from typing import Protocol


class LLMClient(Protocol):
    """Minimal LLM client protocol.

    Implementations should provide a `generate` method that returns a string
    response for a given prompt. This keeps the agent layer decoupled from any
    specific LLM provider.
    """

    def generate(self, prompt: str) -> str:  # pragma: no cover - interface
        ...


class EchoJSONLLM:
    """A very small testing stub that returns the provided prompt tail if it
    appears to contain a JSON example block. Useful for offline tests.

    NOTE: This is only for development/testing. Replace with a real LLMClient
    in production.
    """

    def __init__(self, static_response: str | None = None) -> None:
        self._static = static_response

    def generate(self, prompt: str) -> str:
        if self._static is not None:
            return self._static
        # Try to return whatever looks like JSON contained after a marker
        marker = "JSON_RESPONSE_START\n"
        if marker in prompt:
            return prompt.split(marker, 1)[1].strip()
        return "{}"

