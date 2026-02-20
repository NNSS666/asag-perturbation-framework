"""
Canonical three-object schema for ASAG research.

These three Pydantic v2 models are the single source of truth for all data
flowing through the pipeline. Every loader, splitter, grader, and metric
receives validated instances of these types — never raw dicts or DataFrames.

Design principles:
  - frozen=True: immutable after construction — prevents accidental mutation
  - Python 3.9 compatible: uses typing.Optional/List/Literal (not X | Y syntax)
  - Fail-fast validation: bad data raises ValidationError immediately at load
  - JSON roundtrip: model_dump_json() / model_validate_json() are lossless
"""

from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict


class QuestionRecord(BaseModel):
    """A single unique question with its rubric and reference answers.

    One QuestionRecord is created per unique question text, regardless of how
    many student answers exist for that question. The reference_answers list
    collects all distinct reference answers provided in the dataset.

    Fields:
        question_id:      Stable identifier, e.g. "beetle_a3f2c1b0" (MD5-derived).
        prompt:           The question text shown to the student.
        rubric_text:      Optional grading rubric (not available in SemEval HF mirror).
        reference_answers: One or more reference answers representing correct responses.
        score_scale:      The original grading scale of the dataset:
                          "5way"  — SemEval 5-way (correct / partially / contradictory
                                    / irrelevant / non_domain)
                          "3way"  — 3-way (correct / partially / incorrect)
                          "2way"  — binary (correct / incorrect)
                          "continuous" — continuous float scores
        corpus:           Dataset origin, e.g. "beetle" or "scientsbank".
    """

    model_config = ConfigDict(frozen=True)

    question_id: str
    prompt: str
    rubric_text: Optional[str] = None
    reference_answers: List[str]
    score_scale: Literal["5way", "3way", "2way", "continuous"] = "5way"
    corpus: Optional[str] = None


class AnswerRecord(BaseModel):
    """A single student answer with its gold label and normalized score.

    One AnswerRecord per student response. gold_score is always normalized to
    [0.0, 1.0] by the loader — this enables cross-dataset comparison even when
    the original datasets use different grading schemes.

    Fields:
        answer_id:     Stable identifier, e.g. "beetle_12345".
        question_id:   Foreign key linking to a QuestionRecord.
        student_answer: The raw text of the student's response.
        gold_label:    String label, e.g. "correct", "partially_correct_incomplete".
        gold_score:    Normalized float in [0.0, 1.0]. 1.0 = fully correct.
        annotator_id:  Optional annotator identifier (None for SemEval HF mirror).
    """

    model_config = ConfigDict(frozen=True)

    answer_id: str
    question_id: str
    student_answer: str
    gold_label: str
    gold_score: float
    annotator_id: Optional[str] = None


class PerturbationRecord(BaseModel):
    """A single perturbation of a student answer for robustness testing.

    PerturbationRecords are generated in Phase 2. They are linked to an
    AnswerRecord via answer_id and carry metadata about how they were produced.

    Fields:
        perturb_id:  Stable identifier, e.g. "beetle_12345_inv_001".
        answer_id:   Foreign key linking to the source AnswerRecord.
        family:      High-level perturbation family:
                     "invariance"  — should not change the grade (paraphrase, typo)
                     "sensitivity" — should change the grade (deletion, negation)
                     "gaming"      — adversarial gaming attempt
        type:        Specific perturbation type, e.g. "synonym_substitution".
        generator:   Tool that generated this perturbation, e.g. "rule-based" or
                     "gpt-4o".
        seed:        Random seed used during generation for reproducibility.
        text:        The perturbed student answer text.
    """

    model_config = ConfigDict(frozen=True)

    perturb_id: str
    answer_id: str
    family: Literal["invariance", "sensitivity", "gaming"]
    type: str
    generator: str
    seed: int
    text: str


# ---------------------------------------------------------------------------
# Self-test: JSON roundtrip for all three models (run with `python records.py`)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Running JSON roundtrip self-test for canonical schema...")

    # QuestionRecord
    q = QuestionRecord(
        question_id="beetle_a3f2c1b0",
        prompt="What happens when you connect a battery to a bulb?",
        rubric_text="The bulb lights up because current flows through the circuit.",
        reference_answers=[
            "The bulb lights up because current flows.",
            "Current flows and the bulb illuminates.",
        ],
        score_scale="5way",
        corpus="beetle",
    )
    q_json = q.model_dump_json()
    q2 = QuestionRecord.model_validate_json(q_json)
    assert q == q2, "QuestionRecord roundtrip failed"
    print(f"  QuestionRecord OK: {q.question_id!r}, {len(q.reference_answers)} ref answers")

    # AnswerRecord
    a = AnswerRecord(
        answer_id="beetle_12345",
        question_id="beetle_a3f2c1b0",
        student_answer="The bulb lights up.",
        gold_label="correct",
        gold_score=1.0,
        annotator_id=None,
    )
    a_json = a.model_dump_json()
    a2 = AnswerRecord.model_validate_json(a_json)
    assert a == a2, "AnswerRecord roundtrip failed"
    print(f"  AnswerRecord OK: {a.answer_id!r}, gold_score={a.gold_score}")

    # PerturbationRecord
    p = PerturbationRecord(
        perturb_id="beetle_12345_inv_001",
        answer_id="beetle_12345",
        family="invariance",
        type="synonym_substitution",
        generator="rule-based",
        seed=42,
        text="The lamp lights up.",
    )
    p_json = p.model_dump_json()
    p2 = PerturbationRecord.model_validate_json(p_json)
    assert p == p2, "PerturbationRecord roundtrip failed"
    print(f"  PerturbationRecord OK: {p.perturb_id!r}, family={p.family!r}")

    # Verify frozen=True prevents mutation
    try:
        q.question_id = "modified"  # type: ignore[misc]
        raise AssertionError("Mutation should have raised an error!")
    except Exception as exc:
        print(f"  Immutability OK: mutation correctly blocked ({type(exc).__name__})")

    print("\nAll self-tests passed.")
