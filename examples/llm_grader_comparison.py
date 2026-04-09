#!/usr/bin/env python
"""
llm_grader_comparison.py -- Compare LLMGrader at Level 0 vs Level 1.

Demonstrates the reference-answer trade-off:
  - Level 0 (L0): The grader sees only the question and student answer.
    Simulates a setting where no gold reference is available.
  - Level 1 (L1): The grader also sees the reference answer.
    Simulates a setting where rubric/reference is provided.

This comparison reveals whether access to the reference answer improves
grader robustness (lower IVR, higher SSR) or just raw accuracy.

Requirements:
  pip install asag-perturbation[llm]
  export OPENAI_API_KEY=your-key-here  # or ANTHROPIC_API_KEY / GOOGLE_API_KEY

Usage:
  python examples/llm_grader_comparison.py
  python examples/llm_grader_comparison.py --provider openai --model gpt-5.4-mini
  python examples/llm_grader_comparison.py --provider google --model gemini-2.5-flash
"""

import argparse
import time
from typing import List

from asag import (
    EvaluationEngine,
    EvaluationResult,
    LLMGrader,
    PerturbationEngine,
    SemEval2013Loader,
)


def run_single_config(
    provider: str,
    model: str,
    level: int,
    questions: list,
    answers: list,
    perturbations: list,
    protocols: List[str],
) -> EvaluationResult:
    """Run evaluation for a single LLMGrader configuration.

    Args:
        provider:      LLM provider ("openai", "anthropic", "google").
        model:         Model identifier (e.g. "gpt-5.4-mini").
        level:         Information level: 0 (no reference) or 1 (with reference).
        questions:     List of QuestionRecord instances.
        answers:       List of AnswerRecord instances.
        perturbations: List of PerturbationRecord instances.
        protocols:     Which protocols to run (["A"], ["B"], or ["A", "B"]).

    Returns:
        EvaluationResult for this configuration.
    """
    label = f"{provider}/{model} L{level}"
    print(f"\n--- Evaluating: {label} ---")
    t0 = time.time()

    grader = LLMGrader(provider=provider, model=model, level=level)
    engine = EvaluationEngine(grader, corpus="beetle")
    result = engine.run(questions, answers, perturbations, protocols=protocols)

    print(f"  Complete ({time.time() - t0:.0f}s)")
    return result


def print_comparison(
    result_l0: EvaluationResult,
    result_l1: EvaluationResult,
) -> None:
    """Print side-by-side comparison of L0 vs L1 results.

    Args:
        result_l0: EvaluationResult from Level 0 run.
        result_l1: EvaluationResult from Level 1 run.
    """
    print("\n" + "=" * 70)
    print("COMPARISON: Level 0 (no reference) vs Level 1 (with reference)")
    print("=" * 70)

    # Compare Protocol B aggregates (within-question, more stable)
    aggs_l0 = {a.family: a for a in result_l0.protocol_b_aggregate}
    aggs_l1 = {a.family: a for a in result_l1.protocol_b_aggregate}

    families = sorted(set(list(aggs_l0.keys()) + list(aggs_l1.keys())))

    for family in families:
        a0 = aggs_l0.get(family)
        a1 = aggs_l1.get(family)

        print(f"\n  Family: {family}")
        print(f"  {'Metric':<16} {'L0':>8} {'L1':>8} {'Delta':>8}")
        print(f"  {'-' * 44}")

        # IVR_flip (invariance family)
        if a0 and a0.ivr_flip is not None and a1 and a1.ivr_flip is not None:
            delta = a1.ivr_flip - a0.ivr_flip
            print(f"  {'IVR_flip':<16} {a0.ivr_flip:>8.3f} {a1.ivr_flip:>8.3f} {delta:>+8.3f}")

        # IVR_absdelta (invariance family)
        if a0 and a0.ivr_absdelta is not None and a1 and a1.ivr_absdelta is not None:
            delta = a1.ivr_absdelta - a0.ivr_absdelta
            print(f"  {'IVR_absdelta':<16} {a0.ivr_absdelta:>8.3f} {a1.ivr_absdelta:>8.3f} {delta:>+8.3f}")

        # SSR_directional (sensitivity family)
        if a0 and a0.ssr_directional is not None and a1 and a1.ssr_directional is not None:
            delta = a1.ssr_directional - a0.ssr_directional
            print(f"  {'SSR_dir':<16} {a0.ssr_directional:>8.3f} {a1.ssr_directional:>8.3f} {delta:>+8.3f}")

        # ASR_thresholded (gaming family)
        if a0 and a0.asr_thresholded is not None and a1 and a1.asr_thresholded is not None:
            delta = a1.asr_thresholded - a0.asr_thresholded
            print(f"  {'ASR_thresh':<16} {a0.asr_thresholded:>8.3f} {a1.asr_thresholded:>8.3f} {delta:>+8.3f}")

    print("\nInterpretation:")
    print("  - Lower IVR is better (fewer invariance violations)")
    print("  - Higher SSR is better (grader detects sensitivity perturbations)")
    print("  - Lower ASR is better (grader resists gaming attempts)")
    print("  - Negative IVR delta means L1 is more robust to paraphrases")
    print("  - Positive SSR delta means L1 better detects meaning changes")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare LLMGrader Level 0 vs Level 1 robustness",
    )
    parser.add_argument(
        "--provider",
        type=str,
        default="openai",
        choices=["openai", "anthropic", "google"],
        help="LLM provider (default: openai)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-5.4-mini",
        help="Model ID (default: gpt-5.4-mini)",
    )
    parser.add_argument(
        "--protocols",
        nargs="+",
        default=["B"],
        choices=["A", "B"],
        help="Evaluation protocols (default: B only, for speed)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed (default: 42)",
    )
    args = parser.parse_args()

    # Load data (shared across both runs)
    print("Loading Beetle corpus...")
    questions, answers = SemEval2013Loader("beetle").load()
    print(f"  {len(questions)} questions, {len(answers)} answers")

    # Generate perturbations (shared across both runs)
    print("\nGenerating perturbations...")
    t0 = time.time()
    perturb_engine = PerturbationEngine(seed=args.seed)
    perturbations, gate_log = perturb_engine.generate_all(answers, questions)
    print(f"  {len(perturbations)} perturbations ({time.time() - t0:.0f}s)")

    # Run Level 0 (no reference answer)
    result_l0 = run_single_config(
        provider=args.provider,
        model=args.model,
        level=0,
        questions=questions,
        answers=answers,
        perturbations=perturbations,
        protocols=args.protocols,
    )

    # Run Level 1 (with reference answer)
    result_l1 = run_single_config(
        provider=args.provider,
        model=args.model,
        level=1,
        questions=questions,
        answers=answers,
        perturbations=perturbations,
        protocols=args.protocols,
    )

    # Side-by-side comparison
    print_comparison(result_l0, result_l1)

    print("\nDone.")


if __name__ == "__main__":
    main()
