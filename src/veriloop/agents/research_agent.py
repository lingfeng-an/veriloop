"""Research Agent — produces *candidate* claims.

Separation contract (P0)
------------------------
* The research agent receives only ``question_id`` + ``question_text``. It never
  receives a :class:`Question` object and therefore can never see a gold answer.
* It does **not** decide whether its own claims are correct. Correctness is the
  exclusive job of the independent verifier. This is why the mock deliberately
  emits some wrong candidate claims (e.g. "the telephone was invented by Thomas
  Edison"): the research agent must not self-judge.
"""

from __future__ import annotations

import json

from ..llm import LLMClient
from ..schema import Claim


class ResearchAgent:
    """Generates candidate claims for a research question.

    In mock mode the underlying :class:`~veriloop.llm.MockLLMClient` returns
    deterministic canned claims from the demo fixtures; the agent itself only
    formats a prompt, calls the LLM, and parses the returned JSON.
    """

    def __init__(
        self,
        llm: LLMClient,
        prompt_template: str | None = None,
    ) -> None:
        self._llm = llm
        self._prompt_template = prompt_template or _DEFAULT_RESEARCH_PROMPT

    def generate_claims(self, question_id: str, question_text: str) -> list[Claim]:
        prompt = self._prompt_template.format(
            question_id=question_id,
            question=question_text,
        )
        raw = self._llm.complete(prompt)
        payload = json.loads(raw)
        claims: list[Claim] = []
        for item in payload:
            claims.append(
                Claim(
                    id=item["id"],
                    question_id=question_id,
                    statement=item["statement"],
                    evidence_ids=[],
                )
            )
        return claims


_DEFAULT_RESEARCH_PROMPT = """\
You are a research agent. Produce candidate knowledge claims that could enter a
formal knowledge base. Do NOT judge whether each claim is correct — an
independent verifier decides that. Emit candidates only.

QUESTION_ID: {question_id}
QUESTION: {question}

Return a JSON array of objects, each with keys "id" and "statement".
"""
