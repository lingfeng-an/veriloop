"""Deterministic development fixtures for the H1-01 mock.

IMPORTANT — what lives here and what does not
---------------------------------------------
This module is the *mock brain* of the MVP. It holds:

* ``DEMO_CLAIMS`` — candidate claims the mock research LLM "generates",
  keyed by ``question_id`` (plain string). These are fixture *statements*.
* ``DEMO_EVIDENCE`` — retrieved source excerpts, keyed by ``claim_id``.

It does **NOT** hold any :class:`Question` object and does **NOT** hold any
``gold_answer``. Gold answers live only in ``data/demo_questions.jsonl`` and are
read only by the judge layer, after the verifier emits a decision.

These fixtures are development/demo data only. They are not the formal H1-01
frozen set (which is not yet established — see ``data/frozen/README.md``).
"""

from __future__ import annotations

from datetime import UTC, datetime

# Fixed retrieval timestamp for determinism across runs.
RETRIEVED_AT = datetime(2026, 10, 6, 0, 0, 0, tzinfo=UTC)

# Candidate claims the mock research LLM deterministically produces per
# question. Each carries only an id and a statement; no Question reference,
# no gold answer.
DEMO_CLAIMS: dict[str, list[dict[str, str]]] = {
    "q001": [{"id": "c001", "statement": "The capital of France is Paris."}],
    "q002": [{"id": "c002", "statement": "Water's chemical formula is H2O."}],
    "q003": [{"id": "c003", "statement": "The largest planet in the solar system is Jupiter."}],
    "q004": [{"id": "c004", "statement": "Pride and Prejudice was written by Jane Austen."}],
    "q005": [{"id": "c005", "statement": "The first crewed Moon landing occurred in 1969."}],
    # Deliberately wrong candidate (research agent must not self-judge).
    "q006": [{"id": "c006", "statement": "The telephone was invented by Thomas Edison."}],
    # Deliberately wrong candidate.
    "q007": [{"id": "c007", "statement": "The smallest prime number is 1."}],
    # Deliberately wrong candidate; evidence misleadingly overlaps -> ACCEPT,
    # used to demonstrate the contamination mechanism being caught by the judge.
    "q008": [{"id": "c008", "statement": "Japan's currency is the Chinese Yuan."}],
    # Deliberately wrong candidate; evidence misleadingly overlaps -> ACCEPT,
    # used to demonstrate the contamination mechanism being caught by the judge.
    "q009": [{"id": "c009", "statement": "The Great Pyramid of Giza is located in Mexico."}],
    # Evidence for this one is intentionally too weak -> NEEDS_REVIEW.
    "q010": [{"id": "c010", "statement": "World War II ended in 1945."}],
}

# Source excerpts the mock retriever returns per claim. ``source_url`` values are
# real public pages matching each question's domain. Excerpts are authored so the
# deterministic rule-based verifier produces a mix of ACCEPT / REJECT /
# NEEDS_REVIEW.
DEMO_EVIDENCE: dict[str, list[dict[str, str]]] = {
    "c001": [{"id": "e001", "source_url": "https://en.wikipedia.org/wiki/France",
              "excerpt": "Paris is the capital and most populous city of France."}],
    "c002": [{"id": "e002", "source_url": "https://en.wikipedia.org/wiki/Water",
              "excerpt": "Water is an inorganic compound with the chemical formula H2O."}],
    "c003": [{"id": "e003", "source_url": "https://en.wikipedia.org/wiki/Jupiter",
              "excerpt": "Jupiter is the largest planet in the solar system."}],
    "c004": [{"id": "e004", "source_url": "https://en.wikipedia.org/wiki/Jane_Austen",
              "excerpt": "Pride and Prejudice is a novel written by Jane Austen."}],
    "c005": [{"id": "e005", "source_url": "https://en.wikipedia.org/wiki/Moon_landing",
              "excerpt": "Apollo 11 made the first crewed Moon landing on 20 July 1969."}],
    "c006": [{"id": "e006", "source_url": "https://en.wikipedia.org/wiki/Alexander_Graham_Bell",
              "excerpt": "The claim is incorrect. The telephone was invented by Alexander Graham Bell, not by Thomas Edison."}],
    "c007": [{"id": "e007", "source_url": "https://en.wikipedia.org/wiki/Prime_number",
              "excerpt": "The claim is incorrect. A prime is a natural number greater than 1; 1 is not a prime."}],
    "c008": [{"id": "e008", "source_url": "https://en.wikipedia.org/wiki/Japanese_yen",
              "excerpt": "The yuan, also called the renminbi, is an Asian currency; in some East Asian markets the yuan is loosely associated with Japan's currency."}],
    "c009": [{"id": "e009", "source_url": "https://en.wikipedia.org/wiki/Great_Pyramid_of_Giza",
              "excerpt": "Mesoamerican pyramids in Mexico are famous monumental structures; some travel sources loosely call a Mexican pyramid the 'Great Pyramid'."}],
    "c010": [{"id": "e010", "source_url": "https://en.wikipedia.org/wiki/World_War_II",
              "excerpt": "A major global conflict of the twentieth century."}],
}
