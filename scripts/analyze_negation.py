"""Analyze negation perturbation patterns across graders.

Produces a detailed breakdown of how each grader responds to negation insertion:
- Overall success/failure/paradox rates
- Breakdown by gold label and original score
- Concrete examples of failures (same score after negation)
"""

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_cache(path):
    cache = {}
    with open(path) as f:
        for line in f:
            entry = json.loads(line)
            key = (entry["question"], entry["student_answer"])
            cache[key] = entry
    return cache


def main():
    from asag.loaders.semeval2013 import SemEval2013Loader
    from asag.perturbations.engine import PerturbationEngine

    loader = SemEval2013Loader(corpus="beetle")
    questions, answers = loader.load()

    engine = PerturbationEngine()
    perturbations, _gate_log = engine.generate_all(answers, questions)

    neg_perts = [p for p in perturbations if p.type == "negation_insertion"]
    print(f"Negation perturbations generated: {len(neg_perts)}")

    q_lookup = {q.question_id: q for q in questions}
    a_lookup = {a.answer_id: a for a in answers}

    # --- Analyze each grader ---
    caches = {
        "GPT-5.4 mini L0": ROOT / "runs/llm_grade_caches/llm_openai_gpt-5.4-mini_level0.jsonl",
        "GPT-5.4 mini L1": ROOT / "runs/llm_grade_caches/llm_openai_gpt-5.4-mini_level1.jsonl",
    }

    for grader_name, cache_path in caches.items():
        if not cache_path.exists():
            print(f"\nSkipping {grader_name}: cache not found at {cache_path}")
            continue

        cache = load_cache(cache_path)
        print(f"\n{'='*60}")
        print(f"NEGATION ANALYSIS — {grader_name}")
        print(f"Cache entries: {len(cache)}")
        print(f"{'='*60}")

        decreased = 0
        no_change = 0
        increased = 0
        not_found = 0
        examples_no_change = []
        examples_increased = []
        by_gold = defaultdict(lambda: {"dec": 0, "same": 0, "inc": 0})
        by_orig_score = defaultdict(lambda: {"dec": 0, "same": 0, "inc": 0})

        # Collect all pairs for floor/ceiling analysis
        all_pairs = []

        for p in neg_perts:
            answer = a_lookup[p.answer_id]
            q = q_lookup[answer.question_id]

            orig_key = (q.prompt, answer.student_answer)
            pert_key = (q.prompt, p.text)

            if orig_key not in cache or pert_key not in cache:
                not_found += 1
                continue

            orig_score = cache[orig_key]["score"]
            pert_score = cache[pert_key]["score"]
            gold = answer.gold_label

            all_pairs.append({
                "orig_score": orig_score,
                "pert_score": pert_score,
                "gold": gold,
                "orig_text": answer.student_answer,
                "pert_text": p.text,
                "question": q.prompt,
            })

            if round(pert_score, 6) < round(orig_score, 6):
                decreased += 1
                by_gold[gold]["dec"] += 1
                by_orig_score[orig_score]["dec"] += 1
            elif round(pert_score, 6) == round(orig_score, 6):
                no_change += 1
                by_gold[gold]["same"] += 1
                by_orig_score[orig_score]["same"] += 1
                if len(examples_no_change) < 8:
                    examples_no_change.append({
                        "q": q.prompt[:120],
                        "orig": answer.student_answer,
                        "neg": p.text,
                        "gold": gold,
                        "orig_s": orig_score,
                        "pert_s": pert_score,
                    })
            else:
                increased += 1
                by_gold[gold]["inc"] += 1
                by_orig_score[orig_score]["inc"] += 1
                if len(examples_increased) < 5:
                    examples_increased.append({
                        "q": q.prompt[:120],
                        "orig": answer.student_answer,
                        "neg": p.text,
                        "gold": gold,
                        "orig_s": orig_score,
                        "pert_s": pert_score,
                    })

        total = decreased + no_change + increased
        print(f"Not found in cache: {not_found}")
        print(f"\nTotal matched pairs: {total}")
        print(f"Score DECREASED (correct):  {decreased} ({decreased/total*100:.1f}%)")
        print(f"Score UNCHANGED (failure):  {no_change} ({no_change/total*100:.1f}%)")
        print(f"Score INCREASED (paradox):  {increased} ({increased/total*100:.1f}%)")

        # Floor effect: answers already at 0.0 can't decrease
        floor_pairs = [p for p in all_pairs if p["orig_score"] == 0.0]
        non_floor = [p for p in all_pairs if p["orig_score"] > 0.0]
        print(f"\n--- Floor effect ---")
        print(f"Answers already at score 0.0: {len(floor_pairs)} ({len(floor_pairs)/total*100:.1f}%)")
        if non_floor:
            nf_dec = sum(1 for p in non_floor if round(p["pert_score"], 6) < round(p["orig_score"], 6))
            nf_same = sum(1 for p in non_floor if round(p["pert_score"], 6) == round(p["orig_score"], 6))
            nf_inc = sum(1 for p in non_floor if round(p["pert_score"], 6) > round(p["orig_score"], 6))
            nf_total = len(non_floor)
            print(f"Non-floor pairs: {nf_total}")
            print(f"  Decreased: {nf_dec} ({nf_dec/nf_total*100:.1f}%)")
            print(f"  Unchanged: {nf_same} ({nf_same/nf_total*100:.1f}%)")
            print(f"  Increased: {nf_inc} ({nf_inc/nf_total*100:.1f}%)")

        print(f"\n--- Breakdown by gold label ---")
        for label in sorted(by_gold.keys()):
            d = by_gold[label]
            t = d["dec"] + d["same"] + d["inc"]
            print(
                f"  {label:35s} | dec={d['dec']:4d} ({d['dec']/t*100:5.1f}%) "
                f"| same={d['same']:4d} ({d['same']/t*100:5.1f}%) "
                f"| inc={d['inc']:4d} ({d['inc']/t*100:5.1f}%) | n={t}"
            )

        print(f"\n--- Breakdown by original score ---")
        for score in sorted(by_orig_score.keys()):
            d = by_orig_score[score]
            t = d["dec"] + d["same"] + d["inc"]
            print(
                f"  orig={score:.1f} | dec={d['dec']:4d} ({d['dec']/t*100:5.1f}%) "
                f"| same={d['same']:4d} ({d['same']/t*100:5.1f}%) "
                f"| inc={d['inc']:4d} ({d['inc']/t*100:5.1f}%) | n={t}"
            )

        print(f"\n--- Examples: UNCHANGED after negation (non-floor) ---")
        non_floor_examples = [
            ex for ex in examples_no_change if ex["orig_s"] > 0.0
        ]
        for i, ex in enumerate(non_floor_examples[:6]):
            print(f"\n  Example {i+1} (gold={ex['gold']}, score={ex['orig_s']}→{ex['pert_s']})")
            print(f"  Q: {ex['q']}")
            print(f"  ORIG: {ex['orig']}")
            print(f"  NEG:  {ex['neg']}")

        print(f"\n--- Examples: INCREASED after negation ---")
        for i, ex in enumerate(examples_increased[:5]):
            print(f"\n  Example {i+1} (gold={ex['gold']}, score={ex['orig_s']}→{ex['pert_s']})")
            print(f"  Q: {ex['q']}")
            print(f"  ORIG: {ex['orig']}")
            print(f"  NEG:  {ex['neg']}")


if __name__ == "__main__":
    main()
