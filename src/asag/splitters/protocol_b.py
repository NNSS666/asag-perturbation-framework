"""
Protocol B: Within-question stratified train/test splitter.

Placeholder — full implementation in Task 2 (01-02 Plan).
"""

from typing import Dict, List, Tuple

from asag.schema.records import AnswerRecord


def protocol_b_splits(
    answers: List[AnswerRecord],
    test_size: float = 0.2,
    random_state: int = 42,
) -> Dict[str, Tuple[List[str], List[str]]]:
    """Stub — to be implemented in Task 2."""
    raise NotImplementedError("protocol_b_splits is not yet implemented.")
