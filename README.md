# VeriLoop — Independent Verification for Autonomous LLM Research

## 1. Overview

VeriLoop is a research project investigating whether an **independent verifier**
reduces erroneous knowledge claims entering a formal knowledge base. The first
experiment, **H1-01 — Independent Verifier Minimal Experiment**, implements the
core pipeline:

```
Research → Evidence → Independent Verification → Knowledge → Evaluation
```

The current implementation is a **deterministic, fully-offline MVP/demo**. It
runs with `MOCK_LLM=true` by default, calls no real API, and requires no API
key. **It is not a real LLM experiment and produces no formal evidence.**

## 2. Research Question

> Can an independent verifier reduce erroneous knowledge claims entering a
> formal knowledge base?

The pipeline separates claim *generation* (research agent) from claim
*admission* (independent verifier) so that no actor both proposes and judges its
own claims.

## 3. H1-01 Hypothesis

**H1-01.** Introducing an independent verifier — a component that accepts,
rejects, or defers claims based *only* on retrieved evidence, with no access to
gold answers — lowers the contamination rate (accepted-but-invalid claims)
relative to a baseline where claims flow directly into the knowledge base.

> **Status: HYPOTHESIS, NOT PROVEN.** The demo/mock results are not evidence
> that H1-01 is proven.

## 3a. Status

**Project stage: reproducible MVP/demo only.**

* H1-01 pipeline implemented end-to-end with deterministic mock components.
* Runs fully offline (`MOCK_LLM=true`); no real API; no API key required.
* Test suite passes (35 tests).
* Formal Frozen Set: **NOT ESTABLISHED** (target 50 questions).
* No formal evidence for H1-01; the hypothesis remains unproven.
* This repository was initialized as an immutable research baseline at tag
  `v0.1`; future changes are tracked as new commits.

## 4. Architecture

```
data/demo_questions.jsonl  (dev/demo questions only)
        │
        ▼
Research Agent ──(candidate claims)──▶ Evidence (MockRetriever)
                                              │
                                              ▼
                               Independent Verifier ──(ACCEPT / REJECT / NEEDS_REVIEW)
                                              │
                                              ▼
                                  Rule Judge (reads gold_answer ONLY here,
                                              AFTER the verifier decides)
                                              │
                                              ▼
                                              Metrics
```

Modules live under `src/veriloop/`:

| Module | Responsibility |
| --- | --- |
| `schema.py` | Pydantic data model + access-isolation contract |
| `llm.py` | LLM interface; deterministic `MockLLMClient` (offline) |
| `agents/research_agent.py` | Generates candidate claims (no self-judging) |
| `retrievers/mock_retriever.py` | Returns evidence for a claim |
| `verifiers/independent_verifier.py` | Decides from claim + evidence only |
| `judges/rule_judge.py` | Reads gold answers, after verification |
| `eval/metrics.py` | Accuracy, citation, contamination, cost |
| `pipelines/h1_01.py` | End-to-end pipeline + `summary.json` |

## 5. Experimental Boundary

* **Demo data** (`data/demo_questions.jsonl`, 10 public questions) is for
  development, unit tests, pipeline smoke tests, and mock demonstration only.
* **Formal Frozen Set** (`data/frozen/`) is **not yet established**. Target
  size: **50 questions**. It will be created only after data sources, time
  window, gold answers, scoring rubric, and contamination protocol are decided.
* The verifier never sees gold answers; the judge is the only layer that reads
  them, after the verifier has decided.

## 6. Demo vs Formal Frozen Set

| | Demo Set | Formal H1-01 Frozen Set |
| --- | --- | --- |
| Location | `data/demo_questions.jsonl` | `data/frozen/` (not yet created) |
| Size | 10 questions | Target 50 questions |
| Status | Active, development only | **NOT ESTABLISHED** |
| Inaccessible to Research/Training/Accumulation | n/a | Required until evaluation |
| Evidence value | None (mock) | Formal H1-01 evaluation |

The demo set must **not** be called a formal frozen set, and mock runs must not
be called real LLM experiments.

## 7. Method

1. Load demo questions.
2. Research agent generates candidate claims from the question text (it never
   sees gold answers).
3. Retriever returns evidence for each claim.
4. Independent verifier decides `ACCEPT` / `REJECT` / `NEEDS_REVIEW` from
   `(claim, evidence)` only.
5. Judge reads the gold answer **after** the verifier decision and marks each
   accepted claim valid or invalid.
6. Metrics are aggregated and written to `results/H1-01/summary.json`.

The current verifier/judge are deterministic rule-based mocks.

## 8. Metrics

* `factual_accuracy` — valid accepted claims / accepted claims (null when 0).
* `citation_correctness` — accepted claims with valid citations / accepted claims.
* `contamination_rate` — **accepted-but-invalid / accepted**. *Locked* definition:
  *accepted-but-invalid* = accepted by the verifier yet judged contradictory to
  the gold answer or unsupported by evidence. If `accepted_claims == 0`, the
  rate is `null` (never `0`).
* `cost` — total API spend in USD (always `0.0` in mock mode).

Development/demo metrics are explicitly **not** formal H1-01 evaluation metrics.

## 9. Quick Start

Requires `uv` (manages Python 3.11). From the repository root:

```bash
uv sync               # installs deps, resolves Python 3.11
uv run pytest         # all tests pass
uv run python experiments/H1-01-independent-verifier/run.py \
    --config experiments/H1-01-independent-verifier/config.yaml
```

Fully offline; no API key needed (`MOCK_LLM=true`).

## 10. Demo Results

Demo metrics are written to `results/H1-01/summary.json`. They are produced by a
deterministic mock and are reproducible. **They are not evidence that H1-01 is
proven**, and they are not formal H1-01 evaluation results. See the latest
`results/H1-01/summary.json` for the actual numbers from the last run.

## 11. Formal Frozen Set Status

**NOT ESTABLISHED.** Target size: 50 questions. It will be created once data
sources, time window, gold answers, scoring rubric, and contamination protocol
are fixed. Until then it is only documented, never claimed to exist. See
`data/frozen/README.md`.

## 12. Limitations

* Mock research agent and verifier are deterministic and rule-based; they do not
  reflect real LLM behavior or retrieval quality.
* Evidence is hand-authored fixture data, not real retrieval output.
* Gold-consistency in the judge is a naive token-subset check.
* `citation_correctness` checks URL well-formedness, not reachability or content
  accuracy.
* Demo metrics carry no statistical significance and no evidence value.

## 12a. Known Testing Limitations

* Unit tests cover schema, verifier, and metrics only; they do not test the
  retriever, judge, or pipeline as integration units.
* Tests assert the verifier's access isolation via source-scan and signature
  introspection; this is a structural check, not a runtime guarantee.
* Citation-correctness tests check URL well-formedness, not that URLs are live
  or that excerpts actually match the cited page.
* Deterministic fixtures mean the demo run never exercises retrieval failure or
  ambiguous-evidence edge cases beyond the hand-authored ones.
* No test asserts that the demo `summary.json` is byte-stable across runs (the
  `run_id` and `timestamp` are expected to differ).
* **Static gold-token test is weak.** `test_verifier_source_has_no_gold_answer_token`
  asserts the literal string `"gold_answer"` does not appear in the verifier
  source. It does not prove semantic isolation. This is mitigated by the P0
  signature test, but is not a substitute for a behavioral test.

## 13. Reproducibility

The mock pipeline is fully deterministic: fixed fixtures, fixed retrieval
timestamp, no randomness. Each run records a `run_id`, `timestamp`, hashes of
`config.yaml` and the demo data, and `experiment_status` in
`results/H1-01/summary.json`. `code_commit` is recorded as `none` because no git
commit was created.

## 14. Roadmap

* Establish the formal H1-01 Frozen Set (50 questions) after fixing the
  evaluation protocol.
* Replace mock components with real retrievers and, if sanctioned, a real LLM
  behind the `LLMClient` interface.
* Add a formal evaluation harness that runs against the inaccessible frozen set.
* Compare contamination rate with vs. without an independent verifier.
