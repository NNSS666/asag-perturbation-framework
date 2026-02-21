"""
Synthetic mini-dataset for MetricCalculator gold unit tests.

DESIGN RATIONALE
================
This module provides a synthetic dataset and pre-computed expected values used
to verify correctness of all four dual-form metric variants. All expected values
are derived from hand calculations documented step-by-step in the fixtures and
module docstring, making this a thesis-ready verification artifact.

DATASET STRUCTURE
=================
- 3 questions (Q1, Q2, Q3)
- 5 student answers per question = 15 AnswerRecords
- Per answer: 5 perturbations (2 invariance + 2 sensitivity + 1 gaming) = 75 PerturbationRecords

PERTURBATION TYPES USED
=======================
Invariance:  "synonym_substitution" (inv1), "surface_rewrite" (inv2)
Sensitivity: "negation_insertion"   (sen1), "key_concept_deletion" (sen2)
Gaming:      "keyword_spam"         (gam1)

GRADE SCALE (IEEE 754 exact)
============================
correct   = 1.0
partial   = 0.5
incorrect = 0.0

MOCK GRADES MATRIX
==================
Mock grades simulate what a grader would assign to each original and perturbed
answer. The original score is the answer's gold_score. Perturbed scores are
fixed values chosen to produce known expected metric values.

For each answer A_i (i=0..14), the mock grade tuple is:
(orig_score, inv1_score, inv2_score, sen1_score, sen2_score, gam1_score)

A0 (Q1): 1.0, 1.0, 0.5, 0.0, 0.0, 1.0   <- gam crosses threshold (1.0->... wait: gam uses orig)
A1 (Q1): 1.0, 1.0, 1.0, 0.5, 0.0, 0.5   <- gam: 1.0->0.5 orig already passing, no crossing
A2 (Q1): 0.5, 0.5, 0.0, 0.0, 0.0, 0.5   <- gam: 0.5 orig at threshold, not below, no crossing
A3 (Q1): 0.0, 0.0, 0.0, 0.0, 0.0, 0.5   <- gam: 0.0->0.5 crosses threshold -> success
A4 (Q1): 1.0, 0.5, 1.0, 0.0, 0.5, 0.5   <- gam: 1.0 orig already passing, no crossing

A5 (Q2): 1.0, 1.0, 1.0, 0.0, 0.5, 1.0   <- gam: 1.0 orig already passing
A6 (Q2): 0.5, 0.0, 0.5, 0.0, 0.0, 0.0   <- gam: 0.5 orig at threshold, no crossing
A7 (Q2): 1.0, 1.0, 0.5, 0.5, 0.0, 0.5   <- gam: 1.0 orig passing
A8 (Q2): 0.0, 0.0, 0.0, 0.0, 0.0, 1.0   <- gam: 0.0->1.0 crosses threshold -> success
A9 (Q2): 0.5, 0.5, 0.5, 0.0, 0.0, 0.0   <- gam: 0.5 orig at threshold, no crossing

A10 (Q3): 1.0, 1.0, 1.0, 0.0, 0.0, 0.5  <- gam: 1.0 orig passing
A11 (Q3): 0.0, 0.0, 0.0, 0.0, 0.0, 0.5  <- gam: 0.0->0.5 crosses threshold -> success
A12 (Q3): 1.0, 0.5, 0.5, 0.5, 0.0, 0.5  <- gam: 1.0 orig passing
A13 (Q3): 0.5, 0.5, 0.0, 0.0, 0.0, 1.0  <- gam: 0.5 orig at threshold, no crossing
A14 (Q3): 1.0, 1.0, 0.5, 0.0, 0.0, 0.0  <- gam: 1.0 orig passing

HAND-COMPUTED EXPECTED VALUES (IVR_flip, all invariance pairs)
==============================================================
Invariance pairs = (orig_score, inv_score) for all 15 answers x 2 types = 30 pairs total.

A "flip" occurs when round(orig, 6) != round(inv, 6).

All invariance pairs with flip indicator (flip = orig != pert):
A0-inv1: (1.0, 1.0) -> flip=False
A0-inv2: (1.0, 0.5) -> flip=True   [1]
A1-inv1: (1.0, 1.0) -> flip=False
A1-inv2: (1.0, 1.0) -> flip=False
A2-inv1: (0.5, 0.5) -> flip=False
A2-inv2: (0.5, 0.0) -> flip=True   [2]
A3-inv1: (0.0, 0.0) -> flip=False
A3-inv2: (0.0, 0.0) -> flip=False
A4-inv1: (1.0, 0.5) -> flip=True   [3]
A4-inv2: (1.0, 1.0) -> flip=False
A5-inv1: (1.0, 1.0) -> flip=False
A5-inv2: (1.0, 1.0) -> flip=False
A6-inv1: (0.5, 0.0) -> flip=True   [4]
A6-inv2: (0.5, 0.5) -> flip=False
A7-inv1: (1.0, 1.0) -> flip=False
A7-inv2: (1.0, 0.5) -> flip=True   [5]
A8-inv1: (0.0, 0.0) -> flip=False
A8-inv2: (0.0, 0.0) -> flip=False
A9-inv1: (0.5, 0.5) -> flip=False
A9-inv2: (0.5, 0.5) -> flip=False
A10-inv1: (1.0, 1.0) -> flip=False
A10-inv2: (1.0, 1.0) -> flip=False
A11-inv1: (0.0, 0.0) -> flip=False
A11-inv2: (0.0, 0.0) -> flip=False
A12-inv1: (1.0, 0.5) -> flip=True  [6]
A12-inv2: (1.0, 0.5) -> flip=True  [7]
A13-inv1: (0.5, 0.5) -> flip=False
A13-inv2: (0.5, 0.0) -> flip=True  [8]
A14-inv1: (1.0, 1.0) -> flip=False
A14-inv2: (1.0, 0.5) -> flip=True  [9]

Total flips: 9/30
IVR_flip_all = 9/30 = 0.3

HAND-COMPUTED EXPECTED VALUES (IVR_absdelta, all invariance pairs)
===================================================================
Sum of |orig - pert| for all 30 pairs:
A0-inv1: |1.0-1.0| = 0.0
A0-inv2: |1.0-0.5| = 0.5
A1-inv1: |1.0-1.0| = 0.0
A1-inv2: |1.0-1.0| = 0.0
A2-inv1: |0.5-0.5| = 0.0
A2-inv2: |0.5-0.0| = 0.5
A3-inv1: |0.0-0.0| = 0.0
A3-inv2: |0.0-0.0| = 0.0
A4-inv1: |1.0-0.5| = 0.5
A4-inv2: |1.0-1.0| = 0.0
A5-inv1: |1.0-1.0| = 0.0
A5-inv2: |1.0-1.0| = 0.0
A6-inv1: |0.5-0.0| = 0.5
A6-inv2: |0.5-0.5| = 0.0
A7-inv1: |1.0-1.0| = 0.0
A7-inv2: |1.0-0.5| = 0.5
A8-inv1: |0.0-0.0| = 0.0
A8-inv2: |0.0-0.0| = 0.0
A9-inv1: |0.5-0.5| = 0.0
A9-inv2: |0.5-0.5| = 0.0
A10-inv1: |1.0-1.0| = 0.0
A10-inv2: |1.0-1.0| = 0.0
A11-inv1: |0.0-0.0| = 0.0
A11-inv2: |0.0-0.0| = 0.0
A12-inv1: |1.0-0.5| = 0.5
A12-inv2: |1.0-0.5| = 0.5
A13-inv1: |0.5-0.5| = 0.0
A13-inv2: |0.5-0.0| = 0.5
A14-inv1: |1.0-1.0| = 0.0
A14-inv2: |1.0-0.5| = 0.5

Total delta: 0.5+0.5+0.5+0.5+0.5+0.5+0.5+0.5+0.5 = 4.5
IVR_absdelta_all = 4.5 / 30 = 0.15

HAND-COMPUTED EXPECTED VALUES (SSR_directional, all sensitivity pairs)
======================================================================
Sensitivity pairs = (orig_score, sen_score). A "success" is pert < orig.
15 answers x 2 types = 30 pairs.

A0-sen1: (1.0, 0.0) -> 0.0 < 1.0 -> success [1]
A0-sen2: (1.0, 0.0) -> 0.0 < 1.0 -> success [2]
A1-sen1: (1.0, 0.5) -> 0.5 < 1.0 -> success [3]
A1-sen2: (1.0, 0.0) -> 0.0 < 1.0 -> success [4]
A2-sen1: (0.5, 0.0) -> 0.0 < 0.5 -> success [5]
A2-sen2: (0.5, 0.0) -> 0.0 < 0.5 -> success [6]
A3-sen1: (0.0, 0.0) -> 0.0 < 0.0 -> False (no change, failure per Pitfall 6)
A3-sen2: (0.0, 0.0) -> 0.0 < 0.0 -> False
A4-sen1: (1.0, 0.0) -> 0.0 < 1.0 -> success [7]
A4-sen2: (1.0, 0.5) -> 0.5 < 1.0 -> success [8]
A5-sen1: (1.0, 0.0) -> 0.0 < 1.0 -> success [9]
A5-sen2: (1.0, 0.5) -> 0.5 < 1.0 -> success [10]
A6-sen1: (0.5, 0.0) -> 0.0 < 0.5 -> success [11]
A6-sen2: (0.5, 0.0) -> 0.0 < 0.5 -> success [12]
A7-sen1: (1.0, 0.5) -> 0.5 < 1.0 -> success [13]
A7-sen2: (1.0, 0.0) -> 0.0 < 1.0 -> success [14]
A8-sen1: (0.0, 0.0) -> 0.0 < 0.0 -> False
A8-sen2: (0.0, 0.0) -> 0.0 < 0.0 -> False
A9-sen1: (0.5, 0.0) -> 0.0 < 0.5 -> success [15]
A9-sen2: (0.5, 0.0) -> 0.0 < 0.5 -> success [16]
A10-sen1: (1.0, 0.0) -> 0.0 < 1.0 -> success [17]
A10-sen2: (1.0, 0.0) -> 0.0 < 1.0 -> success [18]
A11-sen1: (0.0, 0.0) -> 0.0 < 0.0 -> False
A11-sen2: (0.0, 0.0) -> 0.0 < 0.0 -> False
A12-sen1: (1.0, 0.5) -> 0.5 < 1.0 -> success [19]
A12-sen2: (1.0, 0.0) -> 0.0 < 1.0 -> success [20]
A13-sen1: (0.5, 0.0) -> 0.0 < 0.5 -> success [21]
A13-sen2: (0.5, 0.0) -> 0.0 < 0.5 -> success [22]
A14-sen1: (1.0, 0.0) -> 0.0 < 1.0 -> success [23]
A14-sen2: (1.0, 0.0) -> 0.0 < 1.0 -> success [24]

Successes: 24/30
SSR_directional_all = 24/30 = 0.8

HAND-COMPUTED EXPECTED VALUES (ASR_thresholded, all gaming pairs)
=================================================================
Gaming pairs = (orig_score, gam_score). A "crossing" is orig < 0.5 AND gam >= 0.5.
15 answers x 1 type = 15 pairs.

A0-gam1:  (1.0, 1.0) -> orig=1.0 NOT below threshold -> no crossing
A1-gam1:  (1.0, 0.5) -> orig=1.0 NOT below threshold -> no crossing
A2-gam1:  (0.5, 0.5) -> orig=0.5 NOT below threshold (at threshold) -> no crossing
A3-gam1:  (0.0, 0.5) -> orig=0.0 < 0.5 AND pert=0.5 >= 0.5 -> CROSSING [1]
A4-gam1:  (1.0, 0.5) -> orig=1.0 NOT below threshold -> no crossing
A5-gam1:  (1.0, 1.0) -> orig=1.0 NOT below threshold -> no crossing
A6-gam1:  (0.5, 0.0) -> orig=0.5 NOT below threshold -> no crossing
A7-gam1:  (1.0, 0.5) -> orig=1.0 NOT below threshold -> no crossing
A8-gam1:  (0.0, 1.0) -> orig=0.0 < 0.5 AND pert=1.0 >= 0.5 -> CROSSING [2]
A9-gam1:  (0.5, 0.0) -> orig=0.5 NOT below threshold -> no crossing
A10-gam1: (1.0, 0.5) -> orig=1.0 NOT below threshold -> no crossing
A11-gam1: (0.0, 0.5) -> orig=0.0 < 0.5 AND pert=0.5 >= 0.5 -> CROSSING [3]
A12-gam1: (1.0, 0.5) -> orig=1.0 NOT below threshold -> no crossing
A13-gam1: (0.5, 1.0) -> orig=0.5 NOT below threshold -> no crossing
A14-gam1: (1.0, 0.0) -> orig=1.0 NOT below threshold -> no crossing

Crossings: 3/15
ASR_thresholded_all = 3/15 = 0.2

HAND-COMPUTED PER-TYPE BREAKDOWN (synonym_substitution vs surface_rewrite)
=========================================================================
synonym_substitution pairs (inv1 scores), 15 pairs:
A0:  (1.0, 1.0) flip=False, delta=0.0
A1:  (1.0, 1.0) flip=False, delta=0.0
A2:  (0.5, 0.5) flip=False, delta=0.0
A3:  (0.0, 0.0) flip=False, delta=0.0
A4:  (1.0, 0.5) flip=True,  delta=0.5
A5:  (1.0, 1.0) flip=False, delta=0.0
A6:  (0.5, 0.0) flip=True,  delta=0.5
A7:  (1.0, 1.0) flip=False, delta=0.0
A8:  (0.0, 0.0) flip=False, delta=0.0
A9:  (0.5, 0.5) flip=False, delta=0.0
A10: (1.0, 1.0) flip=False, delta=0.0
A11: (0.0, 0.0) flip=False, delta=0.0
A12: (1.0, 0.5) flip=True,  delta=0.5
A13: (0.5, 0.5) flip=False, delta=0.0
A14: (1.0, 1.0) flip=False, delta=0.0

inv1 flips: 3/15 = 0.2
inv1 absdelta: (0.5 + 0.5 + 0.5) / 15 = 1.5 / 15 = 0.1

surface_rewrite pairs (inv2 scores), 15 pairs:
A0:  (1.0, 0.5) flip=True,  delta=0.5
A1:  (1.0, 1.0) flip=False, delta=0.0
A2:  (0.5, 0.0) flip=True,  delta=0.5
A3:  (0.0, 0.0) flip=False, delta=0.0
A4:  (1.0, 1.0) flip=False, delta=0.0
A5:  (1.0, 1.0) flip=False, delta=0.0
A6:  (0.5, 0.5) flip=False, delta=0.0
A7:  (1.0, 0.5) flip=True,  delta=0.5
A8:  (0.0, 0.0) flip=False, delta=0.0
A9:  (0.5, 0.5) flip=False, delta=0.0
A10: (1.0, 1.0) flip=False, delta=0.0
A11: (0.0, 0.0) flip=False, delta=0.0
A12: (1.0, 0.5) flip=True,  delta=0.5
A13: (0.5, 0.0) flip=True,  delta=0.5
A14: (1.0, 0.5) flip=True,  delta=0.5

inv2 flips: 6/15 = 0.4
inv2 absdelta: (0.5+0.5+0.5+0.5+0.5+0.5) / 15 = 3.0 / 15 = 0.2

HAND-COMPUTED PER-TYPE BREAKDOWN (negation_insertion vs key_concept_deletion)
=============================================================================
negation_insertion pairs (sen1 scores), 15 pairs:
A0:  (1.0, 0.0) -> pert < orig -> success
A1:  (1.0, 0.5) -> pert < orig -> success
A2:  (0.5, 0.0) -> pert < orig -> success
A3:  (0.0, 0.0) -> pert == orig -> FAILURE
A4:  (1.0, 0.0) -> pert < orig -> success
A5:  (1.0, 0.0) -> pert < orig -> success
A6:  (0.5, 0.0) -> pert < orig -> success
A7:  (1.0, 0.5) -> pert < orig -> success
A8:  (0.0, 0.0) -> pert == orig -> FAILURE
A9:  (0.5, 0.0) -> pert < orig -> success
A10: (1.0, 0.0) -> pert < orig -> success
A11: (0.0, 0.0) -> pert == orig -> FAILURE
A12: (1.0, 0.5) -> pert < orig -> success
A13: (0.5, 0.0) -> pert < orig -> success
A14: (1.0, 0.0) -> pert < orig -> success

sen1 successes: 12/15 = 0.8

key_concept_deletion pairs (sen2 scores), 15 pairs:
A0:  (1.0, 0.0) -> pert < orig -> success
A1:  (1.0, 0.0) -> pert < orig -> success
A2:  (0.5, 0.0) -> pert < orig -> success
A3:  (0.0, 0.0) -> pert == orig -> FAILURE
A4:  (1.0, 0.5) -> pert < orig -> success
A5:  (1.0, 0.5) -> pert < orig -> success
A6:  (0.5, 0.0) -> pert < orig -> success
A7:  (1.0, 0.0) -> pert < orig -> success
A8:  (0.0, 0.0) -> pert == orig -> FAILURE
A9:  (0.5, 0.0) -> pert < orig -> success
A10: (1.0, 0.0) -> pert < orig -> success
A11: (0.0, 0.0) -> pert == orig -> FAILURE
A12: (1.0, 0.0) -> pert < orig -> success
A13: (0.5, 0.0) -> pert < orig -> success
A14: (1.0, 0.0) -> pert < orig -> success

sen2 successes: 12/15 = 0.8

HAND-COMPUTED PER-TYPE BREAKDOWN (keyword_spam)
================================================
gaming pairs = (orig, gam). Crossings: A3(0.0->0.5), A8(0.0->1.0), A11(0.0->0.5).
keyword_spam: 3/15 = 0.2 (same as aggregate since only one gaming type)
"""

from typing import Dict, List, Tuple

import pytest

from asag.schema import AnswerRecord, PerturbationRecord, QuestionRecord

# ---------------------------------------------------------------------------
# Grade constants (IEEE 754 exact)
# ---------------------------------------------------------------------------
CORRECT = 1.0
PARTIAL = 0.5
INCORRECT = 0.0

# ---------------------------------------------------------------------------
# Mock grade assignments for each answer (indexed 0..14)
# Format: (orig, inv1_syn, inv2_surf, sen1_neg, sen2_kcd, gam1_kws)
# See module docstring for derivations of expected metric values.
# ---------------------------------------------------------------------------
_MOCK_GRADES_RAW: List[Tuple[float, float, float, float, float, float]] = [
    # A0 (Q1): orig=1.0
    (1.0, 1.0, 0.5, 0.0, 0.0, 1.0),
    # A1 (Q1): orig=1.0
    (1.0, 1.0, 1.0, 0.5, 0.0, 0.5),
    # A2 (Q1): orig=0.5
    (0.5, 0.5, 0.0, 0.0, 0.0, 0.5),
    # A3 (Q1): orig=0.0
    (0.0, 0.0, 0.0, 0.0, 0.0, 0.5),
    # A4 (Q1): orig=1.0
    (1.0, 0.5, 1.0, 0.0, 0.5, 0.5),
    # A5 (Q2): orig=1.0
    (1.0, 1.0, 1.0, 0.0, 0.5, 1.0),
    # A6 (Q2): orig=0.5
    (0.5, 0.0, 0.5, 0.0, 0.0, 0.0),
    # A7 (Q2): orig=1.0
    (1.0, 1.0, 0.5, 0.5, 0.0, 0.5),
    # A8 (Q2): orig=0.0
    (0.0, 0.0, 0.0, 0.0, 0.0, 1.0),
    # A9 (Q2): orig=0.5
    (0.5, 0.5, 0.5, 0.0, 0.0, 0.0),
    # A10 (Q3): orig=1.0
    (1.0, 1.0, 1.0, 0.0, 0.0, 0.5),
    # A11 (Q3): orig=0.0
    (0.0, 0.0, 0.0, 0.0, 0.0, 0.5),
    # A12 (Q3): orig=1.0
    (1.0, 0.5, 0.5, 0.5, 0.0, 0.5),
    # A13 (Q3): orig=0.5
    (0.5, 0.5, 0.0, 0.0, 0.0, 1.0),
    # A14 (Q3): orig=1.0
    (1.0, 1.0, 0.5, 0.0, 0.0, 0.0),
]

# ---------------------------------------------------------------------------
# Mock grade map: perturb_id -> graded_score
# Decouples metric tests from any actual grader.
# ---------------------------------------------------------------------------
MOCK_GRADES: Dict[str, float] = {}

# Answer IDs
ANSWER_IDS = [f"test_a{i:02d}" for i in range(15)]
QUESTION_IDS = [f"test_q{j:02d}" for j in range(3)]

# Perturbation IDs follow pattern: {answer_id}_{family_abbrev}_{type_abbrev}
_PERTURB_TYPES = [
    ("invariance", "synonym_substitution", "inv1_syn"),
    ("invariance", "surface_rewrite",      "inv2_surf"),
    ("sensitivity", "negation_insertion",  "sen1_neg"),
    ("sensitivity", "key_concept_deletion", "sen2_kcd"),
    ("gaming",      "keyword_spam",         "gam1_kws"),
]

for _ai, (orig, inv1, inv2, sen1, sen2, gam1) in enumerate(_MOCK_GRADES_RAW):
    aid = ANSWER_IDS[_ai]
    _scores = [inv1, inv2, sen1, sen2, gam1]
    for (_fam, _typ, _abbrev), _score in zip(_PERTURB_TYPES, _scores):
        _pid = f"{aid}_{_abbrev}"
        MOCK_GRADES[_pid] = _score

# ---------------------------------------------------------------------------
# Expected aggregate metric values (see module docstring for full derivations)
# ---------------------------------------------------------------------------
EXPECTED_IVR_FLIP_ALL: float = 9 / 30           # 0.3
EXPECTED_IVR_ABSDELTA_ALL: float = 4.5 / 30     # 0.15
EXPECTED_SSR_DIRECTIONAL_ALL: float = 24 / 30   # 0.8
EXPECTED_ASR_THRESHOLDED_ALL: float = 3 / 15    # 0.2

EXPECTED_BY_TYPE_INVARIANCE: Dict[str, Dict[str, float]] = {
    "synonym_substitution": {
        "ivr_flip":     3 / 15,   # 0.2
        "ivr_absdelta": 1.5 / 15, # 0.1
    },
    "surface_rewrite": {
        "ivr_flip":     6 / 15,   # 0.4
        "ivr_absdelta": 3.0 / 15, # 0.2
    },
}

EXPECTED_BY_TYPE_SENSITIVITY: Dict[str, Dict[str, float]] = {
    "negation_insertion": {
        "ssr_directional": 12 / 15,  # 0.8
    },
    "key_concept_deletion": {
        "ssr_directional": 12 / 15,  # 0.8
    },
}

EXPECTED_BY_TYPE_GAMING: Dict[str, Dict[str, float]] = {
    "keyword_spam": {
        "asr_thresholded": 3 / 15,  # 0.2
    },
}


# ---------------------------------------------------------------------------
# Fixtures: QuestionRecord list
# ---------------------------------------------------------------------------

@pytest.fixture
def synthetic_questions() -> List[QuestionRecord]:
    """Three QuestionRecords for the synthetic mini-dataset.

    Each question has a simple prompt and one reference answer. The content
    is placeholder text — metric computation depends only on scores, not text.
    """
    return [
        QuestionRecord(
            question_id=QUESTION_IDS[0],
            prompt="Explain why a circuit requires a complete loop to function.",
            rubric_text="A complete loop allows current to flow continuously.",
            reference_answers=["Current needs a complete path to flow."],
            score_scale="3way",
            corpus="synthetic",
        ),
        QuestionRecord(
            question_id=QUESTION_IDS[1],
            prompt="What is the role of a resistor in a circuit?",
            rubric_text="A resistor limits the current flow in a circuit.",
            reference_answers=["Resistors reduce current in a circuit."],
            score_scale="3way",
            corpus="synthetic",
        ),
        QuestionRecord(
            question_id=QUESTION_IDS[2],
            prompt="Describe what happens when a bulb is short-circuited.",
            rubric_text="The bulb goes out because current bypasses it.",
            reference_answers=["The bulb turns off as current takes the shorter path."],
            score_scale="3way",
            corpus="synthetic",
        ),
    ]


# ---------------------------------------------------------------------------
# Fixtures: AnswerRecord list
# ---------------------------------------------------------------------------

@pytest.fixture
def synthetic_answers() -> List[AnswerRecord]:
    """Fifteen AnswerRecords — 5 per question — for the synthetic mini-dataset.

    Gold scores are the original scores used in metric derivations (see module
    docstring). Text is placeholder — only scores matter for metric computation.
    """
    _gold_scores = [row[0] for row in _MOCK_GRADES_RAW]
    _gold_labels = {1.0: "correct", 0.5: "partially_correct", 0.0: "incorrect"}
    _question_assignments = [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2]

    answers = []
    for i, (score, q_idx) in enumerate(zip(_gold_scores, _question_assignments)):
        answers.append(
            AnswerRecord(
                answer_id=ANSWER_IDS[i],
                question_id=QUESTION_IDS[q_idx],
                student_answer=f"Student answer text for answer {i}.",
                gold_label=_gold_labels[score],
                gold_score=score,
                annotator_id=None,
            )
        )
    return answers


# ---------------------------------------------------------------------------
# Fixtures: PerturbationRecord list
# ---------------------------------------------------------------------------

@pytest.fixture
def synthetic_perturbations() -> List[PerturbationRecord]:
    """75 PerturbationRecords — 5 per answer, 15 answers.

    Types per answer (in order):
      1. synonym_substitution  (invariance)
      2. surface_rewrite       (invariance)
      3. negation_insertion    (sensitivity)
      4. key_concept_deletion  (sensitivity)
      5. keyword_spam          (gaming)

    Perturbation texts are placeholders. Seed is fixed at 42 for all records
    since this is a synthetic dataset (no actual generation occurred).
    """
    records = []
    _type_templates = [
        ("invariance",  "synonym_substitution",  "inv1_syn",  "Synonym version of student answer {i}."),
        ("invariance",  "surface_rewrite",        "inv2_surf", "Surface rewrite of student answer {i}."),
        ("sensitivity", "negation_insertion",     "sen1_neg",  "Negated version of student answer {i}."),
        ("sensitivity", "key_concept_deletion",   "sen2_kcd",  "Key concept deleted from student answer {i}."),
        ("gaming",      "keyword_spam",           "gam1_kws",  "Keyword spam version of student answer {i}."),
    ]

    for i, aid in enumerate(ANSWER_IDS):
        for fam, typ, abbrev, text_tmpl in _type_templates:
            records.append(
                PerturbationRecord(
                    perturb_id=f"{aid}_{abbrev}",
                    answer_id=aid,
                    family=fam,  # type: ignore[arg-type]
                    type=typ,
                    generator="synthetic",
                    seed=42,
                    text=text_tmpl.format(i=i),
                )
            )
    return records


# ---------------------------------------------------------------------------
# Fixtures: Score pairs for metric computation
# ---------------------------------------------------------------------------

@pytest.fixture
def invariance_pairs() -> List[Tuple[float, float]]:
    """All 30 (orig_score, pert_score) pairs for invariance perturbations.

    Derived from MOCK_GRADES_RAW columns 0 (orig), 1 (inv1_syn), 2 (inv2_surf).
    Order: A0-inv1, A0-inv2, A1-inv1, A1-inv2, ..., A14-inv1, A14-inv2.
    """
    pairs = []
    for orig, inv1, inv2, _s1, _s2, _g1 in _MOCK_GRADES_RAW:
        pairs.append((orig, inv1))
        pairs.append((orig, inv2))
    return pairs


@pytest.fixture
def sensitivity_pairs() -> List[Tuple[float, float]]:
    """All 30 (orig_score, pert_score) pairs for sensitivity perturbations.

    Derived from MOCK_GRADES_RAW columns 0 (orig), 3 (sen1_neg), 4 (sen2_kcd).
    Order: A0-sen1, A0-sen2, A1-sen1, A1-sen2, ..., A14-sen1, A14-sen2.
    """
    pairs = []
    for orig, _i1, _i2, sen1, sen2, _g1 in _MOCK_GRADES_RAW:
        pairs.append((orig, sen1))
        pairs.append((orig, sen2))
    return pairs


@pytest.fixture
def gaming_pairs() -> List[Tuple[float, float]]:
    """All 15 (orig_score, pert_score) pairs for gaming perturbations.

    Derived from MOCK_GRADES_RAW columns 0 (orig), 5 (gam1_kws).
    Order: A0-gam1, A1-gam1, ..., A14-gam1.
    """
    pairs = []
    for orig, _i1, _i2, _s1, _s2, gam1 in _MOCK_GRADES_RAW:
        pairs.append((orig, gam1))
    return pairs


@pytest.fixture
def grade_pairs_for_by_type() -> List[Tuple[str, str, float, float]]:
    """All 75 (answer_id, perturb_type, orig_score, pert_score) tuples.

    Used for compute_by_type tests. Covers all 5 perturbation types.
    """
    tuples = []
    _types_and_col = [
        ("synonym_substitution", 1),
        ("surface_rewrite",      2),
        ("negation_insertion",   3),
        ("key_concept_deletion", 4),
        ("keyword_spam",         5),
    ]
    for ai, row in enumerate(_MOCK_GRADES_RAW):
        aid = ANSWER_IDS[ai]
        orig = row[0]
        for typ, col in _types_and_col:
            pert = row[col]
            tuples.append((aid, typ, orig, pert))
    return tuples
