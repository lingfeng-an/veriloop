"""Independent Verifier — decides ACCEPT / REJECT / NEEDS_REVIEW.

ACCESS-ISOLATION (P0, enforced in code, not just comments)
----------------------------------------------------------
* The public entry point is ``verify(claim: Claim, evidence: list[Evidence])``.
  It accepts **only** a :class:`Claim` and its evidence. It never accepts a
  :class:`Question`, never accepts a gold answer, and never accepts any object
  that could carry a gold answer.
* This module imports only ``Claim``, ``Evidence`` and ``VerificationResult``
  from the schema. It does not import ``Question``, and the gold-answer field
  token appears nowhere in this module (asserted by ``tests/test_verifier.py``).
* There is no module-level list/singleton/cache/lru_cache of Question objects.
* The verifier prints/logs nothing about gold answers (it has no access to
  one); its own output only describes evidence and the decision.

This MVP verifier is a deterministic rule-based mock. It is **not** a real LLM
experiment and produces no formal evidence for H1-01.
"""

from __future__ import annotations

from collections.abc import Iterable

from ..schema import Claim, Evidence, VerificationResult, normalize_tokens

# Phrases that mark an evidence excerpt as contradicting the claim. Kept as
# explicit markers so the rule is deterministic and auditable.
_CONTRADICTION_MARKERS: tuple[str, ...] = (
    "incorrect",
    "is false",
    "contradicts",
    "contrary to",
    "does not",
    "is not",
    "not by",
)

# Minimum number of shared meaningful terms to call evidence "supporting".
_SUPPORT_OVERLAP = 2


class IndependentVerifier:
    """Rule-based verifier. Pure function of (claim, evidence)."""

    def verify(self, claim: Claim, evidence: Iterable[Evidence]) -> VerificationResult:
        evidence_list = list(evidence)

        if not evidence_list:
            return VerificationResult(
                claim_id=claim.id,
                decision="NEEDS_REVIEW",
                confidence=0.1,
                reason="No evidence retrieved; cannot verify.",
                evidence_supported=False,
            )

        claim_tokens = normalize_tokens(claim.statement)

        # 1) Reject if any evidence explicitly contradicts the claim.
        for ev in evidence_list:
            low = ev.excerpt.lower()
            for marker in _CONTRADICTION_MARKERS:
                if marker in low:
                    return VerificationResult(
                        claim_id=claim.id,
                        decision="REJECT",
                        confidence=0.9,
                        reason=f"Evidence contradicts the claim (marker: {marker!r}).",
                        evidence_supported=False,
                    )

        # 2) Accept if evidence shares enough meaningful terms with the claim.
        best_overlap = 0
        best_evidence_id: str | None = None
        for ev in evidence_list:
            overlap = len(claim_tokens & normalize_tokens(ev.excerpt))
            if overlap > best_overlap:
                best_overlap = overlap
                best_evidence_id = ev.id

        if best_overlap >= _SUPPORT_OVERLAP:
            return VerificationResult(
                claim_id=claim.id,
                decision="ACCEPT",
                confidence=0.8,
                reason=(
                    f"Evidence supports the claim "
                    f"({best_overlap} shared terms, evidence {best_evidence_id})."
                ),
                evidence_supported=True,
            )

        # 3) Otherwise the evidence is insufficient or ambiguous.
        return VerificationResult(
            claim_id=claim.id,
            decision="NEEDS_REVIEW",
            confidence=0.4,
            reason="Evidence is insufficient or ambiguous to support or refute the claim.",
            evidence_supported=False,
        )
