"""
GraderInterface ABC and GradeResult model.

Defines the contract all graders (hybrid, transformer, LLM) must implement.
Every grader receives a question, an optional rubric, and a student answer,
and returns a GradeResult with a normalized score in [0.0, 1.0].

Design principles:
  - GradeResult is frozen (immutable after construction)
  - Score and confidence are validated to [0.0, 1.0] at construction time
  - GraderInterface is an ABC — concrete subclasses must implement grade() and grader_name
  - Python 3.9 compatible: uses typing.Optional (not X | Y syntax)
"""

from abc import ABC, abstractmethod
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator


class GradeResult(BaseModel):
    """The output of a grader for a single student answer.

    Fields:
        label:      Human-readable grade label, e.g. "correct" or "incorrect".
        score:      Normalized float in [0.0, 1.0]. 1.0 = fully correct.
        confidence: Grader's confidence in its prediction, in [0.0, 1.0].
                    Use 1.0 when the grader is deterministic (e.g. rule-based).
    """

    model_config = ConfigDict(frozen=True)

    label: str
    score: float
    confidence: float

    @field_validator("score", "confidence")
    @classmethod
    def _validate_range(cls, v: float) -> float:
        """Ensure score and confidence are in [0.0, 1.0]."""
        if not (0.0 <= v <= 1.0):
            raise ValueError(
                f"Value {v!r} is outside the allowed range [0.0, 1.0]. "
                "Scores and confidences must be normalized before constructing GradeResult."
            )
        return v


class GraderInterface(ABC):
    """Abstract base class for all ASAG graders.

    Every grader implementation must:
      1. Inherit from GraderInterface.
      2. Implement grade() to return a GradeResult.
      3. Implement grader_name property to return a unique identifier string.

    The contract is deliberately minimal so that rule-based, transformer, and
    LLM graders can all conform without constraint on their internal logic.

    Example usage:
        class MyGrader(GraderInterface):
            @property
            def grader_name(self) -> str:
                return "my_grader_v1"

            def grade(self, question, rubric, student_answer):
                score = ... # grading logic
                return GradeResult(label="correct", score=score, confidence=1.0)
    """

    @property
    @abstractmethod
    def grader_name(self) -> str:
        """Unique identifier for this grader.

        Used as a key in MetricResult and experiment logs. Must be stable
        across runs (don't include timestamps or random seeds).

        Returns:
            str: Unique grader name, e.g. "bert_base_uncased_v1".
        """
        ...

    @abstractmethod
    def grade(
        self,
        question: str,
        rubric: Optional[str],
        student_answer: str,
    ) -> GradeResult:
        """Grade a student answer and return a normalized score.

        Args:
            question:       The question text shown to the student.
            rubric:         Optional grading rubric. May be None if the dataset
                            does not provide rubrics (e.g. SemEval HF mirror).
            student_answer: The raw text of the student's response.

        Returns:
            GradeResult with score in [0.0, 1.0], label, and confidence.
        """
        ...
