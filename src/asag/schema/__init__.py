"""
asag.schema — Canonical data types for the ASAG pipeline.

Re-exports all public schema types so callers can use:
    from asag.schema import QuestionRecord, AnswerRecord, PerturbationRecord
    from asag.schema import GradeLabel, LABEL_TO_SCORE, label_int_to_score
"""

from asag.schema.grade import (
    LABEL_NAMES,
    LABEL_TO_SCORE,
    GradeLabel,
    label_int_to_score,
)
from asag.schema.records import AnswerRecord, PerturbationRecord, QuestionRecord

__all__ = [
    # Records
    "QuestionRecord",
    "AnswerRecord",
    "PerturbationRecord",
    # Grade mapping
    "GradeLabel",
    "LABEL_TO_SCORE",
    "LABEL_NAMES",
    "label_int_to_score",
]
