"""Deep analysis of sensitivity perturbations: stratification + bootstrap CI.

Extends analyze_sensitivity_patterns.py with:
  - Stratification by question_id (uniformity vs concentration of failures)
  - Stratification by answer length bucket (short/medium/long)
  - Bootstrap percentile 95 percent CI for aggregate percentages (10k resamples)
  - Ranking of worst and best questions per (grader, type)

Output:
  - stdout: human-readable report
  - runs/analysis/sensitivity_deep.json: machine-readable dump
"""

import json
import random
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
N_BOOTSTRAP = 10000
SEED = 42
MIN_PER_QUESTION = 20  # minimum pairs per question for ranking eligibility

SENSITIVITY_TYPES = [
    "negation_insertion",
    "key_concept_deletion",
    "semantic_contradiction",
]

GRADERS = {
    "L0": ROOT / "runs/llm_grade_caches/llm_openai_gpt-5.4-mini_level0.jsonl",
    "L1": ROOT / "runs/llm_grade_caches/llm_openai_gpt-5.4-mini_level1.jsonl",
}


def load_cache(path):
    cache = {}
    with open(path) as f:
        for line in f:
            entry = json.loads(line)
            key = (entry["question"], entry["student_answer"])
            cache[key] = entry
    return cache


def classify(orig, pert):
    o = round(orig, 6)
    p = round(pert, 6)
    if p < o:
        return "dec"
    if p > o:
        return "inc"
    return "same"


def build_pairs(perturbations, cache, q_lookup, a_lookup, ptype):
    pairs = []
    for p in perturbations:
        if p.type != ptype:
            continue
        a = a_lookup[p.answer_id]
        q = q_lookup[a.question_id]
        orig_key = (q.prompt, a.student_answer)
        pert_key = (q.prompt, p.text)
        if orig_key not in cache or pert_key not in cache:
            continue
        orig = cache[orig_key]["score"]
        pert = cache[pert_key]["score"]
        pairs.append({
            "question_id": a.question_id,
            "gold": a.gold_label,
            "answer_length": len(a.student_answer.split()),
            "orig_score": orig,
            "pert_score": pert,
            "cls": classify(orig, pert),
        })
    return pairs


def bootstrap_ci(cls_list, n_boot=N_BOOTSTRAP, seed=SEED):
    """Percentile bootstrap 95% CI for dec/same/inc proportions."""
    rng = random.Random(seed)
    n = len(cls_list)
    if n == 0:
        return {"dec": (0, 0), "same": (0, 0), "inc": (0, 0)}
    dec_s, same_s, inc_s = [], [], []
    for _ in range(n_boot):
        sample = rng.choices(cls_list, k=n)
        dec_s.append(sample.count("dec") / n)
        same_s.append(sample.count("same") / n)
        inc_s.append(sample.count("inc") / n)
    dec_s.sort()
    same_s.sort()
    inc_s.sort()
    lo = int(0.025 * n_boot)
    hi = int(0.975 * n_boot)
    return {
        "dec": (dec_s[lo], dec_s[hi]),
        "same": (same_s[lo], same_s[hi]),
        "inc": (inc_s[lo], inc_s[hi]),
    }


def by_question(pairs):
    agg = defaultdict(lambda: {"dec": 0, "same": 0, "inc": 0, "total": 0})
    for p in pairs:
        agg[p["question_id"]][p["cls"]] += 1
        agg[p["question_id"]]["total"] += 1
    return {k: dict(v) for k, v in agg.items()}


def by_length(pairs):
    buckets = {"short": [], "medium": [], "long": []}
    for p in pairs:
        L = p["answer_length"]
        if L < 10:
            buckets["short"].append(p)
        elif L <= 20:
            buckets["medium"].append(p)
        else:
            buckets["long"].append(p)
    return buckets


def pair_stats(pairs):
    n = len(pairs)
    if n == 0:
        return None
    dec = sum(1 for p in pairs if p["cls"] == "dec")
    same = sum(1 for p in pairs if p["cls"] == "same")
    inc = sum(1 for p in pairs if p["cls"] == "inc")
    return {
        "n": n,
        "dec_pct": dec / n * 100,
        "same_pct": same / n * 100,
        "inc_pct": inc / n * 100,
    }


def print_bootstrap_table(results):
    print("\n" + "=" * 108)
    print("BOOTSTRAP 95% CI — Sensitivity aggregate distribution (10k resamples)")
    print("=" * 108)
    hdr = f"{'Grader':<6} {'Type':<24} {'Dec% [95% CI]':<24} {'Same% [95% CI]':<24} {'Inc% [95% CI]':<24}"
    print(hdr)
    print("-" * 108)
    for grader, by_type in results.items():
        for ptype in SENSITIVITY_TYPES:
            if ptype not in by_type:
                continue
            r = by_type[ptype]
            ci = r["ci_95"]
            d = f"{r['dec_pct']:5.1f} [{ci['dec'][0]:.1f}, {ci['dec'][1]:.1f}]"
            s = f"{r['same_pct']:5.1f} [{ci['same'][0]:.1f}, {ci['same'][1]:.1f}]"
            i = f"{r['inc_pct']:5.1f} [{ci['inc'][0]:.1f}, {ci['inc'][1]:.1f}]"
            print(f"{grader:<6} {ptype:<24} {d:<24} {s:<24} {i:<24}")
        print()


def print_length_table(results):
    print("\n" + "=" * 100)
    print("STRATIFICATION BY ANSWER LENGTH — same% (miss rate) per bucket")
    print("=" * 100)
    print(f"{'Grader':<6} {'Type':<24} {'Short (<10w)':<22} {'Medium (10-20w)':<22} {'Long (>20w)':<22}")
    print("-" * 100)
    for grader, by_type in results.items():
        for ptype in SENSITIVITY_TYPES:
            if ptype not in by_type:
                continue
            bl = by_type[ptype]["by_length"]

            def fmt(b):
                if b is None:
                    return "--"
                return f"{b['same_pct']:5.1f}% (n={b['n']})"

            print(f"{grader:<6} {ptype:<24} {fmt(bl['short']):<22} {fmt(bl['medium']):<22} {fmt(bl['long']):<22}")
        print()


def print_question_ranking(results):
    print("\n" + "=" * 100)
    print(f"QUESTION STRATIFICATION — same% dispersion + extremes (n>={MIN_PER_QUESTION} per Q)")
    print("=" * 100)
    for grader, by_type in results.items():
        for ptype in SENSITIVITY_TYPES:
            if ptype not in by_type:
                continue
            bq = by_type[ptype]["by_question"]
            eligible = [
                (qid, d["same"] / d["total"] * 100, d["total"])
                for qid, d in bq.items()
                if d["total"] >= MIN_PER_QUESTION
            ]
            if not eligible:
                continue
            eligible.sort(key=lambda x: x[1], reverse=True)
            vals = [x[1] for x in eligible]
            mean = sum(vals) / len(vals)
            std = (sum((v - mean) ** 2 for v in vals) / len(vals)) ** 0.5
            print(f"\n{grader} / {ptype}")
            print(
                f"  Questions eligible: {len(eligible)}/42  "
                f"same% mean={mean:.1f}  std={std:.1f}  "
                f"range=[{vals[-1]:.1f}, {vals[0]:.1f}]  "
                f"spread={vals[0] - vals[-1]:.1f}pp"
            )
            print("  Worst 5 (highest miss):")
            for qid, s, n in eligible[:5]:
                print(f"    {qid[:48]:<48}  same={s:5.1f}%  n={n}")
            print("  Best 5 (lowest miss):")
            for qid, s, n in eligible[-5:]:
                print(f"    {qid[:48]:<48}  same={s:5.1f}%  n={n}")


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

    all_results = {}

    for grader_name, cache_path in GRADERS.items():
        if not cache_path.exists():
            print(f"Skipping {grader_name}: cache not found")
            continue
        print(f"\n[{grader_name}] Loading cache...")
        cache = load_cache(cache_path)
        all_results[grader_name] = {}

        for ptype in SENSITIVITY_TYPES:
            print(f"  [{grader_name}] {ptype}: building pairs + bootstrap...")
            pairs = build_pairs(perturbations, cache, q_lookup, a_lookup, ptype)
            overall = pair_stats(pairs)
            cls_list = [p["cls"] for p in pairs]
            ci = bootstrap_ci(cls_list)
            bq = by_question(pairs)
            bl = by_length(pairs)
            bl_stats = {k: pair_stats(v) for k, v in bl.items()}

            all_results[grader_name][ptype] = {
                "n": overall["n"],
                "dec_pct": overall["dec_pct"],
                "same_pct": overall["same_pct"],
                "inc_pct": overall["inc_pct"],
                "ci_95": {
                    "dec": (ci["dec"][0] * 100, ci["dec"][1] * 100),
                    "same": (ci["same"][0] * 100, ci["same"][1] * 100),
                    "inc": (ci["inc"][0] * 100, ci["inc"][1] * 100),
                },
                "by_question": bq,
                "by_length": bl_stats,
            }

    print_bootstrap_table(all_results)
    print_length_table(all_results)
    print_question_ranking(all_results)

    out_dir = ROOT / "runs/analysis"
    out_dir.mkdir(exist_ok=True, parents=True)
    out = out_dir / "sensitivity_deep.json"
    with open(out, "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\nResults saved to: {out}")


if __name__ == "__main__":
    main()
