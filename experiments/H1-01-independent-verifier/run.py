"""H1-01 demo runner.

Usage (from the repository root):

    uv run python experiments/H1-01-independent-verifier/run.py \
        --config experiments/H1-01-independent-verifier/config.yaml

Writes results to ``results/H1-01/summary.json``. Fully offline; MOCK_LLM=true.
"""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from veriloop.pipelines.h1_01 import EXPERIMENT_STATUS, load_config, run_pipeline

app = typer.Typer()
console = Console()

# Repository root = two directories above this script
# (run.py -> H1-01-independent-verifier -> experiments -> repo root).
REPO_ROOT = Path(__file__).resolve().parents[2]


def _resolve(path_str: str) -> Path:
    p = Path(path_str)
    return p if p.is_absolute() else REPO_ROOT / p


@app.command()
def main(
    config: Path = typer.Option(  # noqa: B008 - typer requires call-in-default pattern
        "experiments/H1-01-independent-verifier/config.yaml",
        "--config",
        help="Path to the experiment config.yaml.",
    ),
) -> None:
    config_path = _resolve(str(config))
    cfg = load_config(config_path)
    demo_data_path = _resolve(str(cfg["demo_data"]))
    results_dir = _resolve(str(cfg["results_dir"]))

    console.print(
        Panel(
            f"config={config_path}\n"
            f"demo_data={demo_data_path}\n"
            f"mock_llm={cfg.get('mock_llm', True)}",
            title="H1-01 — Independent Verifier (Demo run)",
        )
    )

    summary, _ = run_pipeline(config_path, demo_data_path, results_dir)

    table = Table(title="H1-01 Demo Metrics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("total_questions", str(summary.total_questions))
    table.add_row("total_claims", str(summary.total_claims))
    table.add_row("accepted_claims", str(summary.accepted_claims))
    table.add_row("rejected_claims", str(summary.rejected_claims))
    table.add_row("needs_review_claims", str(summary.needs_review_claims))
    table.add_row("factual_accuracy", _fmt(summary.factual_accuracy))
    table.add_row("citation_correctness", _fmt(summary.citation_correctness))
    table.add_row("contamination_rate", _fmt(summary.contamination_rate))
    table.add_row("cost (USD)", f"{summary.cost:.4f}")
    console.print(table)

    console.print(
        Panel(
            f"summary.json written to: {results_dir / 'summary.json'}\n"
            f"experiment_status: {EXPERIMENT_STATUS}\n\n"
            "This is a reproducible mock/demo. It is NOT formal evidence for "
            "H1-01. The formal frozen set is not yet established.",
            title="Status",
        )
    )


def _fmt(value: float | None) -> str:
    return "null" if value is None else f"{value:.4f}"


if __name__ == "__main__":
    app()
