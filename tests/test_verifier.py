"""Independent Verifier tests: decisions, evidence linkage, and access isolation."""

from __future__ import annotations

import inspect
import re
from datetime import UTC, datetime
from pathlib import Path

from veriloop.schema import Claim, Evidence, Question
from veriloop.verifiers.independent_verifier import IndependentVerifier


def _claim(statement: str, cid: str = "c_x") -> Claim:
    return Claim(id=cid, question_id="q001", statement=statement)


def _evidence(excerpt: str, eid: str = "e_x") -> Evidence:
    return Evidence(
        id=eid,
        source_url="https://en.wikipedia.org/wiki/Example",
        excerpt=excerpt,
        retrieved_at=datetime(2026, 10, 6, tzinfo=UTC),
    )


def test_accept_when_evidence_supports():
    v = IndependentVerifier()
    result = v.verify(
        _claim("The capital of France is Paris."),
        [_evidence("Paris is the capital and most populous city of France.")],
    )
    assert result.decision == "ACCEPT"
    assert result.evidence_supported is True


def test_reject_when_evidence_contradicts():
    v = IndependentVerifier()
    result = v.verify(
        _claim("The telephone was invented by Thomas Edison."),
        [_evidence("The claim is incorrect. The telephone was invented by Bell, not Edison.")],
    )
    assert result.decision == "REJECT"
    assert result.evidence_supported is False


def test_needs_review_when_evidence_insufficient():
    v = IndependentVerifier()
    result = v.verify(
        _claim("World War II ended in 1945."),
        [_evidence("A major global conflict of the twentieth century.")],
    )
    assert result.decision == "NEEDS_REVIEW"
    assert result.evidence_supported is False


def test_needs_review_when_no_evidence():
    v = IndependentVerifier()
    result = v.verify(_claim("Some claim."), [])
    assert result.decision == "NEEDS_REVIEW"


def test_result_carries_claim_id_and_evidence_linkage():
    v = IndependentVerifier()
    result = v.verify(
        _claim("The capital of France is Paris.", cid="c42"),
        [_evidence("Paris is the capital of France.")],
    )
    assert result.claim_id == "c42"
    # accepted results are linked to evidence support
    assert result.evidence_supported is True


# ---- access isolation (P0) ----------------------------------------------


def test_verifier_signature_accepts_only_claim_and_evidence():
    sig = inspect.signature(IndependentVerifier.verify)
    params = list(sig.parameters)
    # self, claim, evidence — nothing else
    assert params == ["self", "claim", "evidence"]
    assert "gold_answer" not in params
    assert "question" not in params


def test_verifier_source_has_no_gold_answer_token():
    """The verifier module must not reference the gold-answer field anywhere."""
    src = Path(inspect.getfile(IndependentVerifier)).read_text(encoding="utf-8")
    assert "gold_answer" not in src
    # verifier must not import Question
    assert "Question" not in src.split("from ..schema import")[1].split("\n")[0]


def test_verifier_deterministic_under_changed_gold_answer():
    """Changing the gold answer must NOT change the verifier decision.

    The verifier never receives a gold answer, so a different gold_answer in the
    surrounding context cannot affect its output.
    """
    claim = _claim("The capital of France is Paris.")
    evidence = [_evidence("Paris is the capital and most populous city of France.")]
    v = IndependentVerifier()

    # First decision, gold irrelevant (verifier never sees it).
    d1 = v.verify(claim, evidence)

    # Surrounding context carries a *different* gold answer; verifier is not
    # given it, so the decision must be byte-for-byte identical.
    _ = Question(
        id="q999",
        question="What is the capital of France?",
        gold_answer="Berlin",  # different gold answer
        source_url="https://en.wikipedia.org/wiki/France",
        domain="geography",
    )
    d2 = v.verify(claim, evidence)

    assert d1.decision == d2.decision
    assert d1.confidence == d2.confidence
    assert d1.reason == d2.reason
    assert d1.evidence_supported == d2.evidence_supported


def test_no_module_level_question_store():
    """No lru_cache/singleton/global list holding Question objects may exist
    in the verifier module (and there is none by construction)."""
    src = Path(inspect.getfile(IndependentVerifier)).read_text(encoding="utf-8")
    assert "@lru_cache" not in src
    assert re.search(r"^\s*_?(questions|QUESTION_POOL|CACHE)\s*=", src, re.M) is None
