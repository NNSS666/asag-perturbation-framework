"""
Protocol B: Within-question stratified train/test splitter.

Purpose: Implements DATA-05 — the within-question evaluation protocol for
measuring in-distribution vulnerability. Each question's answers are split
independently into train/test, preserving the gold_label distribution via
stratification.

Design:
  - Groups answers by question_id using collections.defaultdict
  - For each question, uses sklearn StratifiedShuffleSplit (n_splits=1) to
    stratify on gold_label, ensuring train/test have similar label distributions
  - Fallback for small groups: positional split when the question has < 5 answers,
    < 2 distinct labels, or any label class has < 2 members (sklearn enforces >= 2)
  - Returns dict mapping question_id -> (train_answer_ids, test_answer_ids)
  - random_state passed explicitly per component for seed isolation (INFR-01)

Edge cases handled (RESEARCH.md Pitfall 5):
  - 1 answer:         put it in train (cannot test on nothing)
  - 2-4 answers:      positional split (stratification unreliable on micro groups)
  - All same label:   positional split (stratification impossible without class variety)

Python 3.9 compatible — uses typing.Dict/List/Tuple (not built-in generics).
"""

import logging
from collections import Counter, defaultdict
from typing import Dict, List, Tuple

from sklearn.model_selection import StratifiedShuffleSplit

from asag.schema.records import AnswerRecord

logger = logging.getLogger(__name__)


def protocol_b_splits(
    answers: List[AnswerRecord],
    test_size: float = 0.2,
    random_state: int = 42,
) -> Dict[str, Tuple[List[str], List[str]]]:
    """Split answers within each question into stratified train/test sets.

    For each unique question_id, the answers belonging to that question are
    partitioned into train and test sets. Stratification on gold_label is used
    when the group has enough samples and label variety; otherwise a positional
    fallback split is applied.

    Args:
        answers:      Full list of AnswerRecords to split. All answers must be
                      included — no pre-filtering should be applied.
        test_size:    Fraction of each question's answers to reserve for test.
                      Default 0.2 (80% train, 20% test). Applied per question,
                      not globally.
        random_state: Seed for StratifiedShuffleSplit. Passed explicitly per
                      component for independent reproducibility control (INFR-01).
                      Default 42.

    Returns:
        Dict mapping question_id (str) to a tuple:
            (train_answer_ids: List[str], test_answer_ids: List[str])
        where each element is a list of answer_id strings. Every answer_id from
        the input appears in exactly one of train or test for its question.

    Notes:
        - Questions with 1 answer: the single answer goes to train, test is empty.
        - Questions with 2-4 answers, a single label, or any class with only 1
          member: positional split at int(n * (1 - test_size)) is used instead
          of stratification (sklearn requires >= 2 members per class).
        - Logging reports total questions split, how many used the fallback, and
          the overall train/test answer count ratio.
    """
    # Group answers by question_id, preserving insertion order.
    by_question: Dict[str, List[AnswerRecord]] = defaultdict(list)
    for answer in answers:
        by_question[answer.question_id].append(answer)

    result: Dict[str, Tuple[List[str], List[str]]] = {}
    fallback_count = 0
    total_train = 0
    total_test = 0

    sss = StratifiedShuffleSplit(
        n_splits=1,
        test_size=test_size,
        random_state=random_state,
    )

    for q_id, q_answers in by_question.items():
        n = len(q_answers)
        labels = [a.gold_label for a in q_answers]
        n_distinct_labels = len(set(labels))
        indices = list(range(n))

        # StratifiedShuffleSplit requires:
        #   (a) at least 5 samples total (to have meaningful train+test sizes)
        #   (b) at least 2 distinct labels (can't stratify one class)
        #   (c) every label class must have >= 2 members (sklearn enforces this)
        label_counts = Counter(labels)
        min_class_count = min(label_counts.values())
        use_fallback = n < 5 or n_distinct_labels < 2 or min_class_count < 2

        if use_fallback:
            # Positional split — deterministic, no randomness needed.
            if n == 1:
                # Single answer: train only, test is empty.
                split_point = 1
            else:
                split_point = max(1, int(n * (1.0 - test_size)))
            train_answer_ids = [q_answers[i].answer_id for i in indices[:split_point]]
            test_answer_ids = [q_answers[i].answer_id for i in indices[split_point:]]
            fallback_count += 1
            logger.debug(
                "Protocol B fallback split for question %r: "
                "n=%d, distinct_labels=%d → train=%d, test=%d",
                q_id, n, n_distinct_labels,
                len(train_answer_ids), len(test_answer_ids),
            )
        else:
            # Stratified split on gold_label.
            train_idx_arr, test_idx_arr = next(sss.split(indices, labels))
            train_answer_ids = [q_answers[i].answer_id for i in train_idx_arr]
            test_answer_ids = [q_answers[i].answer_id for i in test_idx_arr]

        result[q_id] = (train_answer_ids, test_answer_ids)
        total_train += len(train_answer_ids)
        total_test += len(test_answer_ids)

    n_questions = len(result)
    logger.info(
        "Protocol B complete: %d questions split, %d used fallback, "
        "%d train answers, %d test answers (overall ratio %.2f/%.2f)",
        n_questions,
        fallback_count,
        total_train,
        total_test,
        total_train / max(1, total_train + total_test),
        total_test / max(1, total_train + total_test),
    )

    return result


# ---------------------------------------------------------------------------
# Self-test / demo (run with: PYTHONPATH=src python3 src/asag/splitters/protocol_b.py)
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

    print("\nRunning Protocol B (within-question) splits...")
    splits = protocol_b_splits(ans)

    print(f"\nPer-question split statistics ({len(splits)} questions):")
    for q_id, (train_ids, test_ids) in sorted(splits.items()):
        n_total = len(train_ids) + len(test_ids)
        test_pct = len(test_ids) / max(1, n_total) * 100
        print(
            f"  {q_id}: {n_total:4d} answers → "
            f"train={len(train_ids):3d}, test={len(test_ids):3d} "
            f"({test_pct:.0f}% test)"
        )

    # Verify invariants
    total_train = sum(len(t[0]) for t in splits.values())
    total_test = sum(len(t[1]) for t in splits.values())
    print(f"\nTotals: {total_train} train + {total_test} test = {total_train + total_test}")
    assert total_train + total_test == len(ans), (
        f"Total mismatch: {total_train + total_test} != {len(ans)}"
    )
    assert len(splits) == len(qs), (
        f"Question count mismatch: {len(splits)} splits != {len(qs)} questions"
    )

    # Verify no overlap between train and test within each question
    for q_id, (train_ids, test_ids) in splits.items():
        overlap = set(train_ids) & set(test_ids)
        assert len(overlap) == 0, f"Train/test overlap in question {q_id}: {overlap}"

    # Verify reproducibility: same random_state → same splits
    splits2 = protocol_b_splits(ans, random_state=42)
    for q_id, (train_ids, test_ids) in splits.items():
        assert splits2[q_id][0] == train_ids, f"Train ids differ for {q_id}"
        assert splits2[q_id][1] == test_ids, f"Test ids differ for {q_id}"

    print("\nProtocol B OK: all invariants satisfied, reproducibility confirmed.")
