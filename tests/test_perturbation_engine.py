"""
End-to-end tests for PerturbationEngine on real Beetle data.

All tests are marked @pytest.mark.slow because they load the SentenceTransformer
model (all-MiniLM-L6-v2) or real Beetle corpus data — both take several seconds
on first run. Use `-m "not slow"` to skip these in fast CI pipelines.

Test coverage:
  1. All answers receive at least one PerturbationRecord.
  2. At most 10 perturbations per answer (gate rejections may produce fewer).
  3. Determinism: same seed + same input = identical output across two runs.
  4. All three families (invariance, sensitivity, gaming) are present.
  5. All seven canonical type strings are present.
  6. Every record has correct fields: generator="rule-based", correct family, correct perturb_id prefix.
  7. GateLog accumulates gate1/gate2 data with correct bypass behavior.
  8. Gate 1 is NEVER tested for typo_insertion.
  9. Cache produces identical output on re-run and persists to disk.
  10. Output PerturbationRecords are compatible with EvaluationEngine.

Module-scoped fixtures (beetle_data, engine) are shared across tests to avoid
reloading the corpus and model for each test.
"""

import pytest

from asag.perturbations import PERTURBATION_TYPES, PerturbationEngine


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def beetle_data():
    """Load Beetle corpus and return first 5 questions + their answers.

    Uses a 5-question subset for speed while still covering meaningful
    diversity of answer lengths and vocabulary.
    """
    from asag.loaders import SemEval2013Loader

    loader = SemEval2013Loader("beetle")
    questions, answers = loader.load()

    # Subset: first 5 questions and all their answers
    q_ids = {q.question_id for q in questions[:5]}
    subset_q = [q for q in questions if q.question_id in q_ids]
    subset_a = [a for a in answers if a.question_id in q_ids]
    return subset_q, subset_a


@pytest.fixture(scope="module")
def engine():
    """PerturbationEngine with seed=42, no cache (tests are self-contained)."""
    return PerturbationEngine(seed=42)


@pytest.fixture(scope="module")
def engine_output(beetle_data, engine):
    """Run engine once; share output across all tests that only need the records."""
    questions, answers = beetle_data
    records, gate_log = engine.generate_all(answers, questions)
    return records, gate_log


# ---------------------------------------------------------------------------
# Test 1: every answer has at least one perturbation
# ---------------------------------------------------------------------------


@pytest.mark.slow
def test_generates_perturbations_for_all_answers(beetle_data, engine_output):
    """Every input answer_id must appear in at least one output PerturbationRecord."""
    _, answers = beetle_data
    records, _ = engine_output

    answer_ids_in_input = {a.answer_id for a in answers}
    answer_ids_in_output = {r.answer_id for r in records}

    # Every answer should have at least one perturbation
    missing = answer_ids_in_input - answer_ids_in_output
    assert not missing, (
        f"{len(missing)} answers have no perturbations: {list(missing)[:5]}"
    )
    assert len(records) > 0, "Expected at least 1 PerturbationRecord"


# ---------------------------------------------------------------------------
# Test 2: at most 10 perturbations per answer; distribution checks
# ---------------------------------------------------------------------------


@pytest.mark.slow
def test_distribution_10_per_answer(beetle_data, engine_output):
    """Each answer has <= 10 perturbations; type counts respect generator n_variants."""
    _, answers = beetle_data
    records, _ = engine_output

    # Group records by answer_id
    from collections import defaultdict
    by_answer = defaultdict(list)
    for r in records:
        by_answer[r.answer_id].append(r)

    # Multi-variant type caps
    MAX_BY_TYPE = {
        "synonym_substitution": 2,
        "typo_insertion": 1,
        "negation_insertion": 1,
        "key_concept_deletion": 1,
        "semantic_contradiction": 2,
        "rubric_keyword_echoing": 2,
        "fluent_wrong_extension": 1,
    }

    violations = []
    for answer_id, recs in by_answer.items():
        # Total cap
        if len(recs) > 10:
            violations.append(f"{answer_id}: {len(recs)} records (>10)")

        # Per-type cap
        type_counts = defaultdict(int)
        for r in recs:
            type_counts[r.type] += 1
        for ptype, count in type_counts.items():
            cap = MAX_BY_TYPE.get(ptype, 0)
            if count > cap:
                violations.append(
                    f"{answer_id}: {ptype} has {count} records (cap={cap})"
                )

    assert not violations, (
        f"Distribution violations found:\n" + "\n".join(violations[:10])
    )


# ---------------------------------------------------------------------------
# Test 3: determinism — same seed produces identical output
# ---------------------------------------------------------------------------


@pytest.mark.slow
def test_determinism_same_seed(beetle_data):
    """Two runs with same seed must produce bit-identical PerturbationRecords."""
    questions, answers = beetle_data

    # Use a fresh engine for each run (no shared encoder state that could differ)
    engine_a = PerturbationEngine(seed=42)
    records_a, _ = engine_a.generate_all(answers, questions)

    engine_b = PerturbationEngine(seed=42, encoder=engine_a._encoder)  # reuse encoder
    records_b, _ = engine_b.generate_all(answers, questions)

    assert len(records_a) == len(records_b), (
        f"Run 1: {len(records_a)} records, Run 2: {len(records_b)} records"
    )

    for i, (r1, r2) in enumerate(zip(records_a, records_b)):
        assert r1.perturb_id == r2.perturb_id, (
            f"Record {i}: perturb_id mismatch: {r1.perturb_id!r} != {r2.perturb_id!r}"
        )
        assert r1.text == r2.text, (
            f"Record {i}: text mismatch at {r1.perturb_id!r}"
        )


# ---------------------------------------------------------------------------
# Test 4: all three families present
# ---------------------------------------------------------------------------


@pytest.mark.slow
def test_all_families_present(engine_output):
    """Output records must include all three perturbation families."""
    records, _ = engine_output
    families_found = {r.family for r in records}
    assert "invariance" in families_found, "Missing invariance family"
    assert "sensitivity" in families_found, "Missing sensitivity family"
    assert "gaming" in families_found, "Missing gaming family"


# ---------------------------------------------------------------------------
# Test 5: all seven canonical types present
# ---------------------------------------------------------------------------


@pytest.mark.slow
def test_all_seven_types_present(engine_output):
    """Output records must include all 7 canonical type strings."""
    records, _ = engine_output
    types_found = {r.type for r in records}
    expected_types = set(PERTURBATION_TYPES.keys())
    missing = expected_types - types_found
    assert not missing, f"Missing perturbation types: {missing}"


# ---------------------------------------------------------------------------
# Test 6: all records have correct fields
# ---------------------------------------------------------------------------


@pytest.mark.slow
def test_perturbation_records_have_correct_fields(engine_output):
    """Every PerturbationRecord must have correct generator, family, and perturb_id."""
    records, _ = engine_output

    field_errors = []
    for r in records:
        # generator must be "rule-based"
        if r.generator != "rule-based":
            field_errors.append(
                f"{r.perturb_id}: generator={r.generator!r} (expected 'rule-based')"
            )

        # family must match PERTURBATION_TYPES[type]
        expected_family = PERTURBATION_TYPES.get(r.type)
        if expected_family is None:
            field_errors.append(f"{r.perturb_id}: unknown type {r.type!r}")
        elif r.family != expected_family:
            field_errors.append(
                f"{r.perturb_id}: family={r.family!r} (expected {expected_family!r} for {r.type!r})"
            )

        # perturb_id must start with answer_id
        if not r.perturb_id.startswith(r.answer_id):
            field_errors.append(
                f"perturb_id {r.perturb_id!r} does not start with answer_id {r.answer_id!r}"
            )

    assert not field_errors, (
        f"{len(field_errors)} field errors:\n" + "\n".join(field_errors[:10])
    )


# ---------------------------------------------------------------------------
# Test 7: GateLog accumulates data after generate_all
# ---------------------------------------------------------------------------


@pytest.mark.slow
def test_gate_log_has_data(engine_output):
    """GateLog must have non-zero gate1 data for synonym_substitution and valid rates."""
    _, gate_log = engine_output

    # Gate 1 must have tested synonym_substitution candidates
    assert gate_log.gate1_tested_by_type.get("synonym_substitution", 0) > 0, (
        "Gate 1 was never tested for synonym_substitution"
    )

    # Gate 2 must have entries for invariance types
    assert len(gate_log.gate2_tested_by_type) > 0, (
        "Gate 2 was never tested for any type"
    )

    # rejection_rates() must return valid structure
    rates = gate_log.rejection_rates()
    assert "gate1" in rates, "rejection_rates() missing 'gate1' key"
    assert "gate2" in rates, "rejection_rates() missing 'gate2' key"

    # All rates must be floats in [0.0, 1.0]
    for gate_key in ("gate1", "gate2"):
        for type_name, rate in rates[gate_key].items():
            assert isinstance(rate, float), (
                f"rejection_rates()[{gate_key!r}][{type_name!r}] = {rate!r} (not float)"
            )
            assert 0.0 <= rate <= 1.0, (
                f"rejection_rates()[{gate_key!r}][{type_name!r}] = {rate:.4f} (out of [0,1])"
            )


# ---------------------------------------------------------------------------
# Test 8: Gate 1 never applied to typo_insertion
# ---------------------------------------------------------------------------


@pytest.mark.slow
def test_gate1_not_applied_to_typo(engine_output):
    """Gate 1 (SBERT cosine) must never be tested for typo_insertion.

    Typo insertions are surface-level changes — Gate 1 is intentionally bypassed
    for this type (RESEARCH.md Critical Finding 1).
    """
    _, gate_log = engine_output
    typo_tested = gate_log.gate1_tested_by_type.get("typo_insertion", 0)
    assert typo_tested == 0, (
        f"Gate 1 was tested {typo_tested} times for typo_insertion (must be 0)"
    )


# ---------------------------------------------------------------------------
# Test 9: cache enables fast re-run with identical output
# ---------------------------------------------------------------------------


@pytest.mark.slow
def test_cache_enables_fast_rerun(beetle_data, tmp_path):
    """Cache must produce identical output on re-run and persist to disk."""
    questions, answers = beetle_data
    # Use only first 2 answers for speed
    small_a = answers[:2]
    small_q = [q for q in questions if q.question_id in {a.question_id for a in small_a}]

    # First run — populates cache
    engine_1 = PerturbationEngine(seed=42, cache_dir=tmp_path)
    records_1, _ = engine_1.generate_all(small_a, small_q)

    # Cache file must exist
    cache_file = tmp_path / "perturbation_cache.jsonl"
    assert cache_file.exists(), f"Cache file not found at {cache_file}"
    assert cache_file.stat().st_size > 0, "Cache file is empty"

    # Second run — reads from cache (reuse encoder to avoid extra model load)
    engine_2 = PerturbationEngine(seed=42, cache_dir=tmp_path, encoder=engine_1._encoder)
    records_2, _ = engine_2.generate_all(small_a, small_q)

    # Output must be identical
    assert len(records_1) == len(records_2), (
        f"Cache re-run: {len(records_1)} vs {len(records_2)} records"
    )
    for i, (r1, r2) in enumerate(zip(records_1, records_2)):
        assert r1.perturb_id == r2.perturb_id, (
            f"Record {i}: perturb_id mismatch on cache hit"
        )
        assert r1.text == r2.text, (
            f"Record {i}: text mismatch on cache hit at {r1.perturb_id!r}"
        )


# ---------------------------------------------------------------------------
# Test 10: output records are compatible with EvaluationEngine
# ---------------------------------------------------------------------------


@pytest.mark.slow
def test_perturbation_records_compatible_with_evaluation_engine(engine_output):
    """Every output record type must map to a known family (EvaluationEngine compatibility).

    The EvaluationEngine groups PerturbationRecords by family. This test confirms
    every record produced by PerturbationEngine has a type that maps to a known
    family in PERTURBATION_TYPES — no unknown types that would cause downstream
    KeyError or silent misclassification.
    """
    records, _ = engine_output

    unknown_types = set()
    for r in records:
        if r.type not in PERTURBATION_TYPES:
            unknown_types.add(r.type)

    assert not unknown_types, (
        f"PerturbationEngine produced records with unknown types: {unknown_types}. "
        f"These are not consumable by EvaluationEngine."
    )

    # Also verify direct field compatibility: family must be a valid Literal value
    valid_families = {"invariance", "sensitivity", "gaming"}
    invalid_families = {r.family for r in records} - valid_families
    assert not invalid_families, (
        f"Records have invalid family values: {invalid_families}"
    )
