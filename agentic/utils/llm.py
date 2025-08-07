from __future__ import annotations

import os
from typing import Optional, Protocol


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


# -------------------- OpenAI-backed clients --------------------

class OpenAIChatLLM:
    """LLMClient implementation using OpenAI Chat Completions API.

    Requires OPENAI_API_KEY set in environment. If not present, this will
    raise at construction time.
    """

    def __init__(self, model: str, *, temperature: float = 0.0, max_tokens: Optional[int] = None) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")
        self._model = model
        self._temperature = float(temperature)
        self._max_tokens = max_tokens
        # Lazy import to avoid hard dependency at import time
        try:
            from openai import OpenAI  # type: ignore
        except Exception as e:  # pragma: no cover - optional
            raise RuntimeError("openai package is required for OpenAIChatLLM") from e
        self._client = OpenAI()

    def generate(self, prompt: str) -> str:
        try:
            # Prefer chat.completions for broad compatibility
            resp = self._client.chat.completions.create(
                model=self._model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self._temperature,
                max_tokens=self._max_tokens,
            )
            text = resp.choices[0].message.content or ""
            return text
        except Exception:
            # As a safety net, return empty JSON-ish
            return "{}"


class ClassifierOpenAILLM:
    """Classifier-compatible client exposing complete()."""

    def __init__(self, model: str, *, temperature: float = 0.0, max_tokens: Optional[int] = 512) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")
        self._model = model
        self._temperature = float(temperature)
        self._max_tokens = max_tokens
        try:
            from openai import OpenAI  # type: ignore
        except Exception as e:  # pragma: no cover - optional
            raise RuntimeError("openai package is required for ClassifierOpenAILLM") from e
        self._client = OpenAI()

    def complete(self, prompt: str, *, model: Optional[str] = None, temperature: float = 0.0, max_tokens: Optional[int] = None) -> str:
        m = model or self._model
        t = temperature if temperature is not None else self._temperature
        mt = max_tokens if max_tokens is not None else self._max_tokens
        try:
            resp = self._client.chat.completions.create(
                model=m,
                messages=[{"role": "user", "content": prompt}],
                temperature=t,
                max_tokens=mt,
            )
            text = resp.choices[0].message.content or ""
            return text
        except Exception:
            return "{}"

