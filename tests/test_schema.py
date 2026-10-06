"""Schema validation tests: valid construction + invalid-input rejection."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from veriloop.schema import Claim, Evidence, ExperimentSummary, Question, VerificationResult


def _question(**overrides):
    base = {
        "id": "q001",
        "question": "What is the capital of France?",
        "gold_answer": "Paris",
        "source_url": "https://en.wikipedia.org/wiki/France",
        "domain": "geography",
    }
    base.update(overrides)
    return Question(**base)


def _evidence(**overrides):
    base = {
        "id": "e001",
        "source_url": "https://en.wikipedia.org/wiki/France",
        "excerpt": "Paris is the capital of France.",
        "retrieved_at": datetime(2026, 10, 6, tzinfo=UTC),
    }
    base.update(overrides)
    return Evidence(**base)


def test_question_valid():
    q = _question()
    assert q.id == "q001"
    assert q.gold_answer == "Paris"


def test_claim_valid_and_isolated_fields():
    c = Claim(id="c001", question_id="q001", statement="The capital of France is Paris.")
    assert c.question_id == "q001"
    assert c.evidence_ids == []
    # Claim must NOT carry a Question object or gold_answer field.
    assert "gold_answer" not in Claim.model_fields
    assert "question" not in Claim.model_fields


def test_evidence_valid():
    e = _evidence()
    assert e.source_url.startswith("https://")


def test_verification_result_valid():
    vr = VerificationResult(
        claim_id="c001",
        decision="ACCEPT",
        confidence=0.8,
        reason="supported",
        evidence_supported=True,
    )
    assert vr.decision == "ACCEPT"


def test_experiment_summary_allows_null_contamination():
    s = ExperimentSummary(
        total_questions=1,
        total_claims=0,
        accepted_claims=0,
        rejected_claims=0,
        needs_review_claims=0,
        factual_accuracy=None,
        citation_correctness=None,
        contamination_rate=None,
        cost=0.0,
    )
    assert s.contamination_rate is None


@pytest.mark.parametrize("field", ["id", "question", "gold_answer", "source_url", "domain"])
def test_question_rejects_empty_field(field):
    with pytest.raises(ValidationError):
        _question(**{field: "   "})


def _claim_kwargs(field):
    base = {"id": "c001", "question_id": "q001", "statement": "some statement"}
    base[field] = "   "
    return base


@pytest.mark.parametrize("field", ["id", "question_id", "statement"])
def test_claim_rejects_empty_field(field):
    with pytest.raises(ValidationError):
        Claim(**_claim_kwargs(field))


def test_verification_result_rejects_bad_decision():
    with pytest.raises(ValidationError):
        VerificationResult(
            claim_id="c001",
            decision="MAYBE",  # not in the Literal
            confidence=0.5,
            reason="x",
            evidence_supported=False,
        )


def test_verification_result_rejects_confidence_out_of_range():
    with pytest.raises(ValidationError):
        VerificationResult(
            claim_id="c001",
            decision="ACCEPT",
            confidence=1.5,  # > 1.0
            reason="x",
            evidence_supported=True,
        )
