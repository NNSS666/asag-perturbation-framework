"""First real experimental run: HybridGrader on Beetle with real perturbations.

Generates perturbations via PerturbationEngine, then evaluates using
EvaluationEngine under both Protocol A (LOQO) and Protocol B (within-question).
Reports IVR/SSR/ASR metrics and robustness drop.
"""
import time
import sys

print("=" * 60)
print("FIRST REAL EXPERIMENTAL RUN")
print("HybridGrader on Beetle — Protocol A + B")
print("=" * 60)

# Step 1: Load data
print("\n[1/4] Loading Beetle corpus...")
t0 = time.time()
from asag.loaders import SemEval2013Loader
questions, answers = SemEval2013Loader("beetle").load()
print(f"  Loaded: {len(questions)} questions, {len(answers)} answers ({time.time()-t0:.1f}s)")

# Step 2: Generate perturbations
print("\n[2/4] Generating perturbations (7 types, ~10 per answer)...")
print("  This takes a few minutes (SBERT encoding for Gate 1)...")
t1 = time.time()
from asag.perturbations import PerturbationEngine
engine = PerturbationEngine(seed=42)
perturbations, gate_log = engine.generate_all(answers, questions)
t_pert = time.time() - t1
print(f"  Generated: {len(perturbations)} perturbations in {t_pert:.0f}s")
print(f"  Avg per answer: {len(perturbations)/len(answers):.1f}")

rates = gate_log.rejection_rates()
g1 = rates.get("gate1", {})
if g1:
    for t, r in g1.items():
        print(f"  Gate 1 rejection ({t}): {r:.1%}")

# Step 3: Run evaluation
print("\n[3/4] Running EvaluationEngine (Protocol A: 42-fold LOQO + Protocol B)...")
print("  Protocol A trains HybridGrader 42 times (one per fold)...")
print("  This will take several minutes...")
sys.stdout.flush()

t2 = time.time()
from asag.graders import HybridGrader
from asag.evaluation import EvaluationEngine

grader = HybridGrader()
eval_engine = EvaluationEngine(grader, corpus="beetle")
result = eval_engine.run(questions, answers, perturbations, protocols=["A", "B"])
t_eval = time.time() - t2

print(f"  Evaluation complete in {t_eval:.0f}s")

# Step 4: Report results
print("\n[4/4] RESULTS")
print("=" * 60)

print(f"\nGrader: {result.grader_name}")
print(f"Corpus: {result.corpus}")
print(f"Protocols: {result.protocols_run}")

print("\n--- PROTOCOL A (LOQO — cross-question generalization) ---")
for agg in result.protocol_a_aggregate:
    print(f"\n  Family: {agg.family} ({agg.n_pairs} pairs)")
    if agg.ivr_flip is not None:
        print(f"    IVR_flip:      {agg.ivr_flip:.3f}  (% of invariance pairs where score changed)")
    if agg.ivr_absdelta is not None:
        print(f"    IVR_absdelta:  {agg.ivr_absdelta:.3f}  (mean absolute score change)")
    if agg.ssr_directional is not None:
        print(f"    SSR_dir:       {agg.ssr_directional:.3f}  (% of sensitivity pairs where score decreased)")
    if agg.asr_thresholded is not None:
        print(f"    ASR_thresh:    {agg.asr_thresholded:.3f}  (% of gaming pairs that crossed pass threshold)")

print("\n--- PROTOCOL B (Within-question — in-distribution) ---")
for agg in result.protocol_b_aggregate:
    print(f"\n  Family: {agg.family} ({agg.n_pairs} pairs)")
    if agg.ivr_flip is not None:
        print(f"    IVR_flip:      {agg.ivr_flip:.3f}")
    if agg.ivr_absdelta is not None:
        print(f"    IVR_absdelta:  {agg.ivr_absdelta:.3f}")
    if agg.ssr_directional is not None:
        print(f"    SSR_dir:       {agg.ssr_directional:.3f}")
    if agg.asr_thresholded is not None:
        print(f"    ASR_thresh:    {agg.asr_thresholded:.3f}")

if result.robustness_drop:
    print("\n--- ROBUSTNESS DROP (Protocol A - Protocol B) ---")
    print("  Positive = worse under cross-question shift")
    print()
    print(f"  {'Family':<14} {'Metric':<16} {'Proto B':>8} {'Proto A':>8} {'Delta':>8}")
    print(f"  {'-'*14} {'-'*16} {'-'*8} {'-'*8} {'-'*8}")
    for row in result.robustness_drop:
        delta_str = f"{row['delta_a_minus_b']:+.3f}"
        print(f"  {row['perturbation_family']:<14} {row['metric_name']:<16} "
              f"{row['proto_b_value']:8.3f} {row['proto_a_value']:8.3f} {delta_str:>8}")

total_time = time.time() - t0
print(f"\n{'=' * 60}")
print(f"Total time: {total_time:.0f}s ({total_time/60:.1f} min)")
print(f"Results saved to: runs/")
print(f"{'=' * 60}")
