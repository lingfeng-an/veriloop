# H1-01 — Independent Verifier Minimal Experiment

**Experiment dir:** `experiments/H1-01-independent-verifier/`
**Pipeline code:** `src/veriloop/pipelines/h1_01.py`

## Hypothesis

**H1-01.** Introducing an independent verifier that admits claims based only on
retrieved evidence — with no access to gold answers — lowers the contamination
rate (accepted-but-invalid claims) entering a formal knowledge base.

## Research Question

> Can an independent verifier reduce erroneous knowledge claims entering a
> formal knowledge base?

## Variables

* **Independent variable:** presence of the independent verifier (current
  pipeline always includes it; a future baseline would omit it).
* **Dependent variables:** contamination rate, factual accuracy, citation
  correctness, cost.
* **Held fixed:** demo questions, mock fixtures, retrieval timestamp, verifier
  and judge rules, offline `MOCK_LLM=true`.

## Pipeline

```
Research → Evidence → Independent Verification → Knowledge → Evaluation
```

Concretely: demo questions → research agent (candidate claims) → mock retriever
(evidence) → independent verifier (`ACCEPT` / `REJECT` / `NEEDS_REVIEW`) → rule
judge (reads gold **after** verification) → metrics → `results/H1-01/summary.json`.

The verifier entry point is `verify(claim, evidence)` only — no `Question`, no
`gold_answer`, no object that carries a gold answer. The judge is the only layer
that reads gold answers, and only after the verifier emits its decision.

## Metrics

* `factual_accuracy` — valid accepted / accepted (null when 0).
* `citation_correctness` — accepted with valid citation / accepted.
* `contamination_rate` — **accepted-but-invalid / accepted**; null when
  `accepted_claims == 0`.
* `cost` — USD (0.0 in mock mode).

## Current Demo Status

The current implementation is a **reproducible MVP/demo** and does **not**
constitute formal evidence for H1-01. It runs offline with `MOCK_LLM=true`, uses
the 10-question demo set and hand-authored fixtures, and writes deterministic
metrics to `results/H1-01/summary.json`.

## Formal Frozen Set Status

**Not established.** Target size: 50 questions. Will be created only after data
sources, time window, gold answers, scoring rubric, and contamination protocol
are decided. Must remain inaccessible to the research agent, training pipeline,
and knowledge-accumulation pipeline until evaluation. See
`data/frozen/README.md`.

## Threats to Validity

* Mock research agent/verifier are rule-based, not real LLMs; results do not
  generalize.
* Evidence is hand-authored; real retrieval would behave differently.
* Judge gold-consistency is a naive token-subset match.
* No baseline (without verifier) is yet implemented, so no causal claim is
  supported.
* Demo sample (10 questions) is far too small and non-random.

## Future Formal Evaluation

* Build the inaccessible 50-question frozen set.
* Implement a real retriever and, if sanctioned, a real LLM behind
  `LLMClient`.
* Add a no-verifier baseline arm.
* Run a pre-registered evaluation on the frozen set and report statistics, not
  demo anecdotes.
