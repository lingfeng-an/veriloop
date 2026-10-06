"""Rule Judge — evaluates accepted claims against gold answers.

Access contract (P0)
--------------------
* The judge is the **only** layer allowed to read ``gold_answer``.
* It reads gold **after** the verifier has emitted a decision. The verifier and
  the judge share no mutable :class:`Question` object reference: the pipeline
  passes the judge a plain ``gold_answer`` string, never a Question object.
* The judge receives only ``claim``, ``evidence``, ``verification`` and the
  gold string. It never hands gold back to any other layer.

For the MVP the judge is a deterministic rule: an accepted claim is *valid* when
every meaningful gold term appears in the claim statement AND the verifier
marked the claim as evidence-supported. Everything else is *invalid*.
"""

from __future__ import annotations

from ..schema import Claim, Evidence, VerificationResult, normalize_tokens


class JudgeVerdict:
    """Per-claim judge outcome."""

    __slots__ = ("claim_id", "decision", "valid", "reason")

    def __init__(self, claim_id: str, decision: str, valid: bool, reason: str) -> None:
        self.claim_id = claim_id
        self.decision = decision
        self.valid = valid
        self.reason = reason


class RuleJudge:
    """Deterministic judge that reads the gold answer only after verification."""

    def evaluate(
        self,
        claim: Claim,
        evidence: list[Evidence],
        verification: VerificationResult,
        gold_answer: str,
    ) -> JudgeVerdict:
        # Only ACCEPTED claims are candidates for entering the knowledge base.
        # REJECT / NEEDS_REVIEW never enter, so they are not scored as invalid.
        if verification.decision != "ACCEPT":
            return JudgeVerdict(
                claim_id=claim.id,
                decision=verification.decision,
                valid=True,
                reason="Claim not accepted; not a KB-entry candidate.",
            )

        gold_tokens = normalize_tokens(gold_answer)
        claim_tokens = normalize_tokens(claim.statement)
        gold_consistent = bool(gold_tokens) and gold_tokens.issubset(claim_tokens)

        if gold_consistent and verification.evidence_supported:
            return JudgeVerdict(
                claim_id=claim.id,
                decision="ACCEPT",
                valid=True,
                reason="Accepted claim is consistent with gold and evidence-supported.",
            )

        return JudgeVerdict(
            claim_id=claim.id,
            decision="ACCEPT",
            valid=False,
            reason=(
                "Accepted claim is invalid: "
                + ("not gold-consistent." if not gold_consistent else "not evidence-supported.")
            ),
        )
