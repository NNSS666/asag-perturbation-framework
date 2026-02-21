"""
Smoke tests for HybridGrader fit/grade cycle.

These tests validate the interface contract, not grader accuracy. The HybridGrader
trained on 10 minimal examples will not produce meaningful predictions — the point
is that the fit/grade pipeline runs end-to-end without errors and returns values
in the expected ranges and types.

Note: Tests involving SentenceTransformer.encode() are slower (~5-10s first run)
due to model loading. Subsequent runs use the cached all-MiniLM-L6-v2 model.
"""

import pytest

from asag.graders import GradeResult, GraderInterface, HybridGrader
from asag.graders.hybrid import FeatureExtractor
from asag.schema import AnswerRecord, QuestionRecord


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def minimal_questions():
    """Two minimal QuestionRecords for smoke testing."""
    return [
        QuestionRecord(
            question_id="q001",
            prompt="What happens when you connect a battery to a bulb?",
            rubric_text="The bulb lights up because current flows through the circuit.",
            reference_answers=["The bulb lights up because current flows."],
            score_scale="5way",
            corpus="test",
        ),
        QuestionRecord(
            question_id="q002",
            prompt="Why does a circuit need a complete loop?",
            rubric_text="Electrons need a continuous path to flow.",
            reference_answers=["Electrons must have a complete path to flow."],
            score_scale="5way",
            corpus="test",
        ),
    ]


@pytest.fixture(scope="module")
def minimal_answers():
    """10 minimal AnswerRecords: 5 correct, 3 partial, 2 incorrect, across 2 questions."""
    return [
        # Question q001 — correct (3)
        AnswerRecord(answer_id="a001", question_id="q001", student_answer="The bulb lights up because current flows.", gold_label="correct", gold_score=1.0),
        AnswerRecord(answer_id="a002", question_id="q001", student_answer="Current flows through the wire and the bulb illuminates.", gold_label="correct", gold_score=1.0),
        AnswerRecord(answer_id="a003", question_id="q001", student_answer="The bulb glows when connected to the battery.", gold_label="correct", gold_score=1.0),
        # Question q001 — partial (2)
        AnswerRecord(answer_id="a004", question_id="q001", student_answer="The bulb lights up.", gold_label="partially_correct_incomplete", gold_score=0.5),
        AnswerRecord(answer_id="a005", question_id="q001", student_answer="Something happens with the bulb.", gold_label="partially_correct_incomplete", gold_score=0.5),
        # Question q002 — correct (2)
        AnswerRecord(answer_id="a006", question_id="q002", student_answer="Electrons need a complete path to flow through the circuit.", gold_label="correct", gold_score=1.0),
        AnswerRecord(answer_id="a007", question_id="q002", student_answer="A complete loop allows electrons to flow continuously.", gold_label="correct", gold_score=1.0),
        # Question q002 — partial (1)
        AnswerRecord(answer_id="a008", question_id="q002", student_answer="The electrons need to move.", gold_label="partially_correct_incomplete", gold_score=0.5),
        # Question q002 — incorrect (2)
        AnswerRecord(answer_id="a009", question_id="q002", student_answer="The circuit does not need a complete loop.", gold_label="contradictory", gold_score=0.0),
        AnswerRecord(answer_id="a010", question_id="q002", student_answer="Electricity is magic.", gold_label="irrelevant", gold_score=0.0),
    ]


@pytest.fixture(scope="module")
def fitted_grader(minimal_answers, minimal_questions):
    """A HybridGrader fitted on minimal data, shared across tests."""
    question_lookup = {q.question_id: q for q in minimal_questions}
    grader = HybridGrader()
    grader.fit(minimal_answers, question_lookup)
    return grader


# ---------------------------------------------------------------------------
# Test 1: Interface compliance
# ---------------------------------------------------------------------------

def test_hybrid_grader_implements_interface():
    """HybridGrader must inherit from GraderInterface."""
    grader = HybridGrader()
    assert isinstance(grader, GraderInterface), (
        "HybridGrader must be an instance of GraderInterface"
    )


# ---------------------------------------------------------------------------
# Test 2: RuntimeError before fit
# ---------------------------------------------------------------------------

def test_hybrid_grader_grade_before_fit_raises():
    """Calling grade() before fit() must raise RuntimeError."""
    grader = HybridGrader()
    with pytest.raises(RuntimeError, match="must be fit before calling grade"):
        grader.grade(
            question="Test question",
            rubric=None,
            student_answer="Test answer",
        )


# ---------------------------------------------------------------------------
# Test 3: Full fit/grade smoke test
# ---------------------------------------------------------------------------

def test_hybrid_grader_fit_and_grade(fitted_grader, minimal_questions):
    """fit() + grade() cycle must complete without errors and return valid GradeResult."""
    q = minimal_questions[0]
    result = fitted_grader.grade(
        question=q.prompt,
        rubric=None,
        student_answer="The bulb lights up.",
        reference_answer=q.reference_answers[0],
    )

    assert isinstance(result, GradeResult), (
        f"grade() must return a GradeResult, got {type(result)}"
    )
    valid_labels = {
        "correct",
        "partially_correct_incomplete",
        "contradictory",
        "irrelevant",
        "non_domain",
    }
    assert result.label in valid_labels, (
        f"result.label {result.label!r} is not in valid label set {valid_labels}"
    )
    assert 0.0 <= result.score <= 1.0, (
        f"result.score {result.score} is outside [0.0, 1.0]"
    )
    assert 0.0 <= result.confidence <= 1.0, (
        f"result.confidence {result.confidence} is outside [0.0, 1.0]"
    )


# ---------------------------------------------------------------------------
# Test 4: Grader name
# ---------------------------------------------------------------------------

def test_hybrid_grader_name():
    """grader_name must return the expected stable identifier."""
    grader = HybridGrader()
    assert grader.grader_name == "hybrid_logreg_minilm", (
        f"Expected grader_name 'hybrid_logreg_minilm', got {grader.grader_name!r}"
    )


# ---------------------------------------------------------------------------
# Test 5: FeatureExtractor output shape
# ---------------------------------------------------------------------------

def test_feature_extractor_output_shape():
    """FeatureExtractor.extract() must return shape (4,)."""
    extractor = FeatureExtractor()
    features = extractor.extract("test answer", "reference answer")
    assert features.shape == (4,), (
        f"Expected shape (4,), got {features.shape}"
    )


# ---------------------------------------------------------------------------
# Test 6: FeatureExtractor negation flag
# ---------------------------------------------------------------------------

def test_feature_extractor_negation_flag():
    """Feature[2] must be 1.0 for negated answers and 0.0 for non-negated answers."""
    extractor = FeatureExtractor()

    # Negated answer — feature[2] should be 1.0
    with_negation = extractor.extract("This is not correct", "ref")
    assert with_negation[2] == 1.0, (
        f"Expected negation_flag=1.0 for 'This is not correct', got {with_negation[2]}"
    )

    # Non-negated answer — feature[2] should be 0.0
    without_negation = extractor.extract("This is correct", "ref")
    assert without_negation[2] == 0.0, (
        f"Expected negation_flag=0.0 for 'This is correct', got {without_negation[2]}"
    )
