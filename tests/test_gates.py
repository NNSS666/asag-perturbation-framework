"""
Unit tests for Gate 1 (SBERT cosine) and Gate 2 (negation/antonym heuristic).

Tests verify:
  - Gate 1 correctly bypasses non-synonym-substitution types
  - Gate 1 correctly accepts high-similarity candidates and rejects low-similarity ones
  - Gate 2 correctly bypasses non-invariance types
  - Gate 2 blocks new negation markers and new antonyms
  - Gate 2 does NOT block pre-existing negation/antonyms in the original
  - GateLog tracks tested/rejected counts and computes rejection rates correctly

Run: PYTHONPATH=src python3 -m pytest tests/test_gates.py -v

Note: Gate 1 tests require loading a SentenceTransformer model (~20s).
      The model is loaded once per session using module-scoped fixture.
"""

import pytest
from collections import defaultdict
from sentence_transformers import SentenceTransformer

from asag.perturbations.gates import (
    gate_1_sbert,
    gate_2_negation,
    GateLog,
    GATE1_THRESHOLD,
    NEGATION_PATTERN,
    ANTONYM_MAP,
)


# ---------------------------------------------------------------------------
# Module-scoped encoder fixture — loads SentenceTransformer once for all tests
# (avoids ~20s reload per test, mirrors HybridGrader test pattern from Phase 2)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def encoder():
    """Load all-MiniLM-L6-v2 once for the entire test module."""
    return SentenceTransformer("all-MiniLM-L6-v2")


@pytest.fixture
def fresh_log():
    """Return a new GateLog for each test that needs one."""
    return GateLog()


# ---------------------------------------------------------------------------
# Test constants
# ---------------------------------------------------------------------------

ORIGINAL = "The battery provides electrical energy to the circuit."
SIMILAR = "The battery supplies electrical energy to the circuit."    # high similarity
DIFFERENT = "Photosynthesis converts sunlight into glucose in leaves."  # low similarity


# ---------------------------------------------------------------------------
# Gate 1 tests
# ---------------------------------------------------------------------------

class TestGate1SBERT:

    def test_gate1_threshold_is_085(self):
        """GATE1_THRESHOLD must be exactly 0.85."""
        assert GATE1_THRESHOLD == 0.85

    def test_gate1_passes_similar_text(self, encoder, fresh_log):
        """Synonym substitution with high similarity passes Gate 1."""
        result = gate_1_sbert(ORIGINAL, SIMILAR, "synonym_substitution", encoder, fresh_log)
        assert result is True

    def test_gate1_rejects_dissimilar_text(self, encoder, fresh_log):
        """Completely different text is rejected by Gate 1."""
        result = gate_1_sbert(ORIGINAL, DIFFERENT, "synonym_substitution", encoder, fresh_log)
        # DIFFERENT is a completely unrelated sentence — should fail threshold
        assert result is False

    def test_gate1_skips_typo_insertion(self, encoder, fresh_log):
        """typo_insertion always passes Gate 1 regardless of text similarity."""
        result = gate_1_sbert(ORIGINAL, DIFFERENT, "typo_insertion", encoder, fresh_log)
        assert result is True, "typo_insertion must bypass Gate 1"

    def test_gate1_skips_negation_insertion(self, encoder, fresh_log):
        """negation_insertion always passes Gate 1."""
        result = gate_1_sbert(ORIGINAL, DIFFERENT, "negation_insertion", encoder, fresh_log)
        assert result is True

    def test_gate1_skips_key_concept_deletion(self, encoder, fresh_log):
        """key_concept_deletion always passes Gate 1."""
        result = gate_1_sbert(ORIGINAL, DIFFERENT, "key_concept_deletion", encoder, fresh_log)
        assert result is True

    def test_gate1_skips_semantic_contradiction(self, encoder, fresh_log):
        """semantic_contradiction always passes Gate 1."""
        result = gate_1_sbert(ORIGINAL, DIFFERENT, "semantic_contradiction", encoder, fresh_log)
        assert result is True

    def test_gate1_skips_rubric_keyword_echoing(self, encoder, fresh_log):
        """rubric_keyword_echoing always passes Gate 1."""
        result = gate_1_sbert(ORIGINAL, DIFFERENT, "rubric_keyword_echoing", encoder, fresh_log)
        assert result is True

    def test_gate1_skips_fluent_wrong_extension(self, encoder, fresh_log):
        """fluent_wrong_extension always passes Gate 1."""
        result = gate_1_sbert(ORIGINAL, DIFFERENT, "fluent_wrong_extension", encoder, fresh_log)
        assert result is True

    def test_gate1_logs_tested_count_for_synonym_substitution(self, encoder, fresh_log):
        """Gate 1 increments tested count for synonym_substitution."""
        assert fresh_log.gate1_tested_by_type["synonym_substitution"] == 0
        gate_1_sbert(ORIGINAL, SIMILAR, "synonym_substitution", encoder, fresh_log)
        assert fresh_log.gate1_tested_by_type["synonym_substitution"] == 1

    def test_gate1_logs_rejected_count_on_rejection(self, encoder, fresh_log):
        """Gate 1 increments rejected count when candidate is rejected."""
        gate_1_sbert(ORIGINAL, DIFFERENT, "synonym_substitution", encoder, fresh_log)
        assert fresh_log.gate1_rejected_by_type["synonym_substitution"] == 1

    def test_gate1_does_not_log_for_bypassed_types(self, encoder, fresh_log):
        """Gate 1 does NOT increment tested count for bypassed types."""
        gate_1_sbert(ORIGINAL, DIFFERENT, "typo_insertion", encoder, fresh_log)
        gate_1_sbert(ORIGINAL, DIFFERENT, "negation_insertion", encoder, fresh_log)
        assert fresh_log.gate1_tested_by_type["typo_insertion"] == 0
        assert fresh_log.gate1_tested_by_type["negation_insertion"] == 0

    def test_gate1_multiple_calls_accumulate(self, encoder, fresh_log):
        """Multiple Gate 1 calls accumulate in the same log."""
        gate_1_sbert(ORIGINAL, SIMILAR, "synonym_substitution", encoder, fresh_log)
        gate_1_sbert(ORIGINAL, SIMILAR, "synonym_substitution", encoder, fresh_log)
        gate_1_sbert(ORIGINAL, DIFFERENT, "synonym_substitution", encoder, fresh_log)
        assert fresh_log.gate1_tested_by_type["synonym_substitution"] == 3
        # Third call (DIFFERENT) should be rejected
        assert fresh_log.gate1_rejected_by_type["synonym_substitution"] >= 1


# ---------------------------------------------------------------------------
# Gate 2 tests
# ---------------------------------------------------------------------------

class TestGate2Negation:

    def test_gate2_blocks_new_negation_in_candidate(self, fresh_log):
        """Candidate with 'not' (not in original) is blocked."""
        original = "The circuit is complete."
        candidate = "The circuit is not complete."
        result = gate_2_negation(original, candidate, "synonym_substitution", fresh_log)
        assert result is False, "New negation 'not' should block the candidate"

    def test_gate2_allows_candidate_when_negation_in_original(self, fresh_log):
        """Candidate with 'not' is NOT blocked if original already had 'not'."""
        original = "The circuit is not complete."
        candidate = "The circuit is not finished."
        result = gate_2_negation(original, candidate, "synonym_substitution", fresh_log)
        assert result is True, "Pre-existing negation should NOT trigger Gate 2 rejection"

    def test_gate2_blocks_never_in_candidate(self, fresh_log):
        """Candidate with 'never' (not in original) is blocked."""
        original = "Current flows through the wire."
        candidate = "Current never flows through the wire."
        result = gate_2_negation(original, candidate, "synonym_substitution", fresh_log)
        assert result is False

    def test_gate2_blocks_new_antonym_in_candidate(self, fresh_log):
        """Candidate with 'closed' when original had 'open' is blocked."""
        original = "The switch is open and current flows."
        candidate = "The switch is closed and current flows."
        result = gate_2_negation(original, candidate, "synonym_substitution", fresh_log)
        assert result is False, "'closed' is an antonym value introduced by perturbation"

    def test_gate2_allows_same_antonym_in_both(self, fresh_log):
        """Candidate with 'negative' is NOT blocked when original also had 'negative'."""
        original = "The negative charge flows through the wire."
        candidate = "The negative current flows through the wire."
        result = gate_2_negation(original, candidate, "synonym_substitution", fresh_log)
        assert result is True, (
            "'negative' appears in both original and candidate — should NOT trigger rejection"
        )

    def test_gate2_passes_clean_synonym(self, fresh_log):
        """Synonym that introduces no new negation or antonym passes Gate 2."""
        original = "The battery provides electrical energy to the circuit."
        candidate = "The battery supplies electrical energy to the circuit."
        result = gate_2_negation(original, candidate, "synonym_substitution", fresh_log)
        assert result is True

    def test_gate2_skips_negation_insertion_type(self, fresh_log):
        """negation_insertion type always passes Gate 2 (not invariance family)."""
        original = "The circuit is complete."
        candidate = "The circuit is not complete."
        result = gate_2_negation(original, candidate, "negation_insertion", fresh_log)
        assert result is True, "Gate 2 does not apply to sensitivity types"

    def test_gate2_skips_key_concept_deletion_type(self, fresh_log):
        """key_concept_deletion type always passes Gate 2."""
        result = gate_2_negation(
            "The battery provides energy.",
            "The battery provides.",
            "key_concept_deletion",
            fresh_log,
        )
        assert result is True

    def test_gate2_skips_gaming_types(self, fresh_log):
        """Gaming types always pass Gate 2."""
        original = "The battery provides energy."
        candidate = "The battery provides energy not ever."
        for gaming_type in ["rubric_keyword_echoing", "fluent_wrong_extension"]:
            log = GateLog()
            result = gate_2_negation(original, candidate, gaming_type, log)
            assert result is True, f"Gate 2 should not apply to {gaming_type}"

    def test_gate2_applies_to_typo_insertion(self, fresh_log):
        """Gate 2 does apply to typo_insertion (invariance family)."""
        original = "The circuit is complete."
        candidate = "The circuut is not complete."  # typo + new negation
        result = gate_2_negation(original, candidate, "typo_insertion", fresh_log)
        assert result is False, "typo_insertion with new negation should be blocked by Gate 2"

    def test_gate2_logs_tested_count_for_invariance_types(self, fresh_log):
        """Gate 2 increments tested count for invariance family types."""
        gate_2_negation(ORIGINAL, SIMILAR, "synonym_substitution", fresh_log)
        gate_2_negation(ORIGINAL, SIMILAR, "typo_insertion", fresh_log)
        assert fresh_log.gate2_tested_by_type["synonym_substitution"] == 1
        assert fresh_log.gate2_tested_by_type["typo_insertion"] == 1

    def test_gate2_does_not_log_for_non_invariance_types(self, fresh_log):
        """Gate 2 does NOT log for non-invariance types."""
        gate_2_negation(ORIGINAL, SIMILAR, "negation_insertion", fresh_log)
        gate_2_negation(ORIGINAL, SIMILAR, "key_concept_deletion", fresh_log)
        assert fresh_log.gate2_tested_by_type["negation_insertion"] == 0
        assert fresh_log.gate2_tested_by_type["key_concept_deletion"] == 0


# ---------------------------------------------------------------------------
# GateLog tests
# ---------------------------------------------------------------------------

class TestGateLog:

    def test_gatelog_default_counters_are_zero(self):
        """Freshly created GateLog has all zero counters."""
        log = GateLog()
        assert log.gate1_tested_by_type["synonym_substitution"] == 0
        assert log.gate1_rejected_by_type["synonym_substitution"] == 0
        assert log.gate2_tested_by_type["typo_insertion"] == 0
        assert log.gate2_rejected_by_type["typo_insertion"] == 0

    def test_gatelog_rejection_rates_empty_for_untested(self):
        """rejection_rates() excludes types with zero tested count."""
        log = GateLog()
        rates = log.rejection_rates()
        assert rates == {"gate1": {}, "gate2": {}}

    def test_gatelog_rejection_rates_correct_calculation(self):
        """Rejection rates are computed correctly."""
        log = GateLog()
        # Simulate: 3 tested, 1 rejected for gate1 synonym_substitution
        log.gate1_tested_by_type["synonym_substitution"] = 3
        log.gate1_rejected_by_type["synonym_substitution"] = 1
        # Simulate: 4 tested, 2 rejected for gate2 typo_insertion
        log.gate2_tested_by_type["typo_insertion"] = 4
        log.gate2_rejected_by_type["typo_insertion"] = 2

        rates = log.rejection_rates()
        assert abs(rates["gate1"]["synonym_substitution"] - 1/3) < 1e-9
        assert abs(rates["gate2"]["typo_insertion"] - 0.5) < 1e-9

    def test_gatelog_rejection_rates_division_by_zero_protection(self):
        """Types with zero tested count do not appear in rejection_rates output."""
        log = GateLog()
        log.gate1_tested_by_type["synonym_substitution"] = 0
        log.gate1_rejected_by_type["synonym_substitution"] = 0
        rates = log.rejection_rates()
        assert "synonym_substitution" not in rates["gate1"]

    def test_gatelog_zero_rejection_rate(self):
        """A type with tests but no rejections has rate 0.0."""
        log = GateLog()
        log.gate1_tested_by_type["synonym_substitution"] = 5
        log.gate1_rejected_by_type["synonym_substitution"] = 0
        rates = log.rejection_rates()
        assert rates["gate1"]["synonym_substitution"] == 0.0

    def test_gatelog_full_rejection_rate(self):
        """A type where all tests are rejected has rate 1.0."""
        log = GateLog()
        log.gate2_tested_by_type["synonym_substitution"] = 3
        log.gate2_rejected_by_type["synonym_substitution"] = 3
        rates = log.rejection_rates()
        assert rates["gate2"]["synonym_substitution"] == 1.0

    def test_gatelog_accumulates_across_calls(self, encoder, fresh_log):
        """GateLog accumulates counts across multiple gate calls."""
        # Call gate 1 twice for synonym substitution
        gate_1_sbert(ORIGINAL, SIMILAR, "synonym_substitution", encoder, fresh_log)
        gate_1_sbert(ORIGINAL, DIFFERENT, "synonym_substitution", encoder, fresh_log)
        assert fresh_log.gate1_tested_by_type["synonym_substitution"] == 2
        # Call gate 2 twice for synonym substitution
        gate_2_negation(ORIGINAL, SIMILAR, "synonym_substitution", fresh_log)
        gate_2_negation(ORIGINAL, SIMILAR, "synonym_substitution", fresh_log)
        assert fresh_log.gate2_tested_by_type["synonym_substitution"] == 2
