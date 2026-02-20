"""
Grade label definitions and score normalization for ASAG datasets.

All datasets are normalized to a continuous float in [0.0, 1.0] representing
degree of correctness. This enables direct comparison across different grading
schemes (5-way SemEval labels, binary pass/fail, continuous scores).

Mapping rationale (confirmed by ASAG2024 benchmark, arxiv.org/abs/2409.18596):
  - "correct"                     → 1.0  (full credit)
  - "partially_correct_incomplete"→ 0.5  (half credit — semantically correct)
  - "contradictory"               → 0.0  (wrong: contradicts expected answer)
  - "irrelevant"                  → 0.0  (wrong: off-topic response)
  - "non_domain"                  → 0.0  (wrong: outside domain entirely)

The LABEL_NAMES list preserves the HuggingFace integer index ordering used in
nkazi/Beetle and nkazi/SciEntsBank datasets:
  0 → correct
  1 → contradictory
  2 → partially_correct_incomplete
  3 → irrelevant
  4 → non_domain
"""

from enum import Enum
from typing import Dict, List, Tuple


class GradeLabel(str, Enum):
    """Five-way grade label for SemEval 2013 Task 7 (Beetle + SciEntsBank)."""

    correct = "correct"
    partially_correct_incomplete = "partially_correct_incomplete"
    contradictory = "contradictory"
    irrelevant = "irrelevant"
    non_domain = "non_domain"


# Normalized [0.0, 1.0] score for each label string.
# Rationale: ASAG2024 benchmark confirms [0,1] normalization as current standard.
# partially_correct_incomplete at 0.5 is semantically half-credit.
# contradictory, irrelevant, non_domain are all variants of "incorrect".
LABEL_TO_SCORE: Dict[str, float] = {
    "correct": 1.0,
    "partially_correct_incomplete": 0.5,
    "contradictory": 0.0,
    "irrelevant": 0.0,
    "non_domain": 0.0,
}

# HuggingFace integer-to-label mapping for nkazi/Beetle and nkazi/SciEntsBank.
# Index positions match the ClassLabel encoding in those HF datasets:
#   0 → correct
#   1 → contradictory
#   2 → partially_correct_incomplete
#   3 → irrelevant
#   4 → non_domain
LABEL_NAMES: List[str] = [
    "correct",                      # 0
    "contradictory",                # 1
    "partially_correct_incomplete", # 2
    "irrelevant",                   # 3
    "non_domain",                   # 4
]


def label_int_to_score(label_int: int) -> Tuple[str, float]:
    """Convert a HuggingFace integer label to (label_name, gold_score).

    Args:
        label_int: Integer label from HuggingFace dataset (0–4).

    Returns:
        Tuple of (label_name: str, gold_score: float) where gold_score is in
        [0.0, 1.0].

    Raises:
        ValueError: If label_int is outside the expected range [0, 4].

    Example:
        >>> label_int_to_score(0)
        ('correct', 1.0)
        >>> label_int_to_score(2)
        ('partially_correct_incomplete', 0.5)
        >>> label_int_to_score(1)
        ('contradictory', 0.0)
    """
    if not (0 <= label_int < len(LABEL_NAMES)):
        raise ValueError(
            f"label_int {label_int!r} is out of range. "
            f"Expected 0–{len(LABEL_NAMES) - 1}. "
            f"Known labels: {LABEL_NAMES}"
        )
    label_name = LABEL_NAMES[label_int]
    gold_score = LABEL_TO_SCORE[label_name]
    return label_name, gold_score
