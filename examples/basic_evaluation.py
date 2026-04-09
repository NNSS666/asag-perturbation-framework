#!/usr/bin/env python
"""
basic_evaluation.py -- Minimal end-to-end ASAG robustness evaluation.

Demonstrates the core workflow:
  1. Load the Beetle corpus from HuggingFace
  2. Generate perturbations (7 types across 3 families)
  3. Grade original + perturbed answers with HybridGrader
  4. Compute robustness metrics under Protocol A and B
  5. Report the robustness drop (the central thesis metric)

Requirements:
  pip install asag-perturbation

Usage:
  python examples/basic_evaluation.py
"""

import time

from asag import (
    EvaluationEngine,
    HybridGrader,
    PerturbationEngine,
    SemEval2013Loader,
)


def main() -> None:
    # ----------------------------------------------------------------
    # Step 1: Load the Beetle corpus
    # ----------------------------------------------------------------
    # SemEval2013Loader concatenates all HuggingFace splits into a single
    # pool. Protocol A/B splitting happens later inside EvaluationEngine.
    print("Step 1: Loading Beetle corpus from HuggingFace...")
    t0 = time.time()
    loader = SemEval2013Loader("beetle")
    questions, answers = loader.load()
    print(f"  {len(questions)} questions, {len(answers)} answers ({time.time() - t0:.1f}s)")

    # ----------------------------------------------------------------
    # Step 2: Generate perturbations
    # ----------------------------------------------------------------
    # PerturbationEngine runs all 7 generators and applies quality gates.
    # Gate 1 (SBERT cosine >= 0.85) filters synonym substitutions.
    # Gate 2 (negation heuristic) filters all invariance perturbations.
    # Rejected candidates are NOT retried -- the rejection rate itself
    # is a research result.
    print("\nStep 2: Generating perturbations (seed=42)...")
    t1 = time.time()
    perturb_engine = PerturbationEngine(seed=42)
    perturbations, gate_log = perturb_engine.generate_all(answers, questions)
    print(f"  {len(perturbations)} perturbations ({time.time() - t1:.0f}s)")
    print(f"  Average per answer: {len(perturbations) / len(answers):.1f}")

    # Show gate rejection rates (if any)
    rates = gate_log.rejection_rates()
    for ptype, rate in rates.get("gate1", {}).items():
        print(f"  Gate 1 rejection ({ptype}): {rate:.1%}")

    # ----------------------------------------------------------------
    # Step 3: Run evaluation under both protocols
    # ----------------------------------------------------------------
    # Protocol A (LOQO): Leave-One-Question-Out cross-validation.
    #   Tests cross-question generalization of the grader.
    # Protocol B: Within-question 80/20 stratified split.
    #   Tests in-distribution performance.
    # The delta between A and B is the "robustness drop" -- the central
    # metric of the thesis.
    print("\nStep 3: Running EvaluationEngine (protocols A + B)...")
    print("  Protocol A trains HybridGrader once per question fold...")
    t2 = time.time()

    grader = HybridGrader()
    eval_engine = EvaluationEngine(grader, corpus="beetle")
    result = eval_engine.run(
        questions, answers, perturbations,
        protocols=["A", "B"],
    )
    print(f"  Complete ({time.time() - t2:.0f}s)")

    # ----------------------------------------------------------------
    # Step 4: Report results
    # ----------------------------------------------------------------
    print("\n" + "=" * 60)
    print(f"Results: {result.grader_name} on {result.corpus}")
    print("=" * 60)

    # Protocol A aggregate metrics
    if result.protocol_a_aggregate:
        print("\nProtocol A (LOQO -- cross-question):")
        for agg in result.protocol_a_aggregate:
            print(f"  {agg.family} ({agg.n_pairs} pairs):")
            if agg.ivr_flip is not None:
                print(f"    IVR_flip:     {agg.ivr_flip:.3f}")
            if agg.ivr_absdelta is not None:
                print(f"    IVR_absdelta: {agg.ivr_absdelta:.3f}")
            if agg.ssr_directional is not None:
                print(f"    SSR_dir:      {agg.ssr_directional:.3f}")
            if agg.asr_thresholded is not None:
                print(f"    ASR_thresh:   {agg.asr_thresholded:.3f}")

    # Protocol B aggregate metrics
    if result.protocol_b_aggregate:
        print("\nProtocol B (within-question -- in-distribution):")
        for agg in result.protocol_b_aggregate:
            print(f"  {agg.family} ({agg.n_pairs} pairs):")
            if agg.ivr_flip is not None:
                print(f"    IVR_flip:     {agg.ivr_flip:.3f}")
            if agg.ivr_absdelta is not None:
                print(f"    IVR_absdelta: {agg.ivr_absdelta:.3f}")
            if agg.ssr_directional is not None:
                print(f"    SSR_dir:      {agg.ssr_directional:.3f}")
            if agg.asr_thresholded is not None:
                print(f"    ASR_thresh:   {agg.asr_thresholded:.3f}")

    # Robustness drop (the key thesis metric)
    if result.robustness_drop:
        print("\nRobustness Drop (Protocol A - Protocol B):")
        for row in result.robustness_drop:
            print(f"  {row}")

    print("\nDone.")


if __name__ == "__main__":
    main()
