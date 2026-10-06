"""H1-01 metrics.

Contamination-rate definition (locked)
--------------------------------------
    contamination_rate = accepted-but-invalid claims / accepted claims

where *accepted-but-invalid* means a claim the Verifier ACCEPTED but that the
judge then judged to either contradict the gold answer or lack evidence
support. If ``accepted_claims == 0`` the contamination rate is ``None`` (null),
never ``0`` and never ``0.0``.

Development/demo metrics computed here are NOT formal H1-01 evaluation metrics.
The formal frozen set is not yet established (see ``data/frozen/README.md``).
"""

from __future__ import annotations

from ..llm import LLMClient
from ..schema import Claim, Evidence


def _ratio(numerator: int, denominator: int) -> float | None:
    if denominator <= 0:
        return None
    return numerator / denominator


def compute_factual_accuracy(valid_accepted: int, accepted_claims: int) -> float | None:
    """Fraction of accepted claims that are valid (gold-consistent + supported)."""
    return _ratio(valid_accepted, accepted_claims)


def compute_citation_correctness(
    accepted_claims: int,
    claims_with_citation: int,
) -> float | None:
    """Fraction of accepted claims backed by a non-empty, well-formed citation."""
    return _ratio(claims_with_citation, accepted_claims)


def compute_contamination_rate(accepted_invalid: int, accepted_claims: int) -> float | None:
    """accepted-but-invalid / accepted. None when accepted_claims == 0."""
    return _ratio(accepted_invalid, accepted_claims)


def has_valid_citation(claim: Claim, evidence_by_id: dict[str, Evidence]) -> bool:
    """A claim has a valid citation when all its evidence_ids resolve to a
    well-formed http(s) source URL and the excerpt is non-empty."""
    if not claim.evidence_ids:
        return False
    for eid in claim.evidence_ids:
        ev = evidence_by_id.get(eid)
        if ev is None or not ev.excerpt.strip():
            return False
        if not (ev.source_url.startswith("http://") or ev.source_url.startswith("https://")):
            return False
    return True


def compute_cost(llm_client: LLMClient) -> float:
    """Total spend for the run in USD. Mock client always returns 0.0."""
    return llm_client.total_cost()
