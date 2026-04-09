"""
asag.cli -- Command-line interface for the ASAG perturbation framework.

Provides three subcommands:
  asag evaluate  -- Run full evaluation (load, perturb, grade, metrics)
  asag perturb   -- Generate perturbations only
  asag metrics   -- Compute metrics from existing results

Python 3.9 compatible: uses typing.Optional, typing.List, etc.
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import List, Optional


def _add_common_args(parser: argparse.ArgumentParser) -> None:
    """Add arguments shared across subcommands."""
    parser.add_argument(
        "--corpus",
        type=str,
        default="beetle",
        choices=["beetle", "scientsbank"],
        help="Dataset corpus to use (default: beetle)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)",
    )


def _cmd_evaluate(args: argparse.Namespace) -> None:
    """Run full evaluation pipeline."""
    from asag.evaluation import EvaluationEngine
    from asag.graders import HybridGrader, LLMGrader
    from asag.loaders import SemEval2013Loader
    from asag.perturbations import PerturbationEngine

    # Load data
    print(f"[1/4] Loading {args.corpus} corpus...")
    t0 = time.time()
    questions, answers = SemEval2013Loader(args.corpus).load()
    print(f"  Loaded: {len(questions)} questions, {len(answers)} answers ({time.time() - t0:.1f}s)")

    # Generate perturbations
    print("\n[2/4] Generating perturbations...")
    t1 = time.time()
    perturb_engine = PerturbationEngine(seed=args.seed)
    perturbations, gate_log = perturb_engine.generate_all(answers, questions)
    print(f"  Generated: {len(perturbations)} perturbations ({time.time() - t1:.0f}s)")

    # Build grader
    if args.grader == "hybrid":
        grader = HybridGrader()
    else:
        # Parse LLM grader spec: "openai:gpt-5.4-mini:0"
        parts = args.grader.split(":")
        if len(parts) != 3:
            print(
                "Error: LLM grader format must be provider:model:level "
                "(e.g. openai:gpt-5.4-mini:0)",
                file=sys.stderr,
            )
            sys.exit(1)
        provider, model, level_str = parts
        grader = LLMGrader(provider=provider, model=model, level=int(level_str))

    # Run evaluation
    protocols = args.protocols
    print(f"\n[3/4] Running evaluation (protocols: {protocols})...")
    t2 = time.time()
    eval_engine = EvaluationEngine(grader, corpus=args.corpus)

    run_dir = None  # type: Optional[Path]
    if args.output_dir:
        run_dir = Path(args.output_dir)

    result = eval_engine.run(
        questions, answers, perturbations,
        protocols=protocols,
        run_dir=run_dir,
    )
    print(f"  Evaluation complete ({time.time() - t2:.0f}s)")

    # Report results
    print(f"\n[4/4] Results for {result.grader_name} on {result.corpus}")
    print("=" * 60)

    if result.protocol_a_aggregate:
        print("\n--- Protocol A (LOQO) ---")
        for agg in result.protocol_a_aggregate:
            _print_metric(agg)

    if result.protocol_b_aggregate:
        print("\n--- Protocol B (Within-question) ---")
        for agg in result.protocol_b_aggregate:
            _print_metric(agg)

    if result.robustness_drop:
        print("\n--- Robustness Drop (A - B) ---")
        for row in result.robustness_drop:
            print(f"  {row}")


def _print_metric(agg) -> None:
    """Print a single aggregate MetricResult."""
    print(f"\n  Family: {agg.family} ({agg.n_pairs} pairs)")
    if agg.ivr_flip is not None:
        print(f"    IVR_flip:      {agg.ivr_flip:.3f}")
    if agg.ivr_absdelta is not None:
        print(f"    IVR_absdelta:  {agg.ivr_absdelta:.3f}")
    if agg.ssr_directional is not None:
        print(f"    SSR_dir:       {agg.ssr_directional:.3f}")
    if agg.asr_thresholded is not None:
        print(f"    ASR_thresh:    {agg.asr_thresholded:.3f}")


def _cmd_perturb(args: argparse.Namespace) -> None:
    """Generate perturbations only and save to disk."""
    from asag.infra import save_records
    from asag.loaders import SemEval2013Loader
    from asag.perturbations import PerturbationEngine

    print(f"[1/2] Loading {args.corpus} corpus...")
    questions, answers = SemEval2013Loader(args.corpus).load()
    print(f"  Loaded: {len(questions)} questions, {len(answers)} answers")

    print("\n[2/2] Generating perturbations (seed={})...".format(args.seed))
    t0 = time.time()
    engine = PerturbationEngine(seed=args.seed)
    perturbations, gate_log = engine.generate_all(answers, questions)
    elapsed = time.time() - t0
    print(f"  Generated: {len(perturbations)} perturbations ({elapsed:.0f}s)")

    # Report gate rejection rates
    rates = gate_log.rejection_rates()
    g1 = rates.get("gate1", {})
    for ptype, rate in g1.items():
        print(f"  Gate 1 rejection ({ptype}): {rate:.1%}")

    # Save output
    output_dir = Path(args.output_dir) if args.output_dir else Path("runs") / "perturbations"
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "perturbations.jsonl"
    save_records(perturbations, out_path)
    print(f"\n  Saved to {out_path}")


def _cmd_metrics(args: argparse.Namespace) -> None:
    """Compute metrics from an existing evaluation_result.json file."""
    results_path = Path(args.results_dir) / "evaluation_result.json"
    if not results_path.exists():
        print(f"Error: {results_path} not found", file=sys.stderr)
        sys.exit(1)

    with open(results_path, "r") as f:
        data = json.load(f)

    from asag.evaluation.engine import EvaluationResult

    result = EvaluationResult(**data)

    print(f"Grader: {result.grader_name}")
    print(f"Corpus: {result.corpus}")
    print(f"Protocols: {result.protocols_run}")

    if result.protocol_a_aggregate:
        print("\n--- Protocol A (LOQO) ---")
        for agg in result.protocol_a_aggregate:
            _print_metric(agg)

    if result.protocol_b_aggregate:
        print("\n--- Protocol B (Within-question) ---")
        for agg in result.protocol_b_aggregate:
            _print_metric(agg)

    if result.robustness_drop:
        print("\n--- Robustness Drop (A - B) ---")
        for row in result.robustness_drop:
            print(f"  {row}")


def main() -> None:
    """Entry point for the ``asag`` CLI."""
    parser = argparse.ArgumentParser(
        prog="asag",
        description="ASAG Perturbation Framework -- robustness evaluation for automated grading systems",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s " + _get_version(),
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # -- evaluate --
    eval_parser = subparsers.add_parser(
        "evaluate",
        help="Run full evaluation (load, perturb, grade, compute metrics)",
    )
    _add_common_args(eval_parser)
    eval_parser.add_argument(
        "--grader",
        type=str,
        default="hybrid",
        help=(
            "Grader to use. 'hybrid' for HybridGrader, or "
            "'provider:model:level' for LLM (e.g. openai:gpt-5.4-mini:0)"
        ),
    )
    eval_parser.add_argument(
        "--protocols",
        nargs="+",
        default=["A", "B"],
        choices=["A", "B"],
        help="Evaluation protocols to run (default: A B)",
    )
    eval_parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Directory to save results (default: auto-generated under runs/)",
    )

    # -- perturb --
    perturb_parser = subparsers.add_parser(
        "perturb",
        help="Generate perturbations only (no grading)",
    )
    _add_common_args(perturb_parser)
    perturb_parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Directory to save perturbations (default: runs/perturbations/)",
    )

    # -- metrics --
    metrics_parser = subparsers.add_parser(
        "metrics",
        help="Compute/display metrics from existing evaluation results",
    )
    metrics_parser.add_argument(
        "--results-dir",
        type=str,
        required=True,
        help="Path to directory containing evaluation_result.json",
    )

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    if args.command == "evaluate":
        _cmd_evaluate(args)
    elif args.command == "perturb":
        _cmd_perturb(args)
    elif args.command == "metrics":
        _cmd_metrics(args)


def _get_version() -> str:
    """Return the package version string."""
    from asag import __version__
    return __version__


if __name__ == "__main__":
    main()
