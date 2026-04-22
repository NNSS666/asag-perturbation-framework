"""Analyze sensitivity perturbation patterns across graders.

Generalises analyze_negation.py to all sensitivity perturbation types:
  - negation_insertion
  - key_concept_deletion
  - semantic_contradiction

For each grader x perturbation type, reports:
  - Overall dec/same/inc distribution
  - Floor-adjusted distribution (excluding orig_score = 0 pairs)
  - Breakdown by gold label
  - Breakdown by original score
  - Concrete example failures

Output:
  - stdout: human-readable report with a comparative summary table up top
  - runs/analysis/sensitivity_patterns.json: machine-readable dump
"""

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SENSITIVITY_TYPES = [
    "negation_insertion",
    "key_concept_deletion",
    "semantic_contradiction",
]

GRADERS = {
    "GPT-5.4 mini L0": ROOT / "runs/llm_grade_caches/llm_openai_gpt-5.4-mini_level0.jsonl",
    "GPT-5.4 mini L1": ROOT / "runs/llm_grade_caches/llm_openai_gpt-5.4-mini_level1.jsonl",
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


def analyze_pairs(perturbations, cache, q_lookup, a_lookup):
    pairs = []
    not_found = 0

    for p in perturbations:
        answer = a_lookup[p.answer_id]
        q = q_lookup[answer.question_id]
        orig_key = (q.prompt, answer.student_answer)
        pert_key = (q.prompt, p.text)
        if orig_key not in cache or pert_key not in cache:
            not_found += 1
            continue
        pairs.append({
            "orig_score": cache[orig_key]["score"],
            "pert_score": cache[pert_key]["score"],
            "gold": answer.gold_label,
            "orig_text": answer.student_answer,
            "pert_text": p.text,
            "question": q.prompt,
        })

    total = len(pairs)
    counts = {"dec": 0, "same": 0, "inc": 0}
    by_gold = defaultdict(lambda: {"dec": 0, "same": 0, "inc": 0})
    by_orig = defaultdict(lambda: {"dec": 0, "same": 0, "inc": 0})
    examples = {"unchanged_nonfloor": [], "increased": [], "decreased": []}

    non_floor_total = 0
    nf_counts = {"dec": 0, "same": 0, "inc": 0}

    for p in pairs:
        cls = classify(p["orig_score"], p["pert_score"])
        counts[cls] += 1
        by_gold[p["gold"]][cls] += 1
        by_orig[round(p["orig_score"], 6)][cls] += 1

        if p["orig_score"] > 0.0:
            non_floor_total += 1
            nf_counts[cls] += 1

        # Example collection: prioritise most interesting cases.
        bucket = None
        if cls == "dec":
            bucket = "decreased"
        elif cls == "same" and p["orig_score"] > 0.0:
            bucket = "unchanged_nonfloor"
        elif cls == "inc":
            bucket = "increased"
        if bucket and len(examples[bucket]) < 8:
            examples[bucket].append({
                "q": p["question"][:140],
                "orig": p["orig_text"],
                "pert": p["pert_text"],
                "gold": p["gold"],
                "orig_s": p["orig_score"],
                "pert_s": p["pert_score"],
            })

    return {
        "total": total,
        "not_found": not_found,
        "counts": counts,
        "non_floor_total": non_floor_total,
        "non_floor_counts": nf_counts,
        "by_gold": {k: dict(v) for k, v in by_gold.items()},
        "by_orig_score": {str(k): dict(v) for k, v in by_orig.items()},
        "examples": examples,
    }


def pct(num, den):
    return f"{num/den*100:5.1f}%" if den else "   --"


def print_summary_table(results):
    print("\n" + "=" * 82)
    print("SUMMARY — Sensitivity response distribution (dec = correct, same = missed, inc = flipped)")
    print("=" * 82)
    print(f"{'Grader':<18} {'Perturbation':<26} {'Dec':>8} {'Same':>8} {'Inc':>8} {'N':>8}")
    print("-" * 82)
    for grader_name, by_type in results.items():
        for ptype in SENSITIVITY_TYPES:
            if ptype not in by_type:
                continue
            r = by_type[ptype]
            t = r["total"]
            c = r["counts"]
            print(
                f"{grader_name:<18} {ptype:<26} "
                f"{pct(c['dec'], t):>8} "
                f"{pct(c['same'], t):>8} "
                f"{pct(c['inc'], t):>8} "
                f"{t:>8}"
            )
        print()


def print_nonfloor_table(results):
    print("\n" + "=" * 82)
    print("FLOOR-ADJUSTED — Distribution restricted to pairs with orig_score > 0")
    print("=" * 82)
    print(f"{'Grader':<18} {'Perturbation':<26} {'Dec':>8} {'Same':>8} {'Inc':>8} {'N_nf':>8}")
    print("-" * 82)
    for grader_name, by_type in results.items():
        for ptype in SENSITIVITY_TYPES:
            if ptype not in by_type:
                continue
            r = by_type[ptype]
            nf = r["non_floor_total"]
            c = r["non_floor_counts"]
            print(
                f"{grader_name:<18} {ptype:<26} "
                f"{pct(c['dec'], nf):>8} "
                f"{pct(c['same'], nf):>8} "
                f"{pct(c['inc'], nf):>8} "
                f"{nf:>8}"
            )
        print()


def print_detailed_report(grader_name, by_type):
    print("\n" + "=" * 82)
    print(f"DETAILED — {grader_name}")
    print("=" * 82)
    for ptype in SENSITIVITY_TYPES:
        if ptype not in by_type:
            continue
        r = by_type[ptype]
        t = r["total"]
        nf = r["non_floor_total"]
        c = r["counts"]
        nfc = r["non_floor_counts"]
        print(f"\n--- {ptype} ---")
        print(f"Matched pairs: {t} (not found: {r['not_found']})")
        print(f"Overall    : dec={pct(c['dec'], t)}  same={pct(c['same'], t)}  inc={pct(c['inc'], t)}")
        print(f"Non-floor  : dec={pct(nfc['dec'], nf)}  same={pct(nfc['same'], nf)}  inc={pct(nfc['inc'], nf)}  (n_nf={nf})")

        print("\nBy gold label:")
        for gold in sorted(r["by_gold"].keys()):
            gc = r["by_gold"][gold]
            tt = gc["dec"] + gc["same"] + gc["inc"]
            print(
                f"  {gold:<28} n={tt:>4}  "
                f"dec={pct(gc['dec'], tt)}  same={pct(gc['same'], tt)}  inc={pct(gc['inc'], tt)}"
            )

        print("\nBy original score:")
        for s in sorted(r["by_orig_score"].keys(), key=float):
            sc = r["by_orig_score"][s]
            tt = sc["dec"] + sc["same"] + sc["inc"]
            print(
                f"  orig={s:<5} n={tt:>4}  "
                f"dec={pct(sc['dec'], tt)}  same={pct(sc['same'], tt)}  inc={pct(sc['inc'], tt)}"
            )

        if r["examples"]["unchanged_nonfloor"]:
            print("\nExample failures (same score, orig>0):")
            for i, ex in enumerate(r["examples"]["unchanged_nonfloor"][:3], 1):
                print(f"  [{i}] gold={ex['gold']}  {ex['orig_s']} -> {ex['pert_s']}")
                print(f"      Q:    {ex['q']}")
                print(f"      ORIG: {ex['orig']}")
                print(f"      PERT: {ex['pert']}")


def main():
    from asag.loaders.semeval2013 import SemEval2013Loader
    from asag.perturbations.engine import PerturbationEngine

    print("Loading dataset and generating perturbations...")
    loader = SemEval2013Loader(corpus="beetle")
    questions, answers = loader.load()

    engine = PerturbationEngine()
    perturbations, _gate_log = engine.generate_all(answers, questions)

    q_lookup = {q.question_id: q for q in questions}
    a_lookup = {a.answer_id: a for a in answers}

    perts_by_type = defaultdict(list)
    for p in perturbations:
        perts_by_type[p.type].append(p)

    print("Sensitivity perturbations generated:")
    for ptype in SENSITIVITY_TYPES:
        print(f"  {ptype:<26} {len(perts_by_type[ptype]):>6}")

    results = {}
    for grader_name, cache_path in GRADERS.items():
        if not cache_path.exists():
            print(f"\nSkipping {grader_name}: cache not found at {cache_path}")
            continue
        print(f"\nLoading cache for {grader_name}...")
        cache = load_cache(cache_path)
        print(f"  cache entries: {len(cache)}")

        by_type = {}
        for ptype in SENSITIVITY_TYPES:
            perts = perts_by_type[ptype]
            if not perts:
                continue
            by_type[ptype] = analyze_pairs(perts, cache, q_lookup, a_lookup)
        results[grader_name] = by_type

    print_summary_table(results)
    print_nonfloor_table(results)
    for grader_name, by_type in results.items():
        print_detailed_report(grader_name, by_type)

    out_dir = ROOT / "runs/analysis"
    out_dir.mkdir(exist_ok=True, parents=True)
    out_path = out_dir / "sensitivity_patterns.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n\nResults saved to: {out_path}")


if __name__ == "__main__":
    main()
