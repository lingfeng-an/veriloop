"""Metrics tests: accuracy, citation correctness, contamination, cost."""

from __future__ import annotations

from datetime import UTC, datetime

from veriloop.eval.metrics import (
    compute_citation_correctness,
    compute_contamination_rate,
    compute_cost,
    compute_factual_accuracy,
    has_valid_citation,
)
from veriloop.llm import MockLLMClient
from veriloop.schema import Claim, Evidence


def _evidence(eid: str, url: str = "https://en.wikipedia.org/wiki/Water") -> Evidence:
    return Evidence(
        id=eid,
        source_url=url,
        excerpt="Water is an inorganic compound with the chemical formula H2O.",
        retrieved_at=datetime(2026, 10, 6, tzinfo=UTC),
    )


# ---- factual accuracy ---------------------------------------------------


def test_factual_accuracy_ratio():
    # 5 valid of 7 accepted
    assert abs(compute_factual_accuracy(5, 7) - (5 / 7)) < 1e-9


def test_factual_accuracy_null_when_no_accepted():
    assert compute_factual_accuracy(0, 0) is None


# ---- citation correctness ------------------------------------------------


def test_citation_correctness_ratio():
    assert compute_citation_correctness(7, 7) == 1.0
    assert abs(compute_citation_correctness(7, 3) - (3 / 7)) < 1e-9


def test_citation_correctness_null_when_no_accepted():
    assert compute_citation_correctness(0, 0) is None


def test_has_valid_citation():
    ev = _evidence("e001")
    by_id = {"e001": ev}
    # no evidence ids -> invalid
    assert not has_valid_citation(Claim(id="c1", question_id="q1", statement="x"), by_id)
    # resolves to a well-formed url -> valid
    claim = Claim(id="c1", question_id="q1", statement="x", evidence_ids=["e001"])
    assert has_valid_citation(claim, by_id)


def test_has_valid_citation_rejects_bad_url():
    ev = _evidence("e001", url="not-a-url")
    claim = Claim(id="c1", question_id="q1", statement="x", evidence_ids=["e001"])
    assert not has_valid_citation(claim, {"e001": ev})


def test_has_valid_citation_rejects_missing_evidence():
    claim = Claim(id="c1", question_id="q1", statement="x", evidence_ids=["missing"])
    assert not has_valid_citation(claim, {})


# ---- contamination rate (locked definition) ------------------------------


def test_contamination_rate_ratio():
    # accepted-but-invalid / accepted
    assert abs(compute_contamination_rate(2, 7) - (2 / 7)) < 1e-9


def test_contamination_rate_null_when_accepted_zero():
    # Must be null (None), NOT 0 and NOT 0.0, when accepted_claims == 0.
    assert compute_contamination_rate(0, 0) is None


def test_contamination_rate_null_even_with_invalid():
    # denominator is the guard: accepted==0 -> null regardless of invalid count
    assert compute_contamination_rate(5, 0) is None


# ---- cost -----------------------------------------------------------------


def test_cost_zero_for_mock():
    assert compute_cost(MockLLMClient()) == 0.0
