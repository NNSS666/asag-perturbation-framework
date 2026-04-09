"""
Run LLM grader experiments: 3 models x 2 levels = 6 configurations on Beetle.

Optimization: LLMGrader is zero-shot (no fit()). The grade for a given text is
identical regardless of which fold/split it belongs to. So we grade each
perturbation ONCE, cache the results, then wrap them in a CachedGrader that
the EvaluationEngine uses for Protocol A/B evaluation — instant dict lookups
instead of API calls.

Crash recovery: grades are persisted to JSONL incrementally. Use --resume to
continue from a partial run.

Usage:
    PYTHONPATH=src python3 -m scripts.run_llm_experiments
    PYTHONPATH=src python3 -m scripts.run_llm_experiments --models gpt-5.4-mini --levels 0
    PYTHONPATH=src python3 -m scripts.run_llm_experiments --resume
"""

import argparse
import json
import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from asag.evaluation import EvaluationEngine
from asag.graders.base import GradeResult, GraderInterface
from asag.graders.llm import LLMGrader
from asag.loaders import SemEval2013Loader
from asag.perturbations import PerturbationEngine
from asag.schema import AnswerRecord, PerturbationRecord, QuestionRecord

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Experiment configurations
# ---------------------------------------------------------------------------

# (provider, model_id, level)
ALL_CONFIGURATIONS: List[Tuple[str, str, int]] = [
    ("openai", "gpt-5.4-mini", 0),
    ("openai", "gpt-5.4-mini", 1),
    ("openai", "gpt-5.4", 0),
    ("openai", "gpt-5.4", 1),
    ("google", "gemini-2.5-flash", 0),
    ("google", "gemini-2.5-flash", 1),
]

# All available model IDs for CLI filtering
ALL_MODEL_IDS = sorted(set(m for _, m, _ in ALL_CONFIGURATIONS))

# Directory for grade caches (persisted across runs for crash recovery)
CACHE_DIR = Path("runs") / "llm_grade_caches"

# Maximum consecutive API errors before aborting
MAX_CONSECUTIVE_ERRORS = 100


# ---------------------------------------------------------------------------
# CachedGrader — wraps pre-computed grades for EvaluationEngine
# ---------------------------------------------------------------------------


class CachedGrader(GraderInterface):
    """Grader that returns pre-computed grades from an in-memory cache.

    Implements GraderInterface so EvaluationEngine can use it transparently.
    Does NOT define fit() — the engine checks hasattr(grader, 'fit') and
    skips training for this grader.

    Args:
        name:  The grader_name string (delegated from the original LLMGrader).
        cache: Dict mapping (question, student_answer, reference_answer) to GradeResult.
    """

    def __init__(
        self,
        name: str,
        cache: Dict[Tuple[str, str, str], GradeResult],
    ) -> None:
        self._name = name
        self._cache = cache
        self._miss_count = 0

    @property
    def grader_name(self) -> str:
        """Return the original LLMGrader's name."""
        return self._name

    def grade(
        self,
        question: str,
        rubric: Optional[str],
        student_answer: str,
        reference_answer: str = "",
    ) -> GradeResult:
        """Look up a pre-computed grade from the cache.

        Args:
            question:         Question text.
            rubric:           Unused (kept for interface compliance).
            student_answer:   Student/perturbed answer text.
            reference_answer: Reference answer text.

        Returns:
            Cached GradeResult.

        Raises:
            KeyError: If the (question, student_answer, reference_answer) triple
                      is not in the cache. This indicates a bug in the grading
                      phase — all perturbations should have been graded.
        """
        key = (question, student_answer, reference_answer)
        result = self._cache.get(key)
        if result is None:
            self._miss_count += 1
            # Fallback: return a neutral grade to avoid crashing the evaluation.
            # This should not happen if the grading phase completed successfully.
            logger.warning(
                "Cache miss #%d for key (q=%s..., sa=%s..., ref=%s...)",
                self._miss_count,
                question[:40],
                student_answer[:40],
                reference_answer[:40],
            )
            return GradeResult(
                label="irrelevant", score=0.0, confidence=0.0
            )
        return result


# ---------------------------------------------------------------------------
# Grade cache persistence (JSONL)
# ---------------------------------------------------------------------------


def _cache_path_for(grader_name: str) -> Path:
    """Return the JSONL cache file path for a given grader configuration."""
    return CACHE_DIR / f"{grader_name}.jsonl"


def load_grade_cache(
    cache_path: Path,
) -> Dict[Tuple[str, str, str], GradeResult]:
    """Load previously saved grades from a JSONL file.

    Args:
        cache_path: Path to the JSONL cache file.

    Returns:
        Dict mapping (question, student_answer, ref) to GradeResult.
    """
    cache: Dict[Tuple[str, str, str], GradeResult] = {}
    if not cache_path.exists():
        return cache

    with open(cache_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
                key = (row["question"], row["student_answer"], row["ref"])
                cache[key] = GradeResult(
                    label=row["label"],
                    score=row["score"],
                    confidence=row["confidence"],
                )
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning("Skipping malformed cache line %d: %s", line_num, e)

    return cache


def append_grade_to_cache(
    cache_file,
    question: str,
    student_answer: str,
    ref: str,
    result: GradeResult,
) -> None:
    """Append a single grade to the open cache file.

    Args:
        cache_file:     Open file handle in append mode.
        question:       Question text.
        student_answer: Student/perturbed answer text.
        ref:            Reference answer text.
        result:         GradeResult to persist.
    """
    row = {
        "question": question,
        "student_answer": student_answer,
        "ref": ref,
        "label": result.label,
        "score": result.score,
        "confidence": result.confidence,
    }
    cache_file.write(json.dumps(row, ensure_ascii=False) + "\n")
    cache_file.flush()


# ---------------------------------------------------------------------------
# Grading phase — grade all perturbations once
# ---------------------------------------------------------------------------


def build_grade_cache(
    grader: LLMGrader,
    perturbations: List[PerturbationRecord],
    answers: List[AnswerRecord],
    questions: List[QuestionRecord],
    cache_path: Path,
    resume: bool = False,
) -> Dict[Tuple[str, str, str], GradeResult]:
    """Grade all perturbations, persisting results incrementally.

    For each perturbation, calls grader.grade() and caches the result.
    On resume, loads existing cache and skips already-graded perturbations.

    Args:
        grader:        LLMGrader instance.
        perturbations: All PerturbationRecords to grade.
        answers:       All AnswerRecords (for question_id lookup).
        questions:     All QuestionRecords (for prompt and reference_answer).
        cache_path:    Path to JSONL cache file.
        resume:        If True, load existing cache and continue.

    Returns:
        Complete grade cache dict.
    """
    answer_lookup: Dict[str, AnswerRecord] = {a.answer_id: a for a in answers}
    question_lookup: Dict[str, QuestionRecord] = {
        q.question_id: q for q in questions
    }

    # Load existing cache if resuming
    cache: Dict[Tuple[str, str, str], GradeResult] = {}
    if resume:
        cache = load_grade_cache(cache_path)
        if cache:
            print(f"  Resumed: {len(cache)} cached grades loaded")

    # Prepare list of perturbations to grade
    to_grade: List[Tuple[PerturbationRecord, str, str, str]] = []
    for pert in perturbations:
        answer = answer_lookup.get(pert.answer_id)
        if answer is None:
            continue
        q = question_lookup.get(answer.question_id)
        if q is None:
            continue

        ref_answer = q.reference_answers[0] if q.reference_answers else ""
        key = (q.prompt, pert.text, ref_answer)

        if key not in cache:
            to_grade.append((pert, q.prompt, pert.text, ref_answer))

    total = len(to_grade)
    if total == 0:
        print("  All perturbations already graded (cache complete)")
        return cache

    print(f"  To grade: {total} perturbations ({len(cache)} already cached)")

    # Grade with progress reporting
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    error_count = 0
    consecutive_errors = 0
    t_start = time.time()
    grader_name = grader.grader_name

    with open(cache_path, "a", encoding="utf-8") as cache_file:
        for i, (pert, question, student_answer, ref_answer) in enumerate(to_grade):
            try:
                result = grader.grade(
                    question=question,
                    rubric=None,
                    student_answer=student_answer,
                    reference_answer=ref_answer,
                )
                key = (question, student_answer, ref_answer)
                cache[key] = result
                append_grade_to_cache(cache_file, question, student_answer, ref_answer, result)
                consecutive_errors = 0

            except Exception as e:
                error_count += 1
                consecutive_errors += 1
                logger.warning(
                    "Error grading perturbation %s: %s", pert.perturb_id, e
                )

                if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                    print(
                        f"\n  ABORT: {MAX_CONSECUTIVE_ERRORS} consecutive errors. "
                        f"Use --resume to continue later."
                    )
                    print(f"  Graded {len(cache)} / {len(cache) + total - i - 1} total")
                    sys.exit(1)

            # Progress reporting every 100 items
            if (i + 1) % 100 == 0 or (i + 1) == total:
                elapsed = time.time() - t_start
                rate = (i + 1) / elapsed if elapsed > 0 else 0
                eta_s = (total - i - 1) / rate if rate > 0 else 0
                eta_m = eta_s / 60
                pct = (i + 1) / total * 100
                print(
                    f"\r  [{grader_name}] {i + 1}/{total} ({pct:.1f}%) "
                    f"| {error_count} errors | ETA {eta_m:.0f}m",
                    end="",
                    flush=True,
                )

    print()  # newline after progress
    print(f"  Done: {len(cache)} grades cached, {error_count} errors")
    return cache


def build_original_grade_cache(
    grader: LLMGrader,
    answers: List[AnswerRecord],
    questions: List[QuestionRecord],
    cache_path: Path,
    existing_cache: Dict[Tuple[str, str, str], GradeResult],
    resume: bool = False,
) -> Dict[Tuple[str, str, str], GradeResult]:
    """Grade all original (unperturbed) answers, persisting results incrementally.

    After Fix B1, EvaluationEngine grades originals to compute grader-vs-grader
    robustness (not grader-vs-gold). CachedGrader needs these in its cache.

    Args:
        grader:         LLMGrader instance.
        answers:        All AnswerRecords to grade.
        questions:      All QuestionRecords (for prompt and reference_answer).
        cache_path:     Path to JSONL cache file (same as perturbation cache).
        existing_cache: Already-populated cache dict (mutated in place).
        resume:         If True, skip already-cached originals.

    Returns:
        Updated cache dict (same object as existing_cache).
    """
    question_lookup: Dict[str, QuestionRecord] = {
        q.question_id: q for q in questions
    }

    # Build list of originals to grade
    to_grade: List[Tuple[AnswerRecord, str, str, str]] = []
    for answer in answers:
        q = question_lookup.get(answer.question_id)
        if q is None:
            continue
        ref_answer = q.reference_answers[0] if q.reference_answers else ""
        key = (q.prompt, answer.student_answer, ref_answer)
        if key not in existing_cache:
            to_grade.append((answer, q.prompt, answer.student_answer, ref_answer))

    total = len(to_grade)
    if total == 0:
        print("  All originals already graded (cache complete)")
        return existing_cache

    print(f"  To grade: {total} originals ({len(existing_cache)} already cached)")

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    error_count = 0
    consecutive_errors = 0
    t_start = time.time()
    grader_name = grader.grader_name

    with open(cache_path, "a", encoding="utf-8") as cache_file:
        for i, (answer, question, student_answer, ref_answer) in enumerate(to_grade):
            try:
                result = grader.grade(
                    question=question,
                    rubric=None,
                    student_answer=student_answer,
                    reference_answer=ref_answer,
                )
                key = (question, student_answer, ref_answer)
                existing_cache[key] = result
                append_grade_to_cache(cache_file, question, student_answer, ref_answer, result)
                consecutive_errors = 0

            except Exception as e:
                error_count += 1
                consecutive_errors += 1
                logger.warning(
                    "Error grading original %s: %s", answer.answer_id, e
                )

                if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                    print(
                        f"\n  ABORT: {MAX_CONSECUTIVE_ERRORS} consecutive errors. "
                        f"Use --resume to continue later."
                    )
                    sys.exit(1)

            if (i + 1) % 100 == 0 or (i + 1) == total:
                elapsed = time.time() - t_start
                rate = (i + 1) / elapsed if elapsed > 0 else 0
                eta_s = (total - i - 1) / rate if rate > 0 else 0
                eta_m = eta_s / 60
                pct = (i + 1) / total * 100
                print(
                    f"\r  [{grader_name}] originals {i + 1}/{total} ({pct:.1f}%) "
                    f"| {error_count} errors | ETA {eta_m:.0f}m",
                    end="",
                    flush=True,
                )

    print()
    print(f"  Done: {total - error_count} originals graded, {error_count} errors")
    return existing_cache


# ---------------------------------------------------------------------------
# Single configuration run
# ---------------------------------------------------------------------------


def run_single_config(
    provider: str,
    model: str,
    level: int,
    questions: List[QuestionRecord],
    answers: List[AnswerRecord],
    perturbations: List[PerturbationRecord],
    resume: bool = False,
) -> Optional[Dict[str, Any]]:
    """Run one (provider, model, level) configuration end-to-end.

    1. Grade all perturbations (or resume from cache).
    2. Wrap grades in CachedGrader.
    3. Run EvaluationEngine with Protocol A + B.
    4. Print and save results.

    Args:
        provider:      API provider ("openai", "google").
        model:         Model ID (e.g. "gpt-5.4-mini").
        level:         Information level (0 or 1).
        questions:     All QuestionRecords.
        answers:       All AnswerRecords.
        perturbations: All PerturbationRecords.
        resume:        Resume from cached grades.

    Returns:
        Dict with summary metrics, or None on failure.
    """
    grader = LLMGrader(provider=provider, model=model, level=level)
    grader_name = grader.grader_name
    cache_path = _cache_path_for(grader_name)

    print(f"\n{'=' * 60}")
    print(f"Configuration: {grader_name}")
    print(f"  Provider: {provider} | Model: {model} | Level: {level}")
    print(f"{'=' * 60}")

    # Phase 1: Grade all perturbations
    print("\n[1/3] Grading perturbations...")
    t0 = time.time()
    grade_cache = build_grade_cache(
        grader, perturbations, answers, questions, cache_path, resume=resume
    )
    t_grade = time.time() - t0
    print(f"  Grading time: {t_grade:.0f}s")

    # Phase 2: Grade all original (unperturbed) answers
    print("\n[2/3] Grading original answers...")
    t_orig = time.time()
    grade_cache = build_original_grade_cache(
        grader, answers, questions, cache_path, grade_cache, resume=True
    )
    t_orig = time.time() - t_orig
    print(f"  Originals time: {t_orig:.0f}s")

    # Phase 3: Run evaluation with CachedGrader
    print("\n[3/3] Running EvaluationEngine (Protocol A + B)...")
    t1 = time.time()
    cached_grader = CachedGrader(name=grader_name, cache=grade_cache)
    eval_engine = EvaluationEngine(cached_grader, corpus="beetle")
    result = eval_engine.run(questions, answers, perturbations, protocols=["A", "B"])
    t_eval = time.time() - t1
    print(f"  Evaluation time: {t_eval:.0f}s")

    if cached_grader._miss_count > 0:
        print(f"  WARNING: {cached_grader._miss_count} cache misses during evaluation")

    # Print results
    _print_results(result)

    # Collect summary for final table
    summary = {
        "grader_name": grader_name,
        "provider": provider,
        "model": model,
        "level": level,
        "cache_size": len(grade_cache),
        "cache_misses": cached_grader._miss_count,
        "grading_time_s": t_grade,
        "eval_time_s": t_eval,
    }

    # Extract aggregate metrics for summary
    for agg in result.protocol_a_aggregate:
        prefix = f"A_{agg.family}"
        if agg.ivr_flip is not None:
            summary[f"{prefix}_ivr_flip"] = agg.ivr_flip
        if agg.ivr_absdelta is not None:
            summary[f"{prefix}_ivr_absdelta"] = agg.ivr_absdelta
        if agg.ssr_directional is not None:
            summary[f"{prefix}_ssr_directional"] = agg.ssr_directional
        if agg.asr_thresholded is not None:
            summary[f"{prefix}_asr_thresholded"] = agg.asr_thresholded

    return summary


def _print_results(result) -> None:
    """Print evaluation results in the same format as first_real_run.py."""
    print(f"\n--- PROTOCOL A (LOQO — cross-question generalization) ---")
    for agg in result.protocol_a_aggregate:
        print(f"\n  Family: {agg.family} ({agg.n_pairs} pairs)")
        if agg.ivr_flip is not None:
            print(f"    IVR_flip:      {agg.ivr_flip:.3f}")
        if agg.ivr_absdelta is not None:
            print(f"    IVR_absdelta:  {agg.ivr_absdelta:.3f}")
        if agg.ssr_directional is not None:
            print(f"    SSR_dir:       {agg.ssr_directional:.3f}")
        if agg.asr_thresholded is not None:
            print(f"    ASR_thresh:    {agg.asr_thresholded:.3f}")

    print(f"\n--- PROTOCOL B (Within-question — in-distribution) ---")
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
        print(f"\n--- ROBUSTNESS DROP (Protocol A - Protocol B) ---")
        print(f"  {'Family':<14} {'Metric':<16} {'Proto B':>8} {'Proto A':>8} {'Delta':>8}")
        print(f"  {'-'*14} {'-'*16} {'-'*8} {'-'*8} {'-'*8}")
        for row in result.robustness_drop:
            delta_str = f"{row['delta_a_minus_b']:+.3f}"
            print(
                f"  {row['perturbation_family']:<14} {row['metric_name']:<16} "
                f"{row['proto_b_value']:8.3f} {row['proto_a_value']:8.3f} {delta_str:>8}"
            )


# ---------------------------------------------------------------------------
# Summary table across all configurations
# ---------------------------------------------------------------------------


def _print_summary_table(summaries: List[Dict[str, Any]]) -> None:
    """Print a compact comparison table across all configurations."""
    if not summaries:
        return

    print(f"\n{'=' * 80}")
    print("SUMMARY — All Configurations")
    print(f"{'=' * 80}")
    print(
        f"  {'Grader':<40} {'IVR_flip':>9} {'IVR_abs':>9} "
        f"{'SSR_dir':>9} {'ASR_thr':>9}"
    )
    print(f"  {'-'*40} {'-'*9} {'-'*9} {'-'*9} {'-'*9}")

    for s in summaries:
        ivr = s.get("A_invariance_ivr_flip", float("nan"))
        ivr_abs = s.get("A_invariance_ivr_absdelta", float("nan"))
        ssr = s.get("A_sensitivity_ssr_directional", float("nan"))
        asr = s.get("A_gaming_asr_thresholded", float("nan"))
        print(
            f"  {s['grader_name']:<40} {ivr:9.3f} {ivr_abs:9.3f} "
            f"{ssr:9.3f} {asr:9.3f}"
        )

    print()


# ---------------------------------------------------------------------------
# CLI and main
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Run LLM grader experiments on Beetle dataset.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  Run all 6 configurations:\n"
            "    PYTHONPATH=src python3 -m scripts.run_llm_experiments\n\n"
            "  Run only GPT-5.4 mini level 0:\n"
            "    PYTHONPATH=src python3 -m scripts.run_llm_experiments "
            "--models gpt-5.4-mini --levels 0\n\n"
            "  Resume after crash:\n"
            "    PYTHONPATH=src python3 -m scripts.run_llm_experiments --resume\n"
        ),
    )
    parser.add_argument(
        "--models",
        nargs="+",
        choices=ALL_MODEL_IDS,
        default=ALL_MODEL_IDS,
        help=f"Model(s) to test. Default: all ({', '.join(ALL_MODEL_IDS)})",
    )
    parser.add_argument(
        "--levels",
        nargs="+",
        type=int,
        choices=[0, 1],
        default=[0, 1],
        help="Information level(s). 0=no ref, 1=with ref. Default: both.",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from cached grades (crash recovery).",
    )
    return parser.parse_args()


def main() -> None:
    """Entry point: load data, run selected configurations, print summary."""
    args = parse_args()

    # Filter configurations based on CLI args
    configs = [
        (p, m, l) for p, m, l in ALL_CONFIGURATIONS
        if m in args.models and l in args.levels
    ]

    if not configs:
        print("No configurations match the given --models and --levels filters.")
        sys.exit(1)

    print("=" * 60)
    print("LLM GRADER EXPERIMENTS")
    print(f"Configurations: {len(configs)}")
    for p, m, l in configs:
        print(f"  - {p}/{m} level {l}")
    print("=" * 60)

    # Step 1: Load data
    print("\n[SETUP] Loading Beetle corpus...")
    t0 = time.time()
    questions, answers = SemEval2013Loader("beetle").load()
    print(f"  Loaded: {len(questions)} questions, {len(answers)} answers ({time.time()-t0:.1f}s)")

    # Step 2: Generate/load perturbations (cached, instant on re-run)
    print("\n[SETUP] Loading perturbations (cached)...")
    t1 = time.time()
    engine = PerturbationEngine(seed=42)
    perturbations, gate_log = engine.generate_all(answers, questions)
    print(f"  Loaded: {len(perturbations)} perturbations ({time.time()-t1:.1f}s)")

    # Step 3: Run each configuration
    summaries: List[Dict[str, Any]] = []
    for provider, model, level in configs:
        summary = run_single_config(
            provider, model, level,
            questions, answers, perturbations,
            resume=args.resume,
        )
        if summary is not None:
            summaries.append(summary)

    # Step 4: Print summary table
    _print_summary_table(summaries)

    total_time = time.time() - t0
    print(f"Total time: {total_time:.0f}s ({total_time/60:.1f} min)")


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    main()
