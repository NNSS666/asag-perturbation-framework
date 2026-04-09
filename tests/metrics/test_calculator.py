"""
Gold unit tests for MetricCalculator — all four dual-form metric variants.

Every test uses hand-computed expected values documented in synthetic_mini_dataset.py.
All assertions use pytest.approx(expected, abs=1e-9) to allow only rounding differences
at the 9th decimal place — no tolerance relaxation beyond strict mathematical equality.

See tests/metrics/synthetic_mini_dataset.py for the full step-by-step derivation
of every expected value used in these tests.
"""

from typing import List, Tuple

import pytest

from asag.metrics import MetricCalculator
from tests.metrics.synthetic_mini_dataset import (
    EXPECTED_ASR_THRESHOLDED_ALL,
    EXPECTED_BY_TYPE_GAMING,
    EXPECTED_BY_TYPE_INVARIANCE,
    EXPECTED_BY_TYPE_SENSITIVITY,
    EXPECTED_IVR_ABSDELTA_ALL,
    EXPECTED_IVR_FLIP_ALL,
    EXPECTED_SSR_DIRECTIONAL_ALL,
)

# ---------------------------------------------------------------------------
# Module-level fixture: shared calculator instance
# ---------------------------------------------------------------------------

@pytest.fixture
def calc() -> MetricCalculator:
    """Shared MetricCalculator instance for all tests."""
    return MetricCalculator()


# ---------------------------------------------------------------------------
# Gold tests — IVR_flip
# ---------------------------------------------------------------------------

def test_ivr_flip_gold(calc, invariance_pairs):
    """Test IVR_flip aggregate across all 30 invariance pairs.

    Derivation (from synthetic_mini_dataset.py module docstring):
      Total pairs: 30 (15 answers x 2 invariance types)
      Flips (orig != pert after rounding to 6 decimals):
        A0-inv2: 1.0->0.5  [1]
        A2-inv2: 0.5->0.0  [2]
        A4-inv1: 1.0->0.5  [3]
        A6-inv1: 0.5->0.0  [4]
        A7-inv2: 1.0->0.5  [5]
        A12-inv1: 1.0->0.5 [6]
        A12-inv2: 1.0->0.5 [7]
        A13-inv2: 0.5->0.0 [8]
        A14-inv2: 1.0->0.5 [9]
      Total flips: 9
      IVR_flip = 9/30 = 0.3
    """
    result = calc.ivr_flip(invariance_pairs)
    assert result == pytest.approx(EXPECTED_IVR_FLIP_ALL, abs=1e-9)
    assert result == pytest.approx(0.3, abs=1e-9)


# ---------------------------------------------------------------------------
# Gold tests — IVR_absdelta
# ---------------------------------------------------------------------------

def test_ivr_absdelta_gold(calc, invariance_pairs):
    """Test IVR_absdelta aggregate across all 30 invariance pairs.

    Derivation (from synthetic_mini_dataset.py module docstring):
      Total pairs: 30 (15 answers x 2 invariance types)
      |orig - pert| for each pair (non-zero pairs only):
        A0-inv2:  |1.0 - 0.5| = 0.5
        A2-inv2:  |0.5 - 0.0| = 0.5
        A4-inv1:  |1.0 - 0.5| = 0.5
        A6-inv1:  |0.5 - 0.0| = 0.5
        A7-inv2:  |1.0 - 0.5| = 0.5
        A12-inv1: |1.0 - 0.5| = 0.5
        A12-inv2: |1.0 - 0.5| = 0.5
        A13-inv2: |0.5 - 0.0| = 0.5
        A14-inv2: |1.0 - 0.5| = 0.5
      Sum of deltas: 9 x 0.5 = 4.5
      IVR_absdelta = 4.5 / 30 = 0.15
    """
    result = calc.ivr_absdelta(invariance_pairs)
    assert result == pytest.approx(EXPECTED_IVR_ABSDELTA_ALL, abs=1e-9)
    assert result == pytest.approx(0.15, abs=1e-9)


# ---------------------------------------------------------------------------
# Gold tests — SSR_directional
# ---------------------------------------------------------------------------

def test_ssr_directional_gold(calc, sensitivity_pairs):
    """Test SSR_directional aggregate across all 30 sensitivity pairs.

    Derivation (from synthetic_mini_dataset.py module docstring):
      Total pairs: 30 (15 answers x 2 sensitivity types)
      Failures (pert >= orig — no decrease detected):
        A3-sen1: (0.0, 0.0) -> equal, no decrease -> FAILURE
        A3-sen2: (0.0, 0.0) -> equal, no decrease -> FAILURE
        A8-sen1: (0.0, 0.0) -> equal, no decrease -> FAILURE
        A8-sen2: (0.0, 0.0) -> equal, no decrease -> FAILURE
        A11-sen1: (0.0, 0.0) -> equal, no decrease -> FAILURE
        A11-sen2: (0.0, 0.0) -> equal, no decrease -> FAILURE
      Failures: 6 (answers already at 0.0 — can't decrease further)
      Successes: 30 - 6 = 24
      SSR_directional = 24/30 = 0.8
    """
    result = calc.ssr_directional(sensitivity_pairs)
    assert result == pytest.approx(EXPECTED_SSR_DIRECTIONAL_ALL, abs=1e-9)
    assert result == pytest.approx(0.8, abs=1e-9)


# ---------------------------------------------------------------------------
# Gold tests — ASR_thresholded
# ---------------------------------------------------------------------------

def test_asr_thresholded_gold(calc, gaming_pairs):
    """Test ASR_thresholded aggregate across all 15 gaming pairs.

    Derivation (from synthetic_mini_dataset.py module docstring):
      Total pairs: 15 (15 answers x 1 gaming type)
      Criterion: orig < 0.5 AND pert >= 0.5
      Crossings:
        A3-gam1:  (0.0, 0.5)  -> 0.0 < 0.5 AND 0.5 >= 0.5 -> CROSSING [1]
        A8-gam1:  (0.0, 1.0)  -> 0.0 < 0.5 AND 1.0 >= 0.5 -> CROSSING [2]
        A11-gam1: (0.0, 0.5)  -> 0.0 < 0.5 AND 0.5 >= 0.5 -> CROSSING [3]
      Non-crossings:
        A0,A1,A4,A5,A7,A10,A12,A14: orig=1.0 (already passing) -> no crossing
        A2,A6,A9,A13: orig=0.5 (at threshold, NOT below) -> no crossing
        A6-gam1:  (0.5, 0.0)  -> orig=0.5 not below threshold -> no crossing
        A9-gam1:  (0.5, 0.0)  -> orig=0.5 not below threshold -> no crossing
      Crossings: 3/15
      ASR_thresholded = 3/15 = 0.2
    """
    result = calc.asr_thresholded(gaming_pairs)
    assert result == pytest.approx(EXPECTED_ASR_THRESHOLDED_ALL, abs=1e-9)
    assert result == pytest.approx(0.2, abs=1e-9)


# ---------------------------------------------------------------------------
# Edge case tests — empty input returns NaN
# ---------------------------------------------------------------------------

def test_empty_returns_none(calc):
    """All four metric methods return None on empty input.

    None (not 0.0) is the correct return value for empty input to distinguish
    'no pairs evaluated' from 'all pairs passed the criterion'. Returning 0.0
    would be misleading — it would look like all invariance perturbations caused
    violations, or no sensitivity perturbations succeeded.
    """
    assert calc.ivr_flip([]) is None
    assert calc.ivr_absdelta([]) is None
    assert calc.ssr_directional([]) is None
    assert calc.asr_thresholded([]) is None


# ---------------------------------------------------------------------------
# Edge case tests — behavioral correctness
# ---------------------------------------------------------------------------

def test_asr_already_passing_not_counted(calc):
    """Explicit test that already-passing answers are NOT counted in ASR.

    Scenario: orig=0.5 (AT the threshold) increases to 1.0.
    This is NOT an adversarial crossing because orig was not BELOW the threshold.
    The criterion requires orig < 0.5, not orig <= 0.5.

    Similarly: orig=0.5 increases to 0.5 — still not below threshold.

    Derivation:
      pairs = [(0.5, 1.0), (0.5, 0.5), (1.0, 1.0)]
      Criterion: orig < 0.5 AND pert >= 0.5
      (0.5, 1.0): 0.5 < 0.5 -> False (not below threshold)
      (0.5, 0.5): 0.5 < 0.5 -> False (not below threshold)
      (1.0, 1.0): 1.0 < 0.5 -> False (not below threshold)
      Crossings: 0/3 = 0.0
    """
    pairs = [(0.5, 1.0), (0.5, 0.5), (1.0, 1.0)]
    result = calc.asr_thresholded(pairs)
    assert result == pytest.approx(0.0, abs=1e-9)


def test_ssr_no_change_is_failure(calc):
    """Explicit test that no score change in sensitivity perturbation counts as failure.

    RESEARCH.md Pitfall 6: SSR_directional requires STRICT decrease (pert < orig).
    A sensitivity perturbation that leaves the score unchanged means the grader
    did NOT detect the perturbation — this is a negative result, counted as failure.

    Derivation:
      pairs = [(1.0, 1.0), (0.5, 0.5), (0.0, 0.0), (1.0, 0.0)]
      Criterion: pert < orig (strict less-than)
      (1.0, 1.0): 1.0 < 1.0 -> False (no change = failure)
      (0.5, 0.5): 0.5 < 0.5 -> False (no change = failure)
      (0.0, 0.0): 0.0 < 0.0 -> False (no change = failure)
      (1.0, 0.0): 0.0 < 1.0 -> True  (success)
      Successes: 1/4 = 0.25
    """
    pairs = [(1.0, 1.0), (0.5, 0.5), (0.0, 0.0), (1.0, 0.0)]
    result = calc.ssr_directional(pairs)
    assert result == pytest.approx(0.25, abs=1e-9)


# ---------------------------------------------------------------------------
# Per-type breakdown tests — invariance
# ---------------------------------------------------------------------------

def test_compute_by_type_invariance(calc, grade_pairs_for_by_type):
    """Test per-perturbation-type breakdown for invariance family.

    Filters grade_pairs to invariance types (synonym_substitution, surface_rewrite)
    and verifies that each type has different IVR values, confirming the breakdown
    correctly separates perturbation types.

    Derivation for synonym_substitution (15 pairs, inv1 column):
      Flips: A4(1.0->0.5), A6(0.5->0.0), A12(1.0->0.5) = 3 flips
      IVR_flip = 3/15 = 0.2
      Deltas: 0.5 + 0.5 + 0.5 = 1.5
      IVR_absdelta = 1.5/15 = 0.1

    Derivation for surface_rewrite (15 pairs, inv2 column):
      Flips: A0(1.0->0.5), A2(0.5->0.0), A7(1.0->0.5), A12(1.0->0.5),
             A13(0.5->0.0), A14(1.0->0.5) = 6 flips
      IVR_flip = 6/15 = 0.4
      Deltas: 6 x 0.5 = 3.0
      IVR_absdelta = 3.0/15 = 0.2

    The two types have DIFFERENT IVR_flip values (0.2 vs 0.4), confirming
    per-type breakdown provides signal beyond the aggregate.
    """
    inv_pairs = [t for t in grade_pairs_for_by_type
                 if t[1] in ("synonym_substitution", "surface_rewrite")]
    result = calc.compute_by_type(inv_pairs, "invariance")

    assert set(result.keys()) == {"synonym_substitution", "surface_rewrite"}

    # synonym_substitution
    syn = result["synonym_substitution"]
    assert syn["ivr_flip"] == pytest.approx(
        EXPECTED_BY_TYPE_INVARIANCE["synonym_substitution"]["ivr_flip"], abs=1e-9
    )
    assert syn["ivr_absdelta"] == pytest.approx(
        EXPECTED_BY_TYPE_INVARIANCE["synonym_substitution"]["ivr_absdelta"], abs=1e-9
    )
    assert syn["ivr_flip"] == pytest.approx(0.2, abs=1e-9)
    assert syn["ivr_absdelta"] == pytest.approx(0.1, abs=1e-9)

    # surface_rewrite
    surf = result["surface_rewrite"]
    assert surf["ivr_flip"] == pytest.approx(
        EXPECTED_BY_TYPE_INVARIANCE["surface_rewrite"]["ivr_flip"], abs=1e-9
    )
    assert surf["ivr_absdelta"] == pytest.approx(
        EXPECTED_BY_TYPE_INVARIANCE["surface_rewrite"]["ivr_absdelta"], abs=1e-9
    )
    assert surf["ivr_flip"] == pytest.approx(0.4, abs=1e-9)
    assert surf["ivr_absdelta"] == pytest.approx(0.2, abs=1e-9)

    # Verify they differ (the breakdown adds information)
    assert result["surface_rewrite"]["ivr_flip"] != pytest.approx(
        result["synonym_substitution"]["ivr_flip"], abs=1e-9
    )


def test_compute_by_type_sensitivity(calc, grade_pairs_for_by_type):
    """Test per-perturbation-type breakdown for sensitivity family.

    Filters grade_pairs to sensitivity types (negation_insertion, key_concept_deletion)
    and verifies SSR_directional values.

    Derivation for negation_insertion (15 pairs, sen1 column):
      Failures (no decrease): A3(0.0->0.0), A8(0.0->0.0), A11(0.0->0.0) = 3 failures
      Successes: 15 - 3 = 12
      SSR_directional = 12/15 = 0.8

    Derivation for key_concept_deletion (15 pairs, sen2 column):
      Failures (no decrease): A3(0.0->0.0), A8(0.0->0.0), A11(0.0->0.0) = 3 failures
      Successes: 15 - 3 = 12
      SSR_directional = 12/15 = 0.8
    """
    sen_pairs = [t for t in grade_pairs_for_by_type
                 if t[1] in ("negation_insertion", "key_concept_deletion")]
    result = calc.compute_by_type(sen_pairs, "sensitivity")

    assert set(result.keys()) == {"negation_insertion", "key_concept_deletion"}

    assert result["negation_insertion"]["ssr_directional"] == pytest.approx(
        EXPECTED_BY_TYPE_SENSITIVITY["negation_insertion"]["ssr_directional"], abs=1e-9
    )
    assert result["negation_insertion"]["ssr_directional"] == pytest.approx(0.8, abs=1e-9)

    assert result["key_concept_deletion"]["ssr_directional"] == pytest.approx(
        EXPECTED_BY_TYPE_SENSITIVITY["key_concept_deletion"]["ssr_directional"], abs=1e-9
    )
    assert result["key_concept_deletion"]["ssr_directional"] == pytest.approx(0.8, abs=1e-9)

    # verify only ssr_directional key is present (not ivr or asr keys)
    assert "ivr_flip" not in result["negation_insertion"]
    assert "asr_thresholded" not in result["negation_insertion"]


def test_compute_by_type_gaming(calc, grade_pairs_for_by_type):
    """Test per-perturbation-type breakdown for gaming family.

    Filters grade_pairs to gaming type (keyword_spam) and verifies
    ASR_thresholded value.

    Derivation for keyword_spam (15 pairs, gam1 column):
      Crossings (orig < 0.5 AND pert >= 0.5):
        A3-gam1:  (0.0, 0.5)  -> CROSSING [1]
        A8-gam1:  (0.0, 1.0)  -> CROSSING [2]
        A11-gam1: (0.0, 0.5)  -> CROSSING [3]
      ASR_thresholded = 3/15 = 0.2
    """
    gam_pairs = [t for t in grade_pairs_for_by_type if t[1] == "keyword_spam"]
    result = calc.compute_by_type(gam_pairs, "gaming")

    assert set(result.keys()) == {"keyword_spam"}

    assert result["keyword_spam"]["asr_thresholded"] == pytest.approx(
        EXPECTED_BY_TYPE_GAMING["keyword_spam"]["asr_thresholded"], abs=1e-9
    )
    assert result["keyword_spam"]["asr_thresholded"] == pytest.approx(0.2, abs=1e-9)

    # verify only asr_thresholded key is present
    assert "ivr_flip" not in result["keyword_spam"]
    assert "ssr_directional" not in result["keyword_spam"]


# ---------------------------------------------------------------------------
# Additional correctness tests — small hand-verified examples
# ---------------------------------------------------------------------------

def test_ivr_flip_simple(calc):
    """Minimal IVR_flip test with a hand-verifiable 4-pair example.

    Derivation:
      pairs = [(1.0, 1.0), (1.0, 0.5), (0.5, 0.5), (0.0, 0.5)]
      Flips: (1.0, 0.5) -> True, (0.0, 0.5) -> True
      IVR_flip = 2/4 = 0.5
    """
    pairs = [(1.0, 1.0), (1.0, 0.5), (0.5, 0.5), (0.0, 0.5)]
    assert calc.ivr_flip(pairs) == pytest.approx(0.5, abs=1e-9)


def test_ivr_absdelta_simple(calc):
    """Minimal IVR_absdelta test with a hand-verifiable 3-pair example.

    Derivation:
      pairs = [(1.0, 0.0), (0.5, 0.5), (0.0, 0.0)]
      Deltas: 1.0, 0.0, 0.0
      IVR_absdelta = 1.0 / 3 ≈ 0.3333...
    """
    pairs = [(1.0, 0.0), (0.5, 0.5), (0.0, 0.0)]
    assert calc.ivr_absdelta(pairs) == pytest.approx(1.0 / 3, abs=1e-9)


def test_asr_threshold_boundary(calc):
    """Explicit boundary test: orig=0.5 is NOT below threshold, orig=0.0 IS.

    This tests the strict less-than criterion: orig < PASSING_THRESHOLD (0.5).
    At-threshold answers are considered passing — they should not be counted
    as successful adversarial gaming even if their score increases.

    Derivation:
      pairs = [(0.0, 0.5), (0.5, 1.0), (0.4999, 0.5)]
      PASSING_THRESHOLD = 0.5
      (0.0, 0.5):    0.0 < 0.5 AND 0.5 >= 0.5 -> CROSSING [1]
      (0.5, 1.0):    0.5 < 0.5 -> False (AT threshold, not below)
      (0.4999, 0.5): 0.4999 < 0.5 AND 0.5 >= 0.5 -> CROSSING [2]
      ASR = 2/3 ≈ 0.6667
    """
    pairs = [(0.0, 0.5), (0.5, 1.0), (0.4999, 0.5)]
    result = calc.asr_thresholded(pairs)
    assert result == pytest.approx(2 / 3, abs=1e-9)
