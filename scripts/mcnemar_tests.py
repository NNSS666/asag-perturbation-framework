"""McNemar paired tests on grader miss patterns.

Two test families:

A) Within-grader, between perturbation types (the gradient-of-blindness claim).
   For each grader (L0, L1), pairwise McNemar on the same answer_id:
     - deletion vs negation
     - deletion vs contradiction
     - negation vs contradiction
   Pairing: one perturbation per (answer_id, type), deterministic by perturbation order.
   "Miss" = orig_score == pert_score (grader did not change score under perturbation).

B) Between graders, within perturbation type (the L1-deletion paradox).
   For each sensitivity type, paired McNemar on the SAME (orig, perturbed) pair
   evaluated by L0 vs L1.

Output:
  - stdout: formatted table per family
  - runs/analysis/mcnemar_tests.json: machine-readable dump

Requires: statsmodels.
"""

import json
from collections import defaultdict
from pathlib import Path

from statsmodels.stats.contingency_tables import mcnemar

ROOT = Path(__file__).resolve().parent.parent

SENSITIVITY_TYPES = [
    "negation_insertion",
    "key_concept_deletion",
    "semantic_contradiction",
]

GRADERS = {
    "L0": ROOT / "runs/llm_grade_caches/llm_openai_gpt-5.4-mini_level0.jsonl",
    "L1": ROOT / "runs/llm_grade_caches/llm_openai_gpt-5.4-mini_level1.jsonl",
}

PAIRWISE_TYPE_COMPARISONS = [
    ("key_concept_deletion", "negation_insertion"),
    ("key_concept_deletion", "semantic_contradiction"),
    ("negation_insertion", "semantic_contradiction"),
]


def load_cache(path):
    cache = {}
    with open(path) as f:
        for line in f:
            entry = json.loads(line)
            cache[(entry["question"], entry["student_answer"])] = entry
    return cache


def is_miss(orig, pert):
    return round(orig, 6) == round(pert, 6)


def build_miss_map(perturbations, cache, q_lookup, a_lookup):
    """Per (answer_id, type), pick the first perturbation present in cache and
    classify miss(orig, pert). Returns dict[(aid, type)] -> int (0/1)."""
    seen = set()
    out = {}
    for p in perturbations:
        if p.type not in SENSITIVITY_TYPES:
            continue
        key = (p.answer_id, p.type)
        if key in seen:
            continue
        a = a_lookup[p.answer_id]
        q = q_lookup[a.question_id]
        ok = (q.prompt, a.student_answer)
        pk = (q.prompt, p.text)
        if ok not in cache or pk not in cache:
            continue
        os_ = cache[ok]["score"]
        ps_ = cache[pk]["score"]
        out[key] = 1 if is_miss(os_, ps_) else 0
        seen.add(key)
    return out


def build_paired(miss_map, type_a, type_b):
    """Return (a, b, c, d, n) for paired observations on the same answer_id."""
    a = b = c = d = 0
    common = 0
    aids_a = {aid for (aid, t) in miss_map if t == type_a}
    aids_b = {aid for (aid, t) in miss_map if t == type_b}
    common_aids = aids_a & aids_b
    for aid in common_aids:
        ma = miss_map[(aid, type_a)]
        mb = miss_map[(aid, type_b)]
        if ma == 1 and mb == 1:
            a += 1
        elif ma == 1 and mb == 0:
            b += 1
        elif ma == 0 and mb == 1:
            c += 1
        else:
            d += 1
        common += 1
    return a, b, c, d, common


def build_paired_cross_grader(miss_a, miss_b, ptype):
    """Same (answer_id, ptype) evaluated under two graders: pair (miss_L0, miss_L1)."""
    a = b = c = d = 0
    common = 0
    keys_a = {k for k in miss_a if k[1] == ptype}
    keys_b = {k for k in miss_b if k[1] == ptype}
    common_keys = keys_a & keys_b
    for k in common_keys:
        ma = miss_a[k]
        mb = miss_b[k]
        if ma == 1 and mb == 1:
            a += 1
        elif ma == 1 and mb == 0:
            b += 1
        elif ma == 0 and mb == 1:
            c += 1
        else:
            d += 1
        common += 1
    return a, b, c, d, common


def run_mcnemar(a, b, c, d):
    table = [[a, b], [c, d]]
    res = mcnemar(table, exact=False, correction=True)
    return {
        "chi2": float(res.statistic),
        "p_value": float(res.pvalue),
        "table": table,
        "discordant_b": b,
        "discordant_c": c,
    }


def fmt_p(p):
    if p < 0.0001:
        return "<0.0001"
    return f"{p:.4f}"


def sig_marker(p):
    if p < 0.001:
        return "***"
    if p < 0.01:
        return "**"
    if p < 0.05:
        return "*"
    return "ns"


def print_family_a(results):
    print("\n" + "=" * 100)
    print("FAMILY A — Within-grader, between perturbation types (gradient-of-blindness)")
    print("=" * 100)
    hdr = f"{'Grader':<6} {'Comparison':<46} {'n':>6} {'b':>6} {'c':>6} {'chi2':>10} {'p-value':>10} {'sig':>4}"
    print(hdr)
    print("-" * 100)
    for grader, comps in results.items():
        for comp_name, r in comps.items():
            print(
                f"{grader:<6} {comp_name:<46} "
                f"{r['n']:>6} {r['discordant_b']:>6} {r['discordant_c']:>6} "
                f"{r['chi2']:>10.2f} {fmt_p(r['p_value']):>10} {sig_marker(r['p_value']):>4}"
            )
        print()


def print_family_b(results):
    print("\n" + "=" * 100)
    print("FAMILY B — Between graders (L0 vs L1), same perturbation type (paradox check)")
    print("=" * 100)
    hdr = f"{'Type':<26} {'n':>6} {'b (L0 miss only)':>20} {'c (L1 miss only)':>20} {'chi2':>10} {'p-value':>10} {'sig':>4}"
    print(hdr)
    print("-" * 100)
    for ptype, r in results.items():
        print(
            f"{ptype:<26} "
            f"{r['n']:>6} {r['discordant_b']:>20} {r['discordant_c']:>20} "
            f"{r['chi2']:>10.2f} {fmt_p(r['p_value']):>10} {sig_marker(r['p_value']):>4}"
        )
    print()
    print("Interpretation:")
    print("  b > c  =>  L0 misses more  =>  L1 helps detection on this type")
    print("  c > b  =>  L1 misses more  =>  L1 hurts detection on this type")


def main():
    from asag.loaders.semeval2013 import SemEval2013Loader
    from asag.perturbations.engine import PerturbationEngine

    print("Loading dataset and generating perturbations...")
    loader = SemEval2013Loader(corpus="beetle")
    questions, answers = loader.load()
    engine = PerturbationEngine()
    perturbations, _ = engine.generate_all(answers, questions)

    q_lookup = {q.question_id: q for q in questions}
    a_lookup = {a.answer_id: a for a in answers}

    miss_maps = {}
    for grader_name, cache_path in GRADERS.items():
        if not cache_path.exists():
            print(f"Skipping {grader_name}: cache not found")
            continue
        print(f"[{grader_name}] loading cache + building miss map...")
        cache = load_cache(cache_path)
        miss_maps[grader_name] = build_miss_map(perturbations, cache, q_lookup, a_lookup)
        n_by_type = defaultdict(int)
        for (_, t) in miss_maps[grader_name]:
            n_by_type[t] += 1
        for t in SENSITIVITY_TYPES:
            print(f"    {t:<26} n_paired_units={n_by_type[t]}")

    family_a = {}
    for grader_name, mm in miss_maps.items():
        family_a[grader_name] = {}
        for ta, tb in PAIRWISE_TYPE_COMPARISONS:
            a, b, c, d, n = build_paired(mm, ta, tb)
            comp_name = f"{ta} vs {tb}"
            res = run_mcnemar(a, b, c, d)
            res["n"] = n
            family_a[grader_name][comp_name] = res

    family_b = {}
    if "L0" in miss_maps and "L1" in miss_maps:
        for ptype in SENSITIVITY_TYPES:
            a, b, c, d, n = build_paired_cross_grader(
                miss_maps["L0"], miss_maps["L1"], ptype
            )
            res = run_mcnemar(a, b, c, d)
            res["n"] = n
            family_b[ptype] = res

    print_family_a(family_a)
    print_family_b(family_b)

    out_dir = ROOT / "runs/analysis"
    out_dir.mkdir(exist_ok=True, parents=True)
    out = out_dir / "mcnemar_tests.json"
    with open(out, "w") as f:
        json.dump({"family_a": family_a, "family_b": family_b}, f, indent=2)
    print(f"\nResults saved to: {out}")


if __name__ == "__main__":
    main()
