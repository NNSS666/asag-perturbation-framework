"""
Protocol A: Leave-One-Question-Out (LOQO) cross-validation splitter.

Purpose: Implements DATA-02 — the gold-standard evaluation protocol for measuring
cross-question generalization. Each fold holds out all answers for one question as
the test set and trains on all answers for all other questions.

Design:
  - Wraps sklearn.model_selection.LeaveOneGroupOut where groups = question_id
  - Yields one dict per fold (0-indexed fold_id)
  - Runs the leakage diagnostic (assert_no_leakage) after each split by default
  - Number of folds = number of unique question IDs

See:
  - RESEARCH.md Pattern 4 (LOQO Splitter)
  - RESEARCH.md Pitfall 4 (LOQO Leakage from Reference Answers)
  - splitters/leakage.py for the leakage diagnostic implementation

Python 3.9 compatible — uses typing.List/Dict/Iterator (not built-in generics).
"""

import logging
from typing import Dict, Iterator, List

import numpy as np
from sklearn.model_selection import LeaveOneGroupOut

from asag.schema.records import AnswerRecord, QuestionRecord
from asag.splitters.leakage import assert_no_leakage

logger = logging.getLogger(__name__)


def protocol_a_splits(
    questions: List[QuestionRecord],
    answers: List[AnswerRecord],
    run_leakage_check: bool = True,
) -> Iterator[Dict]:
    """Yield LOQO cross-validation folds, one per unique question.

    For each fold one question is held out: its answers become the test set and
    all remaining answers form the training set. The number of folds equals the
    number of unique question IDs in the answers list.

    Args:
        questions:         Full list of QuestionRecords (used for leakage check
                           and fold metadata). Must contain at least the questions
                           referenced by question_ids in answers.
        answers:           Full list of AnswerRecords to split. Ordering is
                           preserved — returned indices reference this list.
        run_leakage_check: If True (default), call assert_no_leakage after each
                           fold split to confirm no held-out question text appears
                           in training data. Set to False only for benchmarking.

    Yields:
        dict with keys:
            fold_id (int):                  0-indexed fold number.
            held_out_question_id (str):     question_id of the held-out question.
            train_answer_indices (np.ndarray): Integer indices into `answers` for
                                              the training partition.
            test_answer_indices  (np.ndarray): Integer indices into `answers` for
                                              the test partition.
            n_train (int):                  Number of training answers.
            n_test  (int):                  Number of test answers.

    Raises:
        AssertionError: If run_leakage_check=True and any fold fails the leakage
                        diagnostic (see leakage.py for details).
        ValueError:     If questions list has no matching QuestionRecord for the
                        held-out question_id.
    """
    # Build a lookup from question_id -> QuestionRecord for leakage checks.
    question_lookup: Dict[str, QuestionRecord] = {
        q.question_id: q for q in questions
    }

    # Build the groups array (one group label per answer = its question_id).
    groups = np.array([a.question_id for a in answers])
    indices = np.arange(len(answers))

    logo = LeaveOneGroupOut()
    n_splits = logo.get_n_splits(groups=groups)
    unique_questions = np.unique(groups)

    logger.info(
        "Protocol A (LOQO): %d unique questions → %d folds, "
        "%d total answers, leakage_check=%s",
        len(unique_questions),
        n_splits,
        len(answers),
        run_leakage_check,
    )

    test_sizes: List[int] = []

    for fold_id, (train_idx, test_idx) in enumerate(
        logo.split(indices, groups=groups)
    ):
        held_out_qid = groups[test_idx[0]]

        if run_leakage_check:
            # Determine which question IDs appear in training answers.
            train_question_ids = set(groups[train_idx])
            train_questions = [
                question_lookup[qid]
                for qid in train_question_ids
                if qid in question_lookup
            ]
            # Retrieve the held-out QuestionRecord.
            if held_out_qid not in question_lookup:
                raise ValueError(
                    f"Held-out question_id '{held_out_qid}' not found in the "
                    f"provided questions list. Ensure questions contains all "
                    f"QuestionRecords referenced by answers."
                )
            held_out_question = question_lookup[held_out_qid]
            assert_no_leakage(train_questions, held_out_question)

        n_train = len(train_idx)
        n_test = len(test_idx)
        test_sizes.append(n_test)

        yield {
            "fold_id": fold_id,
            "held_out_question_id": held_out_qid,
            "train_answer_indices": train_idx,
            "test_answer_indices": test_idx,
            "n_train": n_train,
            "n_test": n_test,
        }

    # Log summary statistics after all folds have been yielded.
    if test_sizes:
        logger.info(
            "Protocol A complete: %d folds, test set sizes — "
            "min=%d, max=%d, mean=%.1f",
            len(test_sizes),
            min(test_sizes),
            max(test_sizes),
            float(np.mean(test_sizes)),
        )


# ---------------------------------------------------------------------------
# Self-test / demo (run with: PYTHONPATH=src python3 protocol_a.py)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
        stream=sys.stdout,
    )

    print("Loading Beetle via SemEval2013Loader...")
    from asag.loaders.semeval2013 import SemEval2013Loader  # noqa: E402

    loader = SemEval2013Loader("beetle")
    qs, ans = loader.load()
    print(f"Loaded {len(qs)} questions, {len(ans)} answers")

    print("\nRunning Protocol A (LOQO) folds with leakage checks...")
    fold_count = 0
    for fold in protocol_a_splits(qs, ans):
        fid = fold["fold_id"]
        qid = fold["held_out_question_id"]
        n_tr = fold["n_train"]
        n_te = fold["n_test"]
        total = n_tr + n_te
        assert total == len(ans), (
            f"Fold {fid}: train+test={total} != total answers={len(ans)}"
        )
        # Verify no index overlap between train and test
        overlap = set(fold["train_answer_indices"].tolist()) & set(
            fold["test_answer_indices"].tolist()
        )
        assert len(overlap) == 0, f"Fold {fid}: index overlap detected: {overlap}"

        print(
            f"  Fold {fid:3d}: held_out={qid!r:30s}  "
            f"train={n_tr:4d}  test={n_te:3d}  total={total}"
        )
        fold_count += 1

    assert fold_count == len(qs), (
        f"Expected {len(qs)} folds (one per question), got {fold_count}"
    )
    print(
        f"\nProtocol A OK: {fold_count} folds, all leakage checks passed, "
        f"all index invariants satisfied."
    )
