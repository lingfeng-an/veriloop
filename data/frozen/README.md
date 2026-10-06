# Formal H1-01 Frozen Set — Status

**Formal H1-01 frozen evaluation set is not yet established.**

Target size: **50 questions**.

The formal frozen set must remain inaccessible to:

1. **Research Agent**
2. **Training pipeline**
3. **Knowledge accumulation pipeline**

until evaluation.

## What is allowed right now

- `data/demo_questions.jsonl` (10 public, development-only questions) may be
  used for development, unit tests, pipeline smoke tests, and mock
  demonstration. It is **not** the frozen set.
- No formal frozen set files are created, published, or placed here yet.

## When the frozen set will be established

A formal H1-01 Frozen Set will only be created once the following are decided
and recorded:

- Data sources and provenance policy
- Time window / snapshot date of the underlying sources
- Gold answers and their citation requirements
- Scoring rubric (factual accuracy, citation correctness, contamination)
- Contamination protocol (how to prevent the research/accumulation stacks from
  ever seeing the frozen set prior to evaluation)

Until those decisions are made, this directory must remain effectively empty of
evaluation items (aside from this README). Do not fabricate or pre-claim a
frozen set that does not yet exist.
