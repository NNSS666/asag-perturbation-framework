"""Extract deletion 'missed' cases for qualitative manual review.

Random sample (seeded) of N key_concept_deletion pairs where:
  - orig_score > 0 (non-floor)
  - pert_score == orig_score (grader missed the deletion)

Per grader (L0, L1). Output structured for easy reading + categorisation:
  - question
  - original answer
  - perturbed answer (with visible word-diff marker)
  - gold label
  - scores
  - deleted word (inferred from diff)

Output: runs/analysis/deletion_missed_cases.txt
"""

import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
N_CASES_PER_GRADER = 15  # total 30 cases
SEED = 42

GRADERS = {
    "L0": ROOT / "runs/llm_grade_caches/llm_openai_gpt-5.4-mini_level0.jsonl",
    "L1": ROOT / "runs/llm_grade_caches/llm_openai_gpt-5.4-mini_level1.jsonl",
}


def load_cache(path):
    cache = {}
    with open(path) as f:
        for line in f:
            e = json.loads(line)
            cache[(e["question"], e["student_answer"])] = e
    return cache


def find_deleted_word(orig_tokens, pert_tokens):
    """Infer which word was deleted by diffing orig vs pert."""
    i = j = 0
    while i < len(orig_tokens) and j < len(pert_tokens):
        if orig_tokens[i] == pert_tokens[j]:
            i += 1
            j += 1
        else:
            return orig_tokens[i]
    if i < len(orig_tokens):
        return orig_tokens[i]
    return "?"


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
    del_perts = [p for p in perturbations if p.type == "key_concept_deletion"]
    print(f"Deletion perturbations: {len(del_perts)}")

    lines = [f"# Random sample, seed={SEED}, N={N_CASES_PER_GRADER} per grader"]

    for grader_name, cache_path in GRADERS.items():
        cache = load_cache(cache_path)
        candidates = []
        for p in del_perts:
            a = a_lookup[p.answer_id]
            q = q_lookup[a.question_id]
            ok = (q.prompt, a.student_answer)
            pk = (q.prompt, p.text)
            if ok not in cache or pk not in cache:
                continue
            os_ = cache[ok]["score"]
            ps_ = cache[pk]["score"]
            if os_ == 0.0:
                continue
            if round(os_, 6) != round(ps_, 6):
                continue
            candidates.append((p, a, q, os_, ps_))

        rng = random.Random(SEED)
        k = min(N_CASES_PER_GRADER, len(candidates))
        selected = rng.sample(candidates, k)

        lines.append("")
        lines.append("=" * 90)
        lines.append(
            f"GRADER: {grader_name}   "
            f"(random sample {k} of {len(candidates)} missed deletion cases, seed={SEED})"
        )
        lines.append("=" * 90)

        for i, (p, a, q, os_, ps_) in enumerate(selected, 1):
            deleted = find_deleted_word(a.student_answer.split(), p.text.split())
            lines.append(f"\n[{i}] question_id={a.question_id}")
            lines.append(f"    gold={a.gold_label}  orig_score={os_}  pert_score={ps_}")
            lines.append(f"    Q:    {q.prompt[:160]}")
            lines.append(f"    ORIG: {a.student_answer}")
            lines.append(f"    PERT: {p.text}")
            lines.append(f"    DELETED WORD (inferred): '{deleted}'")
            lines.append("    CATEGORY: [_____________]  (fill in: article / domain_concept / verb / connective / other)")
            lines.append("    SEVERITY: [_____________]  (fill in: meaning_preserved / meaning_degraded / meaning_inverted)")

    out = ROOT / "runs/analysis/deletion_missed_cases.txt"
    out.parent.mkdir(exist_ok=True, parents=True)
    with open(out, "w") as f:
        f.write("\n".join(lines))

    print(f"\nSaved random sample (seed={SEED}, {N_CASES_PER_GRADER} per grader) to: {out}")
    print("\nReview instructions:")
    print("  1. Open runs/analysis/deletion_missed_cases.txt")
    print("  2. For each case, fill CATEGORY and SEVERITY")
    print("  3. Aggregate counts by hand or re-run the analyser on the annotated file")


if __name__ == "__main__":
    main()
