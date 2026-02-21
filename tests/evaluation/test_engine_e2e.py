"""
E2E tests for EvaluationEngine.

Tests that the full evaluation loop — HybridGrader + Protocol A (LOQO) +
Protocol B (within-question) + MetricCalculator — works end-to-end on real
Beetle and SciEntsBank corpus subsets with mock perturbations.

Mock perturbations strategy (one per family per answer):
  - invariance (family="invariance", type="mock_synonym"):
      text = student_answer + " indeed"
  - sensitivity (family="sensitivity", type="mock_negation"):
      text = "Not " + student_answer
  - gaming (family="gaming", type="mock_keyword_spam"):
      text = student_answer + " excellent perfect accurate"

All tests are marked @pytest.mark.slow — skip in CI with: pytest -m "not slow"

Expected runtime: 30-60s per test (HybridGrader SBERT encoding dominates).
"""

from pathlib import Path
from typing import List

import pytest

from asag.evaluation import EvaluationEngine, EvaluationResult
from asag.graders.hybrid import HybridGrader
from asag.infra.storage import load_json
from asag.loaders.semeval2013 import SemEval2013Loader
from asag.schema import AnswerRecord, PerturbationRecord, QuestionRecord

# ---------------------------------------------------------------------------
# Required keys for robustness drop rows
# ---------------------------------------------------------------------------

REQUIRED_DROP_KEYS = {
    "grader_name",
    "perturbation_family",
    "metric_name",
    "proto_b_value",
    "proto_a_value",
    "delta_a_minus_b",
}

# ---------------------------------------------------------------------------
# Shared helper: mock perturbations
# ---------------------------------------------------------------------------


def make_mock_perturbations(answers: List[AnswerRecord]) -> List[PerturbationRecord]:
    """Create 3 mock PerturbationRecords per answer (one per family).

    Args:
        answers: List of AnswerRecords to create perturbations for.

    Returns:
        List of PerturbationRecords — 3 per answer.
    """
    perturbations: List[PerturbationRecord] = []
    for answer in answers:
        aid = answer.answer_id
        text = answer.student_answer

        # Invariance: trivial surface change — should NOT change grade
        perturbations.append(
            PerturbationRecord(
                perturb_id=f"{aid}_inv_001",
                answer_id=aid,
                family="invariance",
                type="mock_synonym",
                generator="mock",
                seed=0,
                text=text + " indeed",
            )
        )

        # Sensitivity: negation prepended — should change grade
        perturbations.append(
            PerturbationRecord(
                perturb_id=f"{aid}_sen_001",
                answer_id=aid,
                family="sensitivity",
                type="mock_negation",
                generator="mock",
                seed=0,
                text="Not " + text,
            )
        )

        # Gaming: keyword stuffing — adversarial attempt
        perturbations.append(
            PerturbationRecord(
                perturb_id=f"{aid}_gam_001",
                answer_id=aid,
                family="gaming",
                type="mock_keyword_spam",
                generator="mock",
                seed=0,
                text=text + " excellent perfect accurate",
            )
        )

    return perturbations


# ---------------------------------------------------------------------------
# Shared fixture: Beetle 3-question subset
# ---------------------------------------------------------------------------


def _load_beetle_subset():
    """Load first 3 Beetle questions (sorted by question_id) and their answers.

    Returns:
        Tuple of (subset_questions, subset_answers, mock_perturbations).
    """
    loader = SemEval2013Loader("beetle")
    questions, answers = loader.load()

    # Select 3 questions reproducibly (sorted by question_id)
    subset_qids = sorted({q.question_id for q in questions})[:3]
    subset_qid_set = set(subset_qids)

    subset_questions = [q for q in questions if q.question_id in subset_qid_set]
    subset_answers = [a for a in answers if a.question_id in subset_qid_set]
    mock_perturbations = make_mock_perturbations(subset_answers)

    return subset_questions, subset_answers, mock_perturbations


def _load_scientsbank_subset():
    """Load first 3 SciEntsBank questions (sorted by question_id) and their answers.

    Returns:
        Tuple of (subset_questions, subset_answers, mock_perturbations).
    """
    loader = SemEval2013Loader("scientsbank")
    questions, answers = loader.load()

    subset_qids = sorted({q.question_id for q in questions})[:3]
    subset_qid_set = set(subset_qids)

    subset_questions = [q for q in questions if q.question_id in subset_qid_set]
    subset_answers = [a for a in answers if a.question_id in subset_qid_set]
    mock_perturbations = make_mock_perturbations(subset_answers)

    return subset_questions, subset_answers, mock_perturbations


# ---------------------------------------------------------------------------
# Tests: Beetle subset
# ---------------------------------------------------------------------------


@pytest.mark.slow
def test_e2e_beetle_subset(tmp_path):
    """Full evaluation loop on Beetle 3-question subset under both protocols."""
    subset_questions, subset_answers, mock_perturbations = _load_beetle_subset()

    grader = HybridGrader()
    engine = EvaluationEngine(grader, corpus="beetle")

    result = engine.run(
        subset_questions,
        subset_answers,
        mock_perturbations,
        protocols=["A", "B"],
        run_dir=tmp_path / "beetle_run",
    )

    # Basic type assertions
    assert isinstance(result, EvaluationResult)
    assert result.grader_name == "hybrid_logreg_minilm"
    assert result.corpus == "beetle"
    assert result.protocols_run == ["A", "B"]

    # Protocol A results must exist
    assert len(result.protocol_a_results) > 0, "Protocol A should produce fold results"
    assert len(result.protocol_b_results) > 0, "Protocol B should produce question results"

    # Aggregates: one per family (invariance, sensitivity, gaming)
    assert len(result.protocol_a_aggregate) == 3, (
        f"Expected 3 Protocol A aggregate results (one per family), "
        f"got {len(result.protocol_a_aggregate)}"
    )
    assert len(result.protocol_b_aggregate) == 3, (
        f"Expected 3 Protocol B aggregate results (one per family), "
        f"got {len(result.protocol_b_aggregate)}"
    )

    # All aggregates must have n_pairs > 0
    for agg in result.protocol_a_aggregate:
        assert agg.n_pairs > 0, f"Protocol A aggregate for {agg.family} has n_pairs=0"
    for agg in result.protocol_b_aggregate:
        assert agg.n_pairs > 0, f"Protocol B aggregate for {agg.family} has n_pairs=0"

    # Robustness drop must have rows
    assert len(result.robustness_drop) > 0, "Robustness drop should have rows"

    # All required keys present in every drop row
    for row in result.robustness_drop:
        missing = REQUIRED_DROP_KEYS - set(row.keys())
        assert not missing, f"Drop row missing keys: {missing}. Row: {row}"

    # Result file must exist on disk
    assert (tmp_path / "beetle_run" / "evaluation_result.json").exists(), (
        "evaluation_result.json was not written to run_dir"
    )


# ---------------------------------------------------------------------------
# Tests: SciEntsBank subset
# ---------------------------------------------------------------------------


@pytest.mark.slow
def test_e2e_scientsbank_subset(tmp_path):
    """Full evaluation loop on SciEntsBank 3-question subset under both protocols."""
    subset_questions, subset_answers, mock_perturbations = _load_scientsbank_subset()

    grader = HybridGrader()
    engine = EvaluationEngine(grader, corpus="scientsbank")

    result = engine.run(
        subset_questions,
        subset_answers,
        mock_perturbations,
        protocols=["A", "B"],
        run_dir=tmp_path / "scientsbank_run",
    )

    # Basic type assertions
    assert isinstance(result, EvaluationResult)
    assert result.grader_name == "hybrid_logreg_minilm"
    assert result.corpus == "scientsbank"
    assert result.protocols_run == ["A", "B"]

    # Protocol results must exist
    assert len(result.protocol_a_results) > 0
    assert len(result.protocol_b_results) > 0

    # Aggregates: one per family
    assert len(result.protocol_a_aggregate) == 3, (
        f"Expected 3 Protocol A aggregate results, got {len(result.protocol_a_aggregate)}"
    )
    assert len(result.protocol_b_aggregate) == 3, (
        f"Expected 3 Protocol B aggregate results, got {len(result.protocol_b_aggregate)}"
    )

    # n_pairs > 0 for all aggregates
    for agg in result.protocol_a_aggregate:
        assert agg.n_pairs > 0, f"Protocol A aggregate for {agg.family} has n_pairs=0"
    for agg in result.protocol_b_aggregate:
        assert agg.n_pairs > 0, f"Protocol B aggregate for {agg.family} has n_pairs=0"

    # Robustness drop must have rows with correct keys
    assert len(result.robustness_drop) > 0
    for row in result.robustness_drop:
        missing = REQUIRED_DROP_KEYS - set(row.keys())
        assert not missing, f"Drop row missing keys: {missing}. Row: {row}"

    # Result file must exist on disk
    assert (tmp_path / "scientsbank_run" / "evaluation_result.json").exists()


# ---------------------------------------------------------------------------
# Tests: JSON roundtrip
# ---------------------------------------------------------------------------


@pytest.mark.slow
def test_e2e_result_serializable(tmp_path):
    """EvaluationResult must serialize to JSON and roundtrip without data loss."""
    subset_questions, subset_answers, mock_perturbations = _load_beetle_subset()

    grader = HybridGrader()
    engine = EvaluationEngine(grader, corpus="beetle")

    result = engine.run(
        subset_questions,
        subset_answers,
        mock_perturbations,
        protocols=["A", "B"],
        run_dir=tmp_path / "serial_run",
    )

    # model_dump_json must not raise
    json_str = result.model_dump_json()
    assert isinstance(json_str, str)
    assert len(json_str) > 0

    # Roundtrip: validate back from JSON
    restored = EvaluationResult.model_validate_json(json_str)
    assert restored.grader_name == result.grader_name
    assert restored.corpus == result.corpus
    assert restored.protocols_run == result.protocols_run
    assert len(restored.protocol_a_results) == len(result.protocol_a_results)
    assert len(restored.protocol_b_results) == len(result.protocol_b_results)
    assert len(restored.protocol_a_aggregate) == len(result.protocol_a_aggregate)
    assert len(restored.protocol_b_aggregate) == len(result.protocol_b_aggregate)
    assert len(restored.robustness_drop) == len(result.robustness_drop)


# ---------------------------------------------------------------------------
# Tests: Persistence to disk
# ---------------------------------------------------------------------------


@pytest.mark.slow
def test_e2e_result_persisted_to_disk(tmp_path):
    """EvaluationEngine.run() must write evaluation_result.json via save_json.

    This directly validates Roadmap Phase 2 success criterion #5:
    'writes results to the structured store'.
    """
    subset_questions, subset_answers, mock_perturbations = _load_beetle_subset()

    grader = HybridGrader()
    engine = EvaluationEngine(grader, corpus="beetle")

    run_dir = tmp_path / "test_run"
    result = engine.run(
        subset_questions,
        subset_answers,
        mock_perturbations,
        protocols=["A", "B"],
        run_dir=run_dir,
    )

    # File must exist
    result_file = run_dir / "evaluation_result.json"
    assert result_file.exists(), f"evaluation_result.json not found at {result_file}"

    # Load back and verify contents
    data = load_json(result_file)

    assert data["grader_name"] == "hybrid_logreg_minilm", (
        f"Expected grader_name='hybrid_logreg_minilm', got {data['grader_name']!r}"
    )
    assert data["corpus"] == "beetle", (
        f"Expected corpus='beetle', got {data['corpus']!r}"
    )
    assert "protocols_run" in data
    assert "protocol_a_results" in data
    assert "protocol_b_results" in data
    assert "protocol_a_aggregate" in data
    assert "protocol_b_aggregate" in data
    assert "robustness_drop" in data

    # Verify aggregate structure from disk
    assert len(data["protocol_a_aggregate"]) == 3
    assert len(data["protocol_b_aggregate"]) == 3
