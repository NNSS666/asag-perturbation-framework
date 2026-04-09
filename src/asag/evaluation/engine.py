"""
EvaluationEngine — orchestrates grader + evaluation protocols + metric calculation.

This is the capstone of Phase 2. It runs the full evaluation loop:
  1. Splits data using Protocol A (LOQO) and/or Protocol B (within-question).
  2. Fits the grader on training data per fold/question.
  3. Filters perturbations to test-set answer_ids only (no leakage).
  4. Grades each perturbed answer.
  5. Computes MetricResults per fold/question per perturbation family.
  6. Aggregates across folds/questions.
  7. Computes robustness drop comparison (Protocol A vs B delta).
  8. Persists EvaluationResult to disk via save_json.

Design decisions:
  - Perturbation filtering to test-set answer_ids prevents training-set leakage
    (RESEARCH.md Pitfall 3).
  - None aggregation: values that are None (from empty pairs) are excluded from
    averaging. If all values are None, aggregate is None.
  - reference_answer is passed as kwarg to grader.grade(); graders that don't
    accept it (LLM graders) are handled via TypeError catch-and-retry.
  - Score rounding to 6 decimals before float comparison prevents IEEE 754 issues
    (RESEARCH.md Pitfall 1).

Python 3.9 compatible: uses typing.Dict, List, Optional, Tuple.
"""

from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, ConfigDict

from asag.graders.base import GraderInterface, GradeResult
from asag.infra.storage import save_json
from asag.metrics import MetricCalculator, MetricResult
from asag.schema import AnswerRecord, PerturbationRecord, QuestionRecord
from asag.splitters import protocol_a_splits, protocol_b_splits


# ---------------------------------------------------------------------------
# Result models
# ---------------------------------------------------------------------------


class EvaluationResult(BaseModel):
    """Full evaluation output for one (grader, corpus) combination.

    Captures per-fold, per-question, aggregate, and robustness drop results.
    All fields are immutable after construction (frozen=True).

    Fields:
        grader_name:          Identifier of the grader used.
        corpus:               Dataset corpus identifier, e.g. "beetle".
        protocols_run:        Which protocols were executed: ["A"], ["B"], or ["A", "B"].
        protocol_a_results:   One MetricResult per (fold, family) if Protocol A was run.
        protocol_b_results:   One MetricResult per (question, family) if Protocol B was run.
        protocol_a_aggregate: Aggregated MetricResult per family across all folds.
        protocol_b_aggregate: Aggregated MetricResult per family across all questions.
        robustness_drop:      Delta rows (proto_a_value - proto_b_value) per metric per family.
    """

    model_config = ConfigDict(frozen=True)

    grader_name: str
    corpus: str
    protocols_run: List[str]
    protocol_a_results: List[MetricResult] = []
    protocol_b_results: List[MetricResult] = []
    protocol_a_aggregate: List[MetricResult] = []
    protocol_b_aggregate: List[MetricResult] = []
    robustness_drop: List[Dict[str, Any]] = []


# ---------------------------------------------------------------------------
# EvaluationEngine
# ---------------------------------------------------------------------------


class EvaluationEngine:
    """Orchestrates the full ASAG robustness evaluation loop.

    Given a grader, a corpus name, and the three data objects (questions, answers,
    perturbations), EvaluationEngine runs the evaluation under the requested
    protocol(s) and returns an EvaluationResult.

    Usage:
        grader = HybridGrader()
        engine = EvaluationEngine(grader, corpus="beetle")
        result = engine.run(questions, answers, perturbations, protocols=["A", "B"])
    """

    def __init__(self, grader: GraderInterface, corpus: str) -> None:
        """Initialise the engine with a grader and corpus identifier.

        Args:
            grader: Any GraderInterface implementation (HybridGrader, LLM grader, …).
            corpus: Corpus name used in result metadata, e.g. "beetle".
        """
        self._grader = grader
        self._corpus = corpus
        self._calc = MetricCalculator()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(
        self,
        questions: List[QuestionRecord],
        answers: List[AnswerRecord],
        perturbations: List[PerturbationRecord],
        protocols: Optional[List[str]] = None,
        run_dir: Optional[Path] = None,
    ) -> EvaluationResult:
        """Run the full evaluation loop and persist results to disk.

        Args:
            questions:     All QuestionRecords for the corpus subset.
            answers:       All AnswerRecords for the corpus subset.
            perturbations: All PerturbationRecords to evaluate.
            protocols:     Which protocols to run. Default ["A", "B"].
            run_dir:       Directory to write evaluation_result.json. If None,
                           auto-generated under runs/ with timestamp.

        Returns:
            EvaluationResult with per-fold, per-question, aggregate, and
            robustness drop results.
        """
        if protocols is None:
            protocols = ["A", "B"]

        # Build fast lookups
        question_lookup: Dict[str, QuestionRecord] = {
            q.question_id: q for q in questions
        }
        answer_lookup: Dict[str, AnswerRecord] = {
            a.answer_id: a for a in answers
        }

        # Group perturbations by answer_id for O(1) lookup
        perturbations_by_answer: Dict[str, List[PerturbationRecord]] = defaultdict(list)
        for p in perturbations:
            perturbations_by_answer[p.answer_id].append(p)

        protocols_run: List[str] = []
        proto_a_results: List[MetricResult] = []
        proto_a_agg: List[MetricResult] = []
        proto_b_results: List[MetricResult] = []
        proto_b_agg: List[MetricResult] = []
        robustness_drop: List[Dict[str, Any]] = []

        if "A" in protocols:
            proto_a_results, proto_a_agg = self._run_protocol_a(
                questions, answers, perturbations_by_answer, question_lookup, answer_lookup
            )
            protocols_run.append("A")

        if "B" in protocols:
            proto_b_results, proto_b_agg = self._run_protocol_b(
                questions, answers, perturbations_by_answer, question_lookup, answer_lookup
            )
            protocols_run.append("B")

        if "A" in protocols_run and "B" in protocols_run:
            robustness_drop = self._compute_robustness_drop(proto_a_agg, proto_b_agg)

        result = EvaluationResult(
            grader_name=self._grader.grader_name,
            corpus=self._corpus,
            protocols_run=protocols_run,
            protocol_a_results=proto_a_results,
            protocol_b_results=proto_b_results,
            protocol_a_aggregate=proto_a_agg,
            protocol_b_aggregate=proto_b_agg,
            robustness_drop=robustness_drop,
        )

        # Persist to disk
        if run_dir is None:
            run_dir = Path("runs") / (
                f"{self._corpus}_{self._grader.grader_name}_"
                f"{datetime.now().strftime('%Y%m%dT%H%M%S')}"
            )
        save_json(result.model_dump(), Path(run_dir) / "evaluation_result.json")

        return result

    # ------------------------------------------------------------------
    # Protocol A: LOQO
    # ------------------------------------------------------------------

    def _run_protocol_a(
        self,
        questions: List[QuestionRecord],
        answers: List[AnswerRecord],
        perturbations_by_answer: Dict[str, List[PerturbationRecord]],
        question_lookup: Dict[str, QuestionRecord],
        answer_lookup: Dict[str, AnswerRecord],
    ) -> Tuple[List[MetricResult], List[MetricResult]]:
        """Run Protocol A (LOQO) cross-validation.

        Yields one fold per question; trains on all other questions,
        tests on the held-out question's answers only.

        Returns:
            Tuple of (per_fold_results, aggregate_results).
            per_fold_results: one MetricResult per (fold, family).
            aggregate_results: one MetricResult per family averaged across folds.
        """
        per_fold_results: List[MetricResult] = []

        # Accumulate metric values across folds per family for aggregation.
        # Structure: {family: {metric_name: [values across folds]}}
        agg_buckets: Dict[str, Dict[str, List[float]]] = defaultdict(
            lambda: defaultdict(list)
        )
        # Track n_pairs per family across folds for aggregation
        agg_n_pairs: Dict[str, List[int]] = defaultdict(list)

        for fold in protocol_a_splits(questions, answers):
            train_idx = fold["train_answer_indices"]
            test_idx = fold["test_answer_indices"]

            train_answers = [answers[i] for i in train_idx]
            test_answers = [answers[i] for i in test_idx]

            # Fit grader on training set if it supports fitting
            if hasattr(self._grader, "fit"):
                self._grader.fit(train_answers, question_lookup)

            # CRITICAL: Filter perturbations to test-set answer_ids only
            test_answer_ids = {a.answer_id for a in test_answers}

            # Per-fold cache: graders with fit() produce fold-dependent scores,
            # so orig scores must be recomputed after each fit().
            fold_orig_cache: Dict[str, float] = {}
            grade_tuples = self._grade_perturbations(
                test_answers, perturbations_by_answer, question_lookup, answer_lookup,
                orig_score_cache=fold_orig_cache,
            )

            # Group grade tuples by family, then compute metrics per family
            family_grade_tuples = _group_by_family(grade_tuples, perturbations_by_answer, test_answer_ids)

            fold_id = fold["fold_id"]
            for family, tuples in family_grade_tuples.items():
                metric_result = self._compute_metric_result(
                    tuples, family, protocol="A", fold_or_qid=f"fold_{fold_id}"
                )
                per_fold_results.append(metric_result)

                # Accumulate for aggregation
                agg_n_pairs[family].append(metric_result.n_pairs)
                for metric_name in _metric_names_for_family(family):
                    val = getattr(metric_result, metric_name, None)
                    if val is not None:
                        agg_buckets[family][metric_name].append(val)

        # Build aggregate MetricResults (average across folds)
        aggregate_results = self._build_aggregate_results(
            agg_buckets, agg_n_pairs, protocol="A"
        )

        return per_fold_results, aggregate_results

    # ------------------------------------------------------------------
    # Protocol B: Within-question
    # ------------------------------------------------------------------

    def _run_protocol_b(
        self,
        questions: List[QuestionRecord],
        answers: List[AnswerRecord],
        perturbations_by_answer: Dict[str, List[PerturbationRecord]],
        question_lookup: Dict[str, QuestionRecord],
        answer_lookup: Dict[str, AnswerRecord],
    ) -> Tuple[List[MetricResult], List[MetricResult]]:
        """Run Protocol B (within-question) evaluation.

        For each question, trains on that question's train answers and tests
        on its test answers only.

        Returns:
            Tuple of (per_question_results, aggregate_results).
            per_question_results: one MetricResult per (question, family).
            aggregate_results: one MetricResult per family averaged across questions.
        """
        per_question_results: List[MetricResult] = []

        agg_buckets: Dict[str, Dict[str, List[float]]] = defaultdict(
            lambda: defaultdict(list)
        )
        agg_n_pairs: Dict[str, List[int]] = defaultdict(list)

        splits = protocol_b_splits(answers)

        # Build a lookup from answer_id -> AnswerRecord for fast train set construction
        answer_lookup_all: Dict[str, AnswerRecord] = {a.answer_id: a for a in answers}

        for q_id, (train_ids, test_ids) in splits.items():
            # Skip questions where test set is empty (Protocol B fallback for 1-answer Qs)
            if not test_ids:
                continue

            train_answers = [answer_lookup_all[aid] for aid in train_ids if aid in answer_lookup_all]
            test_answers = [answer_lookup_all[aid] for aid in test_ids if aid in answer_lookup_all]

            if not test_answers:
                continue

            # Fit grader on training set if it supports fitting
            if train_answers and hasattr(self._grader, "fit"):
                self._grader.fit(train_answers, question_lookup)

            test_answer_ids = {a.answer_id for a in test_answers}

            # Per-question cache: graders with fit() are re-fit per question
            # in Protocol B, so orig scores are question-dependent.
            q_orig_cache: Dict[str, float] = {}
            grade_tuples = self._grade_perturbations(
                test_answers, perturbations_by_answer, question_lookup, answer_lookup,
                orig_score_cache=q_orig_cache,
            )

            family_grade_tuples = _group_by_family(grade_tuples, perturbations_by_answer, test_answer_ids)

            for family, tuples in family_grade_tuples.items():
                metric_result = self._compute_metric_result(
                    tuples, family, protocol="B", fold_or_qid=q_id
                )
                per_question_results.append(metric_result)

                agg_n_pairs[family].append(metric_result.n_pairs)
                for metric_name in _metric_names_for_family(family):
                    val = getattr(metric_result, metric_name, None)
                    if val is not None:
                        agg_buckets[family][metric_name].append(val)

        aggregate_results = self._build_aggregate_results(
            agg_buckets, agg_n_pairs, protocol="B"
        )

        return per_question_results, aggregate_results

    # ------------------------------------------------------------------
    # Grade perturbations for a test set
    # ------------------------------------------------------------------

    def _grade_perturbations(
        self,
        test_answers: List[AnswerRecord],
        perturbations_by_answer: Dict[str, List[PerturbationRecord]],
        question_lookup: Dict[str, QuestionRecord],
        answer_lookup: Dict[str, AnswerRecord],
        orig_score_cache: Optional[Dict[str, float]] = None,
    ) -> List[Tuple[str, str, float, float]]:
        """Grade all perturbations for the given test answers.

        For each test answer, grades the ORIGINAL answer with the current grader
        (cached per answer_id to avoid redundant calls), then grades each
        perturbation. Returns (answer_id, perturb_type, orig_score, pert_score)
        tuples where orig_score is the grader's own score on the unperturbed text.

        This ensures robustness metrics measure grader-vs-grader consistency,
        not grader-vs-gold accuracy.

        Args:
            test_answers:            AnswerRecords to grade perturbations for.
            perturbations_by_answer: Dict mapping answer_id -> List[PerturbationRecord].
            question_lookup:         Dict mapping question_id -> QuestionRecord.
            answer_lookup:           Dict mapping answer_id -> AnswerRecord.
            orig_score_cache:        Optional shared cache for original scores.
                                     Mutated in-place to accumulate scores across
                                     folds (for graders with fit(), scores are
                                     fold-dependent so pass a new dict per fold).

        Returns:
            List of (answer_id, perturb_type, orig_score, pert_score) tuples.
            Score values are rounded to 6 decimals (RESEARCH.md Pitfall 1).
        """
        if orig_score_cache is None:
            orig_score_cache = {}

        results: List[Tuple[str, str, float, float]] = []

        for answer in test_answers:
            q = question_lookup.get(answer.question_id)
            if q is None:
                continue

            ref_answer = q.reference_answers[0] if q.reference_answers else ""

            # Grade the original (unperturbed) answer — cached per answer_id.
            # For graders with fit(), a new cache should be passed per fold
            # so scores reflect the current model state.
            if answer.answer_id not in orig_score_cache:
                orig_result = self._grade_single(
                    question=q.prompt,
                    rubric=q.rubric_text,
                    student_answer=answer.student_answer,
                    reference_answer=ref_answer,
                )
                orig_score_cache[answer.answer_id] = round(orig_result.score, 6)

            orig_score = orig_score_cache[answer.answer_id]

            perturbations = perturbations_by_answer.get(answer.answer_id, [])

            for pert in perturbations:
                grade_result = self._grade_single(
                    question=q.prompt,
                    rubric=q.rubric_text,
                    student_answer=pert.text,
                    reference_answer=ref_answer,
                )
                pert_score = round(grade_result.score, 6)
                results.append((answer.answer_id, pert.type, orig_score, pert_score))

        return results

    def _grade_single(
        self,
        question: str,
        rubric: Optional[str],
        student_answer: str,
        reference_answer: str,
    ) -> GradeResult:
        """Grade a single answer, passing reference_answer if accepted.

        Tries to call grade() with reference_answer kwarg first. If the grader
        raises TypeError (doesn't accept it), retries without.

        Args:
            question:         Question text.
            rubric:           Optional rubric text.
            student_answer:   Student/perturbed answer text.
            reference_answer: Reference answer for feature extraction.

        Returns:
            GradeResult from the grader.
        """
        try:
            return self._grader.grade(
                question=question,
                rubric=rubric,
                student_answer=student_answer,
                reference_answer=reference_answer,
            )
        except TypeError as e:
            if "reference_answer" in str(e):
                return self._grader.grade(
                    question=question,
                    rubric=rubric,
                    student_answer=student_answer,
                )
            raise

    # ------------------------------------------------------------------
    # Robustness drop comparison
    # ------------------------------------------------------------------

    def _compute_robustness_drop(
        self,
        proto_a_agg: List[MetricResult],
        proto_b_agg: List[MetricResult],
    ) -> List[Dict[str, Any]]:
        """Compute delta_a_minus_b for each metric in each family.

        Matches Protocol A and Protocol B aggregate results by family and
        computes delta = proto_a_value - proto_b_value for each metric.
        For IVR/ASR (higher_is_worse=True): positive delta means Protocol A
        shows worse robustness than Protocol B. For SSR (higher_is_worse=False):
        positive delta means Protocol A is BETTER (detects more perturbations).

        Args:
            proto_a_agg: Aggregate MetricResults from Protocol A.
            proto_b_agg: Aggregate MetricResults from Protocol B.

        Returns:
            List of dicts with keys:
                grader_name, perturbation_family, metric_name,
                proto_b_value, proto_a_value, delta_a_minus_b.
        """
        # Build lookup by family
        a_by_family: Dict[str, MetricResult] = {r.family: r for r in proto_a_agg}
        b_by_family: Dict[str, MetricResult] = {r.family: r for r in proto_b_agg}

        rows: List[Dict[str, Any]] = []
        all_families = set(a_by_family.keys()) | set(b_by_family.keys())

        for family in sorted(all_families):
            a_result = a_by_family.get(family)
            b_result = b_by_family.get(family)

            if a_result is None or b_result is None:
                continue

            for metric_name in _metric_names_for_family(family):
                a_val = getattr(a_result, metric_name, None)
                b_val = getattr(b_result, metric_name, None)

                if a_val is None or b_val is None:
                    continue

                delta = a_val - b_val
                # For IVR and ASR, higher = worse (more violations/gaming).
                # For SSR, higher = better (grader detects more perturbations).
                higher_is_worse = metric_name not in ("ssr_directional",)
                rows.append({
                    "grader_name": self._grader.grader_name,
                    "perturbation_family": family,
                    "metric_name": metric_name,
                    "proto_b_value": b_val,
                    "proto_a_value": a_val,
                    "delta_a_minus_b": delta,
                    "higher_is_worse": higher_is_worse,
                })

        return rows

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _compute_metric_result(
        self,
        grade_tuples: List[Tuple[str, str, float, float]],
        family: str,
        protocol: str,
        fold_or_qid: str,
    ) -> MetricResult:
        """Compute a MetricResult for one (fold/question, family) combination.

        Args:
            grade_tuples: (answer_id, perturb_type, orig_score, pert_score) tuples.
            family:       Perturbation family: "invariance", "sensitivity", "gaming".
            protocol:     "A" or "B".
            fold_or_qid:  Fold identifier (used for grader_name tag).

        Returns:
            MetricResult with computed metric values.
        """
        score_pairs = [(orig, pert) for _, _, orig, pert in grade_tuples]

        ivr_flip = None
        ivr_absdelta = None
        ssr_directional = None
        asr_thresholded = None

        if family == "invariance":
            ivr_flip = self._calc.ivr_flip(score_pairs)
            ivr_absdelta = self._calc.ivr_absdelta(score_pairs)
        elif family == "sensitivity":
            ssr_directional = self._calc.ssr_directional(score_pairs)
        elif family == "gaming":
            asr_thresholded = self._calc.asr_thresholded(score_pairs)

        by_type = self._calc.compute_by_type(grade_tuples, family)

        return MetricResult(
            grader_name=self._grader.grader_name,
            protocol=protocol,
            family=family,
            n_pairs=len(score_pairs),
            ivr_flip=ivr_flip,
            ivr_absdelta=ivr_absdelta,
            ssr_directional=ssr_directional,
            asr_thresholded=asr_thresholded,
            by_type=by_type,
        )

    def _build_aggregate_results(
        self,
        agg_buckets: Dict[str, Dict[str, List[float]]],
        agg_n_pairs: Dict[str, List[int]],
        protocol: str,
    ) -> List[MetricResult]:
        """Average metric values across folds/questions per family (macro-average).

        Each fold/question is weighted equally regardless of test-set size.
        This is intentional: it prevents large questions from dominating the
        aggregate. None values (from empty pair lists) are excluded from
        averaging. If all values for a metric are None, the aggregate is None.

        Args:
            agg_buckets:  {family: {metric_name: [non-NaN values across folds]}}.
            agg_n_pairs:  {family: [n_pairs per fold/question]}.
            protocol:     "A" or "B".

        Returns:
            One MetricResult per family with averaged metric values.
        """
        results: List[MetricResult] = []

        for family in sorted(agg_buckets.keys()):
            metrics = agg_buckets[family]
            total_n_pairs = sum(agg_n_pairs.get(family, []))

            ivr_flip = _safe_mean(metrics.get("ivr_flip", []))
            ivr_absdelta = _safe_mean(metrics.get("ivr_absdelta", []))
            ssr_directional = _safe_mean(metrics.get("ssr_directional", []))
            asr_thresholded = _safe_mean(metrics.get("asr_thresholded", []))

            results.append(MetricResult(
                grader_name=self._grader.grader_name,
                protocol=protocol,
                family=family,
                n_pairs=total_n_pairs,
                ivr_flip=ivr_flip,
                ivr_absdelta=ivr_absdelta,
                ssr_directional=ssr_directional,
                asr_thresholded=asr_thresholded,
            ))

        return results


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------


def _metric_names_for_family(family: str) -> List[str]:
    """Return the metric field names applicable to a perturbation family.

    Args:
        family: "invariance", "sensitivity", or "gaming".

    Returns:
        List of MetricResult field names.
    """
    if family == "invariance":
        return ["ivr_flip", "ivr_absdelta"]
    elif family == "sensitivity":
        return ["ssr_directional"]
    elif family == "gaming":
        return ["asr_thresholded"]
    return []


def _safe_mean(values: List[float]) -> Optional[float]:
    """Compute mean of a list, returning None if empty.

    Args:
        values: List of float values (already filtered to exclude None/NaN).

    Returns:
        Mean of values, or None if values is empty.
    """
    if not values:
        return None
    return sum(values) / len(values)


def _group_by_family(
    grade_tuples: List[Tuple[str, str, float, float]],
    perturbations_by_answer: Dict[str, List[PerturbationRecord]],
    test_answer_ids: set,
) -> Dict[str, List[Tuple[str, str, float, float]]]:
    """Group grade tuples by perturbation family.

    Looks up the family for each perturbation type by scanning the original
    PerturbationRecords. Uses perturb type as the key stored in grade_tuples.

    Since grade_tuples contain (answer_id, perturb_type, gold_score, pert_score)
    and PerturbationRecord has both type and family fields, we need to build a
    type -> family mapping from the perturbations for test answers.

    Args:
        grade_tuples:            Output of _grade_perturbations().
        perturbations_by_answer: All perturbations grouped by answer_id.
        test_answer_ids:         Set of answer_ids in the test partition.

    Returns:
        Dict mapping family -> list of grade tuples for that family.
    """
    # Build perturb_type -> family mapping from test set perturbations
    type_to_family: Dict[str, str] = {}
    for answer_id in test_answer_ids:
        for pert in perturbations_by_answer.get(answer_id, []):
            type_to_family[pert.type] = pert.family

    # Group grade tuples by family
    by_family: Dict[str, List[Tuple[str, str, float, float]]] = defaultdict(list)
    for answer_id, perturb_type, gold_score, pert_score in grade_tuples:
        family = type_to_family.get(perturb_type)
        if family is not None:
            by_family[family].append((answer_id, perturb_type, gold_score, pert_score))

    return dict(by_family)
