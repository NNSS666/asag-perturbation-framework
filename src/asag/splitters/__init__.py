"""
ASAG evaluation protocol splitters.

Provides:
  protocol_a_splits  — LOQO cross-validation (one question held out per fold)
  protocol_b_splits  — Within-question stratified train/test split
  assert_no_leakage  — Leakage diagnostic for LOQO folds

Usage:
    from asag.splitters import protocol_a_splits, protocol_b_splits, assert_no_leakage

    # Protocol A: LOQO
    for fold in protocol_a_splits(questions, answers):
        train_idx = fold["train_answer_indices"]
        test_idx  = fold["test_answer_indices"]

    # Protocol B: Within-question
    splits = protocol_b_splits(answers)
    # splits: {question_id: (train_answer_ids, test_answer_ids)}
"""

from asag.splitters.leakage import assert_no_leakage
from asag.splitters.protocol_a import protocol_a_splits
from asag.splitters.protocol_b import protocol_b_splits

__all__ = ["protocol_a_splits", "protocol_b_splits", "assert_no_leakage"]
