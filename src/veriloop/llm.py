"""LLM client abstraction.

VeriLoop ships with a deterministic, fully-offline :class:`MockLLMClient` as the
default. Real-model integration does not exist in this MVP; if it is added, it
must remain behind this interface and must be gated by ``MOCK_LLM`` so that the
default run stays offline and requires no API key.

Cost tracking lives here so that the metrics layer can read a real dollar figure
from the live client (mock cost is always ``0.0``).
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod

from .fixtures import DEMO_CLAIMS


class LLMClient(ABC):
    """Interface any model provider must implement."""

    @abstractmethod
    def complete(self, prompt: str) -> str:
        """Return the model's completion for a prompt."""

    @abstractmethod
    def total_cost(self) -> float:
        """Return cumulative cost in USD (0.0 for the mock)."""


class MockLLMClient(LLMClient):
    """Deterministic offline stand-in for a research LLM.

    Given a prompt that embeds a ``QUESTION_ID:`` marker, it returns the canned
    candidate-claim JSON from :data:`fixtures.DEMO_CLAIMS` for that question.
    It never makes a network call and never requires an API key.
    """

    def __init__(self) -> None:
        self._calls: int = 0

    def complete(self, prompt: str) -> str:
        self._calls += 1
        qid = self._extract_question_id(prompt)
        claims = DEMO_CLAIMS.get(qid, [])
        return json.dumps(claims, ensure_ascii=False)

    def total_cost(self) -> float:
        return 0.0

    @property
    def calls(self) -> int:
        return self._calls

    @staticmethod
    def _extract_question_id(prompt: str) -> str:
        for line in prompt.splitlines():
            if line.startswith("QUESTION_ID:"):
                return line.split(":", 1)[1].strip()
        return ""
