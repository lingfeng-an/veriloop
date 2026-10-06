"""Mock retriever — returns deterministic source excerpts for a claim.

The retrieval step is deliberately simple: given a :class:`Claim`, it returns
the evidence excerpts recorded in the demo fixtures keyed by ``claim_id``. It
operates purely on claim identity and never touches any gold answer.

This is a development/demo retrieval stand-in. A production retriever (web or
corpus search) would plug into the same :class:`Retriever` interface.
"""

from __future__ import annotations

from ..fixtures import DEMO_EVIDENCE, RETRIEVED_AT
from ..schema import Claim, Evidence


class MockRetriever:
    """Deterministic offline retriever backed by :data:`fixtures.DEMO_EVIDENCE`."""

    def retrieve(self, claim: Claim) -> list[Evidence]:
        raw = DEMO_EVIDENCE.get(claim.id, [])
        return [
            Evidence(
                id=item["id"],
                source_url=item["source_url"],
                excerpt=item["excerpt"],
                retrieved_at=RETRIEVED_AT,
            )
            for item in raw
        ]
