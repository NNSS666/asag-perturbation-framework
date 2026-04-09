"""
Floor-effect analysis for SSR (Sensitivity Success Rate).

SSR measures the proportion of sensitivity perturbations where the grader's
score decreased. However, answers already at score 0.0 cannot decrease
further, mechanically producing SSR = 0% on those pairs. This script
quantifies the floor effect and reports SSR with and without it.

Usage:
    PYTHONPATH=src python -m scripts.analyze_floor_effect \
        --cache runs/llm_grade_caches/llm_openai_gpt-5.4-mini_level0.jsonl \
        --label "GPT-5.4 mini L0"
"""

import argparse
import json
import sys
from typing import Dict, List, Tuple

from asag.loaders.semeval2013 import SemEval2013Loader
from asag.perturbations.generators.sensitivity import (
    KeyConceptDeletionGenerator,
    NegationInsertionGenerator,
    SemanticContradictionGenerator,
)


def load_grade_cache(path: str) -> Dict[Tuple[str, str], float]:
    """Load a grade cache JSONL into a (question, answer) -> score lookup."""
    lookup = {}
    with open(path) as f:
        for line in f:
            r = json.loads(line)
            lookup[(r["question"], r["student_answer"])] = r["score"]
    return lookup


def generate_sensitivity_pairs(
    answers: list, questions_by_id: dict
) -> List[Tuple]:
    """Generate all sensitivity perturbations (no SBERT needed)."""
    generators = [
        NegationInsertionGenerator(),
        KeyConceptDeletionGenerator(),
        SemanticContradictionGenerator(),
    ]
    pairs = []
    for i, a in enumerate(answers):
        q = questions_by_id[a.question_id]
        for gen in generators:
            try:
                for candidate in gen.generate(a, q, seed=42 + i):
                    pairs.append((a, candidate))
            except Exception:
                pass
    return pairs


def analyze_floor_effect(
    pairs: list,
    scores: dict,
    questions_by_id: dict,
) -> dict:
    """Compute SSR overall and split by floor (orig=0) vs non-floor (orig>0)."""
    total = success = 0
    floor_total = floor_success = 0
    nofloor_total = nofloor_success = 0
    missing = 0

    for a, pert_text in pairs:
        q = questions_by_id[a.question_id]
        orig_score = scores.get((q.prompt, a.student_answer))
        pert_score = scores.get((q.prompt, pert_text))

        if orig_score is None or pert_score is None:
            missing += 1
            continue

        total += 1
        decreased = round(pert_score, 6) < round(orig_score, 6)
        if decreased:
            success += 1

        if orig_score <= 0.001:
            floor_total += 1
            if decreased:
                floor_success += 1
        else:
            nofloor_total += 1
            if decreased:
                nofloor_success += 1

    return {
        "total": total,
        "success": success,
        "missing": missing,
        "floor_total": floor_total,
        "floor_success": floor_success,
        "nofloor_total": nofloor_total,
        "nofloor_success": nofloor_success,
    }


def main():
    parser = argparse.ArgumentParser(description="SSR floor-effect analysis")
    parser.add_argument("--cache", nargs="+", required=True, help="Grade cache JSONL path(s)")
    parser.add_argument("--label", nargs="+", required=True, help="Label(s) for each cache")
    args = parser.parse_args()

    if len(args.cache) != len(args.label):
        print("Error: --cache and --label must have the same number of arguments")
        sys.exit(1)

    # Load dataset
    loader = SemEval2013Loader("beetle")
    questions, answers = loader.load()
    q_by_id = {q.question_id: q for q in questions}

    # Generate sensitivity perturbations
    print("Generating sensitivity perturbations...")
    pairs = generate_sensitivity_pairs(answers, q_by_id)
    print(f"Generated {len(pairs)} sensitivity pairs\n")

    # Analyze each cache
    for cache_path, label in zip(args.cache, args.label):
        scores = load_grade_cache(cache_path)
        r = analyze_floor_effect(pairs, scores, q_by_id)

        ssr = r["success"] / r["total"]
        ssr_nf = r["nofloor_success"] / r["nofloor_total"] if r["nofloor_total"] else 0

        print(f"{'=' * 55}")
        print(f"  {label}")
        print(f"{'=' * 55}")
        print(f"  Sensitivity pairs:    {r['total']}  (unmatched: {r['missing']})")
        print(f"  SSR overall:          {ssr:.1%}  ({r['success']}/{r['total']})")
        print()
        print(f"  Floor (orig=0.0):     {r['floor_total']} pairs ({100 * r['floor_total'] / r['total']:.1f}%)")
        if r["floor_total"]:
            print(f"    SSR floor:          {r['floor_success'] / r['floor_total']:.1%}")
        print()
        print(f"  Non-floor (orig>0):   {r['nofloor_total']} pairs ({100 * r['nofloor_total'] / r['total']:.1f}%)")
        if r["nofloor_total"]:
            print(f"    SSR non-floor:      {ssr_nf:.1%}")
        print()
        print(f"  Floor effect:         SSR {ssr:.1%} -> {ssr_nf:.1%}  (+{(ssr_nf - ssr) * 100:.1f} pp)")
        print()


if __name__ == "__main__":
    main()
