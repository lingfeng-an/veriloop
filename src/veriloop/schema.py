"""Core data model for VeriLoop.

ACCESS-ISOLATION CONTRACT (P0)
-----------------------------
- :class:`Claim` deliberately carries only a ``question_id``. It must never
  reference a :class:`Question` object, never carry a ``gold_answer``, and never
  embed any implicit pointer back to a Question. This is enforced by the schema:
  the only Question-related field is the plain string ``question_id``.
- The Verifier's entry point accepts only ``(claim, evidence)`` and therefore
  can never see a gold answer. Gold answers are readable only by the
  evaluation/judge layer, strictly *after* the Verifier has emitted a decision.
- No module in the project may hold a module-level list/singleton/cache of
  Question objects. Question instances are created per-pipeline-run and handed
  only to the judge layer (as a plain ``gold_answer`` string) after verification.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

Decision = Literal["ACCEPT", "REJECT", "NEEDS_REVIEW"]

_STOPWORDS = {
    "the", "and", "of", "in", "is", "to", "for", "a", "an", "was", "are",
    "by", "on", "at", "with", "that", "this", "which", "has", "have", "as",
    "it", "its", "be", "or", "not",
}


def normalize_tokens(text: str) -> set[str]:
    """Lowercase, split on non-alphanumerics, drop stopwords and short tokens.

    Used by the deterministic mock verifier and the rule judge. It is the only
    tokenizer in the project so that both layers share one vocabulary.
    """
    words = re.findall(r"[a-z0-9]+", text.lower())
    return {w for w in words if len(w) >= 3 and w not in _STOPWORDS}


class Question(BaseModel):
    """A demo / formal evaluation item.

    ``gold_answer`` is sensitive: it must be readable only by the judge layer
    after the verifier has produced a decision.
    """

    id: str
    question: str
    gold_answer: str
    source_url: str
    domain: str

    @field_validator("id", "question", "gold_answer", "source_url", "domain")
    @classmethod
    def _non_empty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("field must be a non-empty string")
        return value.strip()


class Evidence(BaseModel):
    """A retrieved source excerpt used by the verifier.

    ``retrieved_at`` is a timezone-aware timestamp recording when the snippet
    was retrieved.
    """

    id: str
    source_url: str
    excerpt: str
    retrieved_at: datetime

    @field_validator("id", "source_url", "excerpt")
    @classmethod
    def _non_empty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("field must be a non-empty string")
        return value.strip()


class Claim(BaseModel):
    """A candidate knowledge claim produced by the Research Agent.

    Isolation: carries ONLY ``question_id`` (a plain string). It must never hold
    a Question object or a gold answer. ``evidence_ids`` are filled by the
    retriever.
    """

    id: str
    question_id: str
    statement: str
    evidence_ids: list[str] = Field(default_factory=list)

    @field_validator("id", "question_id", "statement")
    @classmethod
    def _non_empty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("field must be a non-empty string")
        return value.strip()


class VerificationResult(BaseModel):
    """Output of the Independent Verifier.

    ``evidence_supported`` is True only for ACCEPT decisions backed by evidence.
    """

    claim_id: str
    decision: Decision
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str
    evidence_supported: bool

    @field_validator("claim_id", "reason")
    @classmethod
    def _non_empty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("field must be a non-empty string")
        return value.strip()


class ExperimentSummary(BaseModel):
    """Aggregated metrics for one pipeline run.

    ``contamination_rate`` and the two accuracy fields are ``None`` when their
    denominator is zero (e.g. ``accepted_claims == 0`` → ``contamination_rate``
    is ``null``, never ``0``).
    """

    total_questions: int
    total_claims: int
    accepted_claims: int
    rejected_claims: int
    needs_review_claims: int
    factual_accuracy: float | None
    citation_correctness: float | None
    contamination_rate: float | None
    cost: float = Field(ge=0.0)
    cost_currency: str = "USD"
