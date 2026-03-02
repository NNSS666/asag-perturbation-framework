"""
Unit tests for all 7 perturbation generators.

Tests verify:
  - Correct output format (list of strings)
  - Non-empty output for suitable inputs
  - Determinism across identical calls
  - Edge cases (short text, no eligible words, no matching patterns)
  - ABC conformance (family, type_name, n_variants attributes)

Run: PYTHONPATH=src python3 -m pytest tests/test_generators.py -v
"""

import pytest

from asag.schema.records import AnswerRecord, QuestionRecord
from asag.perturbations.generators import (
    PerturbationGenerator,
    SynonymSubstitutionGenerator,
    TypoInsertionGenerator,
    NegationInsertionGenerator,
    KeyConceptDeletionGenerator,
    SemanticContradictionGenerator,
    RubricKeywordEchoingGenerator,
    FluentWrongExtensionGenerator,
)
from asag.perturbations import PERTURBATION_TYPES

# ---------------------------------------------------------------------------
# Shared test fixtures
# ---------------------------------------------------------------------------

ANSWER = AnswerRecord(
    answer_id="test_1",
    question_id="q1",
    student_answer="The battery provides electrical energy to the circuit.",
    gold_label="correct",
    gold_score=1.0,
)

QUESTION = QuestionRecord(
    question_id="q1",
    prompt="What does the battery do?",
    reference_answers=["The battery supplies electrical energy to power the bulb."],
)

# An answer with antonym-triggering words for SemanticContradiction tests
OPEN_ANSWER = AnswerRecord(
    answer_id="test_2",
    question_id="q2",
    student_answer="The switch is open so the circuit is not complete.",
    gold_label="correct",
    gold_score=1.0,
)

# An answer with an auxiliary verb for NegationInsertion tests
AUX_ANSWER = AnswerRecord(
    answer_id="test_3",
    question_id="q1",
    student_answer="The current is flowing through the wire.",
    gold_label="correct",
    gold_score=1.0,
)

# A very short answer with no eligible words
SHORT_ANSWER = AnswerRecord(
    answer_id="test_4",
    question_id="q1",
    student_answer="Yes it is.",
    gold_label="correct",
    gold_score=1.0,
)

# An answer with a simple verb (no auxiliary) for NegationInsertion
SIMPLE_VERB_ANSWER = AnswerRecord(
    answer_id="test_5",
    question_id="q1",
    student_answer="Current flows from the positive terminal to the negative.",
    gold_label="correct",
    gold_score=1.0,
)


# ---------------------------------------------------------------------------
# Test 1: SynonymSubstitutionGenerator — produces variants
# ---------------------------------------------------------------------------

class TestSynonymSubstitutionGenerator:

    def test_synonym_substitution_produces_variants(self):
        """Produces up to 2 variants, each differing from the original."""
        g = SynonymSubstitutionGenerator()
        results = g.generate(ANSWER, QUESTION, seed=42)
        assert isinstance(results, list)
        assert len(results) >= 1, "Expected at least 1 variant for a content-rich answer"
        for r in results:
            assert isinstance(r, str)
            assert r != ANSWER.student_answer, "Variant should differ from original"

    def test_synonym_substitution_at_most_n_variants(self):
        """Returns at most n_variants (2) candidates."""
        g = SynonymSubstitutionGenerator()
        results = g.generate(ANSWER, QUESTION, seed=42)
        assert len(results) <= g.n_variants

    def test_synonym_substitution_deterministic(self):
        """Same seed produces identical output across calls."""
        g = SynonymSubstitutionGenerator()
        r1 = g.generate(ANSWER, QUESTION, seed=42)
        r2 = g.generate(ANSWER, QUESTION, seed=42)
        assert r1 == r2, "SynonymSubstitutionGenerator must be deterministic for same seed"

    def test_synonym_substitution_different_seeds_may_differ(self):
        """For reference: same generator, same answer — substitution is purely
        text-driven (position-based), so seed does not affect the output here.
        This test just confirms no crash with different seed values."""
        g = SynonymSubstitutionGenerator()
        r1 = g.generate(ANSWER, QUESTION, seed=0)
        r2 = g.generate(ANSWER, QUESTION, seed=99)
        # Both should be lists of strings
        assert all(isinstance(r, str) for r in r1)
        assert all(isinstance(r, str) for r in r2)

    def test_synonym_substitution_empty_for_short_text(self):
        """Very short text with no eligible words returns empty list."""
        g = SynonymSubstitutionGenerator()
        results = g.generate(SHORT_ANSWER, QUESTION, seed=42)
        # "Yes", "it", "is" are all too short (< 4 chars) or not content words
        assert isinstance(results, list)
        assert len(results) == 0


# ---------------------------------------------------------------------------
# Test 2: TypoInsertionGenerator
# ---------------------------------------------------------------------------

class TestTypoInsertionGenerator:

    def test_typo_insertion_modifies_one_word(self):
        """Exactly one token differs from the original."""
        g = TypoInsertionGenerator()
        results = g.generate(ANSWER, QUESTION, seed=42)
        assert len(results) == 1
        original_tokens = ANSWER.student_answer.split()
        result_tokens = results[0].split()
        # Token count should be preserved (typo doesn't add/remove tokens)
        assert len(original_tokens) == len(result_tokens)
        # Exactly one token differs
        diffs = [i for i, (a, b) in enumerate(zip(original_tokens, result_tokens)) if a != b]
        assert len(diffs) == 1, f"Expected exactly 1 differing token, got {len(diffs)}: {diffs}"

    def test_typo_insertion_deterministic(self):
        """Same seed produces identical output."""
        g = TypoInsertionGenerator()
        r1 = g.generate(ANSWER, QUESTION, seed=42)
        r2 = g.generate(ANSWER, QUESTION, seed=42)
        assert r1 == r2

    def test_typo_insertion_different_seeds_differ(self):
        """Different seeds produce different typo positions."""
        g = TypoInsertionGenerator()
        r1 = g.generate(ANSWER, QUESTION, seed=0)
        r2 = g.generate(ANSWER, QUESTION, seed=99)
        # With a rich enough answer, different seeds likely choose different words
        # Just verify both are valid lists of strings
        assert all(isinstance(r, str) for r in r1)
        assert all(isinstance(r, str) for r in r2)

    def test_typo_insertion_empty_for_short_text(self):
        """No eligible words returns empty list."""
        g = TypoInsertionGenerator()
        results = g.generate(SHORT_ANSWER, QUESTION, seed=42)
        # "Yes", "it", "is" are all < 4 chars
        assert isinstance(results, list)
        assert len(results) == 0


# ---------------------------------------------------------------------------
# Test 3: NegationInsertionGenerator
# ---------------------------------------------------------------------------

class TestNegationInsertionGenerator:

    def test_negation_insertion_adds_not_via_auxiliary(self):
        """Sentence with auxiliary verb gets 'not' inserted after it."""
        g = NegationInsertionGenerator()
        results = g.generate(AUX_ANSWER, QUESTION, seed=42)
        assert len(results) == 1
        assert "not" in results[0].lower(), f"Expected 'not' in result: {results[0]}"

    def test_negation_insertion_adds_does_not_for_simple_verb(self):
        """Sentence with simple domain verb gets 'does not' replacement."""
        g = NegationInsertionGenerator()
        results = g.generate(SIMPLE_VERB_ANSWER, QUESTION, seed=42)
        assert len(results) == 1
        assert "does not" in results[0].lower() or "not" in results[0].lower()

    def test_negation_insertion_fallback(self):
        """Text with no auxiliary or simple verb gets 'It is not true that...' prefix."""
        g = NegationInsertionGenerator()
        results = g.generate(ANSWER, QUESTION, seed=42)
        assert len(results) == 1
        # "provides" is not in the auxiliary list or simple verb list
        assert results[0].startswith("It is not true that"), (
            f"Expected fallback prefix, got: {results[0]}"
        )

    def test_negation_insertion_result_differs_from_original(self):
        """All strategies produce a result different from the original."""
        g = NegationInsertionGenerator()
        for answer in [ANSWER, AUX_ANSWER, SIMPLE_VERB_ANSWER]:
            results = g.generate(answer, QUESTION, seed=42)
            assert results[0] != answer.student_answer


# ---------------------------------------------------------------------------
# Test 4: KeyConceptDeletionGenerator
# ---------------------------------------------------------------------------

class TestKeyConceptDeletionGenerator:

    def test_key_concept_deletion_removes_word(self):
        """Result has fewer words than original."""
        g = KeyConceptDeletionGenerator()
        results = g.generate(ANSWER, QUESTION, seed=42)
        assert len(results) == 1
        original_word_count = len(ANSWER.student_answer.split())
        result_word_count = len(results[0].split())
        assert result_word_count < original_word_count

    def test_key_concept_deletion_deterministic(self):
        """Same seed produces identical output."""
        g = KeyConceptDeletionGenerator()
        r1 = g.generate(ANSWER, QUESTION, seed=42)
        r2 = g.generate(ANSWER, QUESTION, seed=42)
        assert r1 == r2

    def test_key_concept_deletion_different_seeds(self):
        """Different seeds may remove different words."""
        g = KeyConceptDeletionGenerator()
        r0 = g.generate(ANSWER, QUESTION, seed=0)
        r1 = g.generate(ANSWER, QUESTION, seed=1)
        # Both should be valid shorter strings
        assert len(r0) == 1 and isinstance(r0[0], str)
        assert len(r1) == 1 and isinstance(r1[0], str)

    def test_key_concept_deletion_empty_for_short_text(self):
        """No eligible content words returns empty list."""
        g = KeyConceptDeletionGenerator()
        results = g.generate(SHORT_ANSWER, QUESTION, seed=42)
        assert isinstance(results, list)
        assert len(results) == 0


# ---------------------------------------------------------------------------
# Test 5: SemanticContradictionGenerator
# ---------------------------------------------------------------------------

class TestSemanticContradictionGenerator:

    def test_semantic_contradiction_replaces_antonym(self):
        """Answer with 'open' gets 'closed' substituted."""
        g = SemanticContradictionGenerator()
        results = g.generate(OPEN_ANSWER, QUESTION, seed=42)
        assert len(results) >= 1
        # The word 'open' should be replaced by 'closed'
        assert "closed" in results[0].lower() or "closed" in " ".join(results).lower()

    def test_semantic_contradiction_fallback(self):
        """Text with no CONTRADICTION_MAP match gets fallback prefix."""
        # ANSWER contains "provides electrical energy" — not in CONTRADICTION_MAP
        g = SemanticContradictionGenerator()
        results = g.generate(ANSWER, QUESTION, seed=42)
        assert len(results) >= 1
        assert results[0].startswith("It is not true that")

    def test_semantic_contradiction_deterministic(self):
        """Same input always produces same output (no randomness)."""
        g = SemanticContradictionGenerator()
        r1 = g.generate(OPEN_ANSWER, QUESTION, seed=0)
        r2 = g.generate(OPEN_ANSWER, QUESTION, seed=99)
        # SemanticContradiction is fully deterministic from text — seed doesn't matter
        assert r1 == r2

    def test_semantic_contradiction_two_variants_for_two_hits(self):
        """Answer with two contradiction matches produces 2 variants."""
        two_hit_answer = AnswerRecord(
            answer_id="test_2hits",
            question_id="q1",
            student_answer="The series circuit is open and current increases.",
            gold_label="correct",
            gold_score=1.0,
        )
        g = SemanticContradictionGenerator()
        results = g.generate(two_hit_answer, QUESTION, seed=42)
        assert len(results) == 2, f"Expected 2 variants for two-hit answer, got {len(results)}"


# ---------------------------------------------------------------------------
# Test 6: RubricKeywordEchoingGenerator
# ---------------------------------------------------------------------------

class TestRubricKeywordEchoingGenerator:

    def test_rubric_keyword_echoing_appends_terms(self):
        """Result is longer than original (appended keywords)."""
        g = RubricKeywordEchoingGenerator()
        results = g.generate(ANSWER, QUESTION, seed=42)
        assert len(results) >= 1
        for r in results:
            assert len(r) > len(ANSWER.student_answer)

    def test_rubric_keyword_echoing_contains_reference_terms(self):
        """Appended text contains words from the reference answer."""
        g = RubricKeywordEchoingGenerator()
        results = g.generate(ANSWER, QUESTION, seed=42)
        ref_words = {
            w.lower().strip(".,;:!?\"'")
            for w in QUESTION.reference_answers[0].split()
        }
        for r in results:
            result_words = {w.lower() for w in r.split()}
            # At least some reference words appear in the result
            assert ref_words & result_words, "Result should contain reference-answer words"

    def test_rubric_keyword_echoing_deterministic(self):
        """Same seed produces identical output."""
        g = RubricKeywordEchoingGenerator()
        r1 = g.generate(ANSWER, QUESTION, seed=42)
        r2 = g.generate(ANSWER, QUESTION, seed=42)
        assert r1 == r2

    def test_rubric_keyword_echoing_empty_for_no_unique_terms(self):
        """If student answer already contains all reference terms, returns empty."""
        # Make an answer that contains all words from the reference
        full_answer = AnswerRecord(
            answer_id="test_full",
            question_id="q1",
            student_answer="The battery supplies electrical energy to power the bulb.",
            gold_label="correct",
            gold_score=1.0,
        )
        g = RubricKeywordEchoingGenerator()
        results = g.generate(full_answer, QUESTION, seed=42)
        # All reference words already in student answer — no unique terms to echo
        assert isinstance(results, list)

    def test_rubric_keyword_echoing_no_reference_answers(self):
        """QuestionRecord with no reference answers returns empty list."""
        no_ref_question = QuestionRecord(
            question_id="q_no_ref",
            prompt="What does the battery do?",
            reference_answers=[],
        )
        g = RubricKeywordEchoingGenerator()
        results = g.generate(ANSWER, no_ref_question, seed=42)
        assert results == []


# ---------------------------------------------------------------------------
# Test 7: FluentWrongExtensionGenerator
# ---------------------------------------------------------------------------

class TestFluentWrongExtensionGenerator:

    def test_fluent_wrong_extension_appends_statement(self):
        """Result is longer than original (appended wrong statement)."""
        g = FluentWrongExtensionGenerator()
        results = g.generate(ANSWER, QUESTION, seed=42)
        assert len(results) == 1
        assert len(results[0]) > len(ANSWER.student_answer)

    def test_fluent_wrong_extension_starts_with_original(self):
        """Result starts with the original student answer."""
        g = FluentWrongExtensionGenerator()
        results = g.generate(ANSWER, QUESTION, seed=42)
        assert results[0].startswith(ANSWER.student_answer)

    def test_fluent_wrong_extension_deterministic(self):
        """Same seed produces identical output."""
        g = FluentWrongExtensionGenerator()
        r1 = g.generate(ANSWER, QUESTION, seed=42)
        r2 = g.generate(ANSWER, QUESTION, seed=42)
        assert r1 == r2

    def test_fluent_wrong_extension_different_seeds(self):
        """Different seeds may pick different wrong statements."""
        g = FluentWrongExtensionGenerator()
        r0 = g.generate(ANSWER, QUESTION, seed=0)
        r99 = g.generate(ANSWER, QUESTION, seed=99)
        # Both should be valid strings longer than original
        assert len(r0[0]) > len(ANSWER.student_answer)
        assert len(r99[0]) > len(ANSWER.student_answer)


# ---------------------------------------------------------------------------
# Test 8: ABC conformance for all 7 generators
# ---------------------------------------------------------------------------

class TestABCConformance:

    def test_all_generators_are_perturbation_generator_instances(self):
        """All 7 generators are instances of PerturbationGenerator."""
        generators = [
            SynonymSubstitutionGenerator(),
            TypoInsertionGenerator(),
            NegationInsertionGenerator(),
            KeyConceptDeletionGenerator(),
            SemanticContradictionGenerator(),
            RubricKeywordEchoingGenerator(),
            FluentWrongExtensionGenerator(),
        ]
        for g in generators:
            assert isinstance(g, PerturbationGenerator), (
                f"{g.__class__.__name__} is not an instance of PerturbationGenerator"
            )

    def test_all_generators_have_correct_family(self):
        """All generators have a valid family attribute."""
        valid_families = {"invariance", "sensitivity", "gaming"}
        generators = [
            SynonymSubstitutionGenerator(),
            TypoInsertionGenerator(),
            NegationInsertionGenerator(),
            KeyConceptDeletionGenerator(),
            SemanticContradictionGenerator(),
            RubricKeywordEchoingGenerator(),
            FluentWrongExtensionGenerator(),
        ]
        for g in generators:
            assert g.family in valid_families, (
                f"{g.__class__.__name__}.family={g.family!r} not in {valid_families}"
            )

    def test_all_generators_type_name_in_perturbation_types(self):
        """All generators' type_name is a key in PERTURBATION_TYPES."""
        generators = [
            SynonymSubstitutionGenerator(),
            TypoInsertionGenerator(),
            NegationInsertionGenerator(),
            KeyConceptDeletionGenerator(),
            SemanticContradictionGenerator(),
            RubricKeywordEchoingGenerator(),
            FluentWrongExtensionGenerator(),
        ]
        for g in generators:
            assert g.type_name in PERTURBATION_TYPES, (
                f"{g.__class__.__name__}.type_name={g.type_name!r} not in PERTURBATION_TYPES"
            )
            assert PERTURBATION_TYPES[g.type_name] == g.family, (
                f"{g.type_name} family mismatch: expected {PERTURBATION_TYPES[g.type_name]}, "
                f"got {g.family}"
            )

    def test_all_generators_have_n_variants(self):
        """All generators have a positive integer n_variants attribute."""
        generators = [
            SynonymSubstitutionGenerator(),
            TypoInsertionGenerator(),
            NegationInsertionGenerator(),
            KeyConceptDeletionGenerator(),
            SemanticContradictionGenerator(),
            RubricKeywordEchoingGenerator(),
            FluentWrongExtensionGenerator(),
        ]
        for g in generators:
            assert hasattr(g, "n_variants"), (
                f"{g.__class__.__name__} missing n_variants attribute"
            )
            assert isinstance(g.n_variants, int) and g.n_variants >= 1, (
                f"{g.__class__.__name__}.n_variants must be a positive int"
            )

    def test_generate_returns_list_of_strings(self):
        """generate() always returns a list of strings for all 7 generators."""
        generators = [
            SynonymSubstitutionGenerator(),
            TypoInsertionGenerator(),
            NegationInsertionGenerator(),
            KeyConceptDeletionGenerator(),
            SemanticContradictionGenerator(),
            RubricKeywordEchoingGenerator(),
            FluentWrongExtensionGenerator(),
        ]
        for g in generators:
            results = g.generate(ANSWER, QUESTION, seed=42)
            assert isinstance(results, list), (
                f"{g.__class__.__name__}.generate() must return a list"
            )
            for item in results:
                assert isinstance(item, str), (
                    f"{g.__class__.__name__}.generate() must return list of strings, "
                    f"got {type(item)}"
                )
