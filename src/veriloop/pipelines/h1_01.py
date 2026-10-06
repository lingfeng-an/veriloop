"""H1-01 end-to-end pipeline.

    Demo Questions
        -> Research Agent (candidate claims)
        -> Evidence (mock retriever)
        -> Independent Verifier (ACCEPT / REJECT / NEEDS_REVIEW)
        -> Rule Judge (gold answer read ONLY here, after verification)
        -> Metrics
        -> results/H1-01/summary.json

The default run is fully deterministic and offline: ``MOCK_LLM=true``, no real
API, no API key. Output carries ``experiment_status=DEMO_ONLY_NOT_FORMAL_EVIDENCE``
and is never presented as formal H1-01 evidence.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from ..agents.research_agent import ResearchAgent
from ..eval.metrics import (
    compute_citation_correctness,
    compute_contamination_rate,
    compute_cost,
    compute_factual_accuracy,
    has_valid_citation,
)
from ..judges.rule_judge import RuleJudge
from ..llm import LLMClient, MockLLMClient
from ..retrievers.mock_retriever import MockRetriever
from ..schema import Claim, Evidence, ExperimentSummary, Question, VerificationResult
from ..verifiers.independent_verifier import IndependentVerifier

EXPERIMENT_STATUS = "DEMO_ONLY_NOT_FORMAL_EVIDENCE"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def load_questions(path: Path) -> list[Question]:
    questions: list[Question] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            questions.append(Question(**json.loads(line)))
    return questions


def run_pipeline(
    config_path: Path,
    demo_data_path: Path,
    results_dir: Path,
    prompts_dir: Path | None = None,
) -> tuple[ExperimentSummary, dict[str, Any]]:
    """Run the deterministic mock pipeline and return (summary, summary_dict)."""

    config = load_config(config_path)
    mock_llm = bool(config.get("mock_llm", True))
    if not mock_llm:
        raise RuntimeError(
            "Real LLM mode is not implemented in this MVP. Set MOCK_LLM=true."
        )

    llm: LLMClient = MockLLMClient()
    research_agent = ResearchAgent(llm=llm)
    retriever = MockRetriever()
    verifier = IndependentVerifier()
    judge = RuleJudge()

    questions = load_questions(demo_data_path)

    # ---- Research -> Evidence -> Verify -> Judge, one question at a time ----
    claims: list[Claim] = []
    evidence_by_id: dict[str, Evidence] = {}
    verifications: dict[str, VerificationResult] = {}
    accepted: list[Claim] = []
    accepted_invalid: int = 0
    valid_accepted: int = 0
    claims_with_citation: int = 0

    for q in questions:
        # Research agent sees only the question text (never gold).
        for claim in research_agent.generate_claims(q.id, q.question):
            claims.append(claim)
            evidence = retriever.retrieve(claim)
            claim.evidence_ids = [ev.id for ev in evidence]
            for ev in evidence:
                evidence_by_id[ev.id] = ev

            verification = verifier.verify(claim, evidence)
            verifications[claim.id] = verification

            if verification.decision == "ACCEPT":
                accepted.append(claim)
                # Judge reads gold ONLY after the verifier decision exists.
                verdict = judge.evaluate(claim, evidence, verification, q.gold_answer)
                if verdict.valid:
                    valid_accepted += 1
                else:
                    accepted_invalid += 1
                if has_valid_citation(claim, evidence_by_id):
                    claims_with_citation += 1

    accepted_claims = len(accepted)
    rejected_claims = sum(
        1 for v in verifications.values() if v.decision == "REJECT"
    )
    needs_review_claims = sum(
        1 for v in verifications.values() if v.decision == "NEEDS_REVIEW"
    )

    factual_accuracy = compute_factual_accuracy(valid_accepted, accepted_claims)
    citation_correctness = compute_citation_correctness(
        accepted_claims, claims_with_citation
    )
    contamination_rate = compute_contamination_rate(accepted_invalid, accepted_claims)
    cost = compute_cost(llm)

    summary = ExperimentSummary(
        total_questions=len(questions),
        total_claims=len(claims),
        accepted_claims=accepted_claims,
        rejected_claims=rejected_claims,
        needs_review_claims=needs_review_claims,
        factual_accuracy=factual_accuracy,
        citation_correctness=citation_correctness,
        contamination_rate=contamination_rate,
        cost=cost,
    )

    summary_dict = _build_summary_dict(
        summary=summary,
        config=config,
        config_path=config_path,
        demo_data_path=demo_data_path,
        mock_llm=mock_llm,
    )

    results_dir.mkdir(parents=True, exist_ok=True)
    out_path = results_dir / "summary.json"
    out_path.write_text(
        json.dumps(summary_dict, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    return summary, summary_dict


def _build_summary_dict(
    summary: ExperimentSummary,
    config: dict[str, Any],
    config_path: Path,
    demo_data_path: Path,
    mock_llm: bool,
) -> dict[str, Any]:
    return {
        "run_metadata": {
            "run_id": str(uuid.uuid4()),
            "timestamp": datetime.now(UTC).isoformat(),
            "mock_llm": mock_llm,
            "config_hash": _sha256(config_path),
            "demo_data_hash": _sha256(demo_data_path),
            "code_commit": config.get("run_metadata", {}).get("code_commit", "none"),
            "experiment_status": EXPERIMENT_STATUS,
        },
        "metrics": summary.model_dump(),
    }
