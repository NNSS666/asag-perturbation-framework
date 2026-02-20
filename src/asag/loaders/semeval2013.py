"""
SemEval 2013 Task 7 dataset loader (DATA-01).

Loads Beetle and SciEntsBank from HuggingFace mirrors:
    nkazi/Beetle       — 56 questions, ~3900 student answers, 5-way labels
    nkazi/SciEntsBank  — 197 questions, ~10800 student answers, 5-way labels

IMPORTANT — HuggingFace split confusion pitfall (see RESEARCH.md Pitfall 1):
    The HuggingFace splits ("train", "test_ua", "test_uq", "test_ud") are the
    ORIGINAL SemEval 2013 splits — they do NOT correspond to this project's
    Protocol A (LOQO) or Protocol B (within-question) splits. This loader
    concatenates ALL rows from ALL HF splits into a single pool. Downstream
    splitters apply the correct protocol.

Question deduplication (see RESEARCH.md Pitfall 2):
    The HF format is answer-centric: each row has the question text repeated.
    This loader groups by question text, collects all distinct reference answers,
    and creates exactly ONE QuestionRecord per unique question.

Grade normalization (see grade.py):
    HuggingFace labels are integers 0–4. This loader maps them to (label_name,
    gold_score) using label_int_to_score(). All gold_score values are in [0, 1].
"""

import hashlib
import logging
from collections import defaultdict
from typing import Dict, List, Literal, Optional, Set, Tuple

from datasets import concatenate_datasets, load_dataset

from asag.loaders.base import DatasetLoader
from asag.schema.grade import label_int_to_score
from asag.schema.records import AnswerRecord, QuestionRecord

# Module-level logger — callers can configure level/handler as needed
logger = logging.getLogger(__name__)


# HuggingFace dataset identifiers for each corpus
_HF_DATASET_IDS: Dict[str, str] = {
    "beetle": "nkazi/Beetle",
    "scientsbank": "nkazi/SciEntsBank",
}

# Expected split names — some may not exist for a given corpus; handled gracefully
_EXPECTED_SPLITS: List[str] = ["train", "test_ua", "test_uq", "test_ud"]


def _derive_question_id(corpus: str, question_text: str) -> str:
    """Derive a stable question_id by hashing the question text.

    Uses MD5 of the question text (8-char hex prefix) to produce a
    deterministic, human-readable identifier. This is stable across runs
    as long as the question text does not change.

    See RESEARCH.md Open Question 4 for rationale.

    Args:
        corpus:        "beetle" or "scientsbank"
        question_text: The raw question prompt string.

    Returns:
        A string like "beetle_a3f2c1b0".
    """
    digest = hashlib.md5(question_text.encode("utf-8")).hexdigest()[:8]
    return f"{corpus}_{digest}"


class SemEval2013Loader(DatasetLoader):
    """Loads SemEval 2013 Task 7 (Beetle or SciEntsBank) into canonical schema.

    Usage:
        loader = SemEval2013Loader("beetle")
        questions, answers = loader.load()
        # len(questions) << len(answers) — confirms deduplication

        loader2 = SemEval2013Loader("scientsbank")
        qs2, ans2 = loader2.load()

    Args:
        corpus: Which corpus to load — "beetle" or "scientsbank".
    """

    def __init__(self, corpus: Literal["beetle", "scientsbank"]) -> None:
        if corpus not in _HF_DATASET_IDS:
            raise ValueError(
                f"Unknown corpus {corpus!r}. "
                f"Expected one of: {sorted(_HF_DATASET_IDS.keys())}"
            )
        self._corpus = corpus

    @property
    def corpus_name(self) -> str:
        """Human-readable identifier for run directory naming."""
        return f"semeval2013_{self._corpus}"

    def load(self) -> Tuple[List[QuestionRecord], List[AnswerRecord]]:
        """Load all rows from all HuggingFace splits into canonical schema.

        CRITICAL: All HF splits (train, test_ua, test_uq, test_ud) are
        concatenated into a single pool. Do NOT use HF split names as
        Protocol A/B splits — see module docstring and RESEARCH.md Pitfall 1.

        Returns:
            questions: Deduplicated list of QuestionRecord — one per unique
                       question text with all reference answers collected.
            answers:   Full list of AnswerRecord — one per student response,
                       with gold_score normalized to [0.0, 1.0].

        Raises:
            ValueError: If no rows are loaded (dataset unreachable or empty).
        """
        hf_id = _HF_DATASET_IDS[self._corpus]
        logger.info("Loading %s from HuggingFace (%s)...", self.corpus_name, hf_id)
        print(f"\n[SemEval2013Loader] Loading corpus: {self.corpus_name}")
        print(f"  HuggingFace dataset: {hf_id}")

        # --- Step 1: Download / retrieve from cache and concatenate all splits ---
        dataset_dict = load_dataset(hf_id)
        available_splits = list(dataset_dict.keys())
        logger.info("  Available HF splits: %s", available_splits)
        print(f"  Available HF splits: {available_splits}")

        splits_to_concat = []
        for split_name in _EXPECTED_SPLITS:
            if split_name in dataset_dict:
                splits_to_concat.append(dataset_dict[split_name])
                logger.debug("  Including HF split: %s (%d rows)", split_name, len(dataset_dict[split_name]))
            else:
                logger.debug("  HF split not present (skipping): %s", split_name)

        if not splits_to_concat:
            # Fallback: use whatever splits are available
            splits_to_concat = list(dataset_dict.values())
            logger.warning("None of expected splits found — using all available splits: %s", available_splits)

        all_rows = concatenate_datasets(splits_to_concat)
        total_rows = len(all_rows)
        logger.info("  Total rows after concatenating all splits: %d", total_rows)
        print(f"  Total rows (all splits): {total_rows}")

        if total_rows == 0:
            raise ValueError(f"No rows loaded for corpus {self._corpus!r} from {hf_id}")

        # --- Step 2: Build QuestionRecord index (deduplicate by question text) ---
        # question_text -> {
        #   "question_id": str,
        #   "reference_answers": Set[str],
        # }
        question_index: Dict[str, dict] = {}
        question_id_log: List[Tuple[str, str]] = []  # (question_id, question_text) for audit log

        # answer_id -> AnswerRecord
        answer_records: List[AnswerRecord] = []

        # --- Step 3: Iterate all rows and build canonical objects ---
        label_distribution: Dict[str, int] = defaultdict(int)

        for row in all_rows:
            question_text: str = row["question"]
            reference_answer: str = row["reference_answer"]
            student_answer: str = row["student_answer"]
            hf_answer_id: str = str(row["id"])
            label_int: int = int(row["label"])

            # Derive/look up question_id
            if question_text not in question_index:
                question_id = _derive_question_id(self._corpus, question_text)
                question_index[question_text] = {
                    "question_id": question_id,
                    "reference_answers": set(),
                }
                question_id_log.append((question_id, question_text))

            # Collect reference answer (may differ per row even for same question)
            question_index[question_text]["reference_answers"].add(reference_answer)

            # Convert integer label to (name, score)
            gold_label, gold_score = label_int_to_score(label_int)
            label_distribution[gold_label] += 1

            # Build AnswerRecord
            answer_id = f"{self._corpus}_{hf_answer_id}"
            q_id = question_index[question_text]["question_id"]
            answer_records.append(
                AnswerRecord(
                    answer_id=answer_id,
                    question_id=q_id,
                    student_answer=student_answer,
                    gold_label=gold_label,
                    gold_score=gold_score,
                    annotator_id=None,  # Not available in HF mirror; see RESEARCH.md OQ3
                )
            )

        # --- Step 4: Build QuestionRecord list (one per unique question) ---
        question_records: List[QuestionRecord] = []
        for question_text, info in question_index.items():
            # Sort reference answers for deterministic ordering
            ref_answers = sorted(info["reference_answers"])
            question_records.append(
                QuestionRecord(
                    question_id=info["question_id"],
                    prompt=question_text,
                    rubric_text=None,  # Not available in HF mirror
                    reference_answers=ref_answers,
                    score_scale="5way",
                    corpus=self._corpus,
                )
            )

        # --- Step 5: Log audit trail and summary statistics ---
        self._log_question_id_mapping(question_id_log)
        self._log_summary(question_records, answer_records, label_distribution)

        return question_records, answer_records

    def _log_question_id_mapping(self, question_id_log: List[Tuple[str, str]]) -> None:
        """Log question_id → question_text mapping for auditability.

        See RESEARCH.md Open Question 4: question_ids are MD5-derived from
        question text; this log enables tracing back from an ID to the original.
        """
        logger.info("  Question ID mapping (first 5 shown):")
        for qid, qtext in question_id_log[:5]:
            logger.info("    %s -> %r", qid, qtext[:80])
        if len(question_id_log) > 5:
            logger.info("    ... (%d more)", len(question_id_log) - 5)

    def _log_summary(
        self,
        questions: List[QuestionRecord],
        answers: List[AnswerRecord],
        label_dist: Dict[str, int],
    ) -> None:
        """Print and log summary statistics for the loaded corpus."""
        n_q = len(questions)
        n_a = len(answers)

        # Answers-per-question distribution
        from collections import Counter
        apq = Counter(a.question_id for a in answers)
        apq_counts = list(apq.values())
        min_apq = min(apq_counts)
        max_apq = max(apq_counts)
        mean_apq = sum(apq_counts) / len(apq_counts)

        print(f"\n  --- {self.corpus_name} Summary ---")
        print(f"  Questions (unique): {n_q}")
        print(f"  Answers (total):    {n_a}")
        print(f"  Answers/question:   min={min_apq}, max={max_apq}, mean={mean_apq:.1f}")
        print(f"  Label distribution:")
        total = sum(label_dist.values())
        for label, count in sorted(label_dist.items()):
            pct = 100 * count / total if total > 0 else 0
            print(f"    {label:<35} {count:>5}  ({pct:.1f}%)")

        logger.info(
            "[%s] Loaded: %d questions, %d answers | "
            "answers/q: min=%d max=%d mean=%.1f | label dist: %s",
            self.corpus_name, n_q, n_a, min_apq, max_apq, mean_apq,
            dict(label_dist),
        )


# ---------------------------------------------------------------------------
# Self-test: load both Beetle and SciEntsBank and print summary statistics
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    for corpus_name in ("beetle", "scientsbank"):
        print(f"\n{'='*60}")
        loader = SemEval2013Loader(corpus_name)  # type: ignore[arg-type]
        questions, answers = loader.load()

        # Correctness assertions
        assert len(questions) > 0, f"No questions loaded for {corpus_name}"
        assert len(answers) > 0, f"No answers loaded for {corpus_name}"
        assert len(questions) < len(answers), (
            f"Expected len(questions) << len(answers) for {corpus_name}, "
            f"got {len(questions)} vs {len(answers)}"
        )

        # All gold_scores must be in [0.0, 1.0]
        out_of_range = [a for a in answers if not (0.0 <= a.gold_score <= 1.0)]
        assert not out_of_range, f"gold_score out of range: {out_of_range[:3]}"

        # All gold_labels must be valid strings
        from asag.schema.grade import LABEL_TO_SCORE
        invalid_labels = [a for a in answers if a.gold_label not in LABEL_TO_SCORE]
        assert not invalid_labels, f"Invalid gold_labels: {[a.gold_label for a in invalid_labels[:3]]}"

        # All answer question_ids must resolve to a known question
        known_qids = {q.question_id for q in questions}
        orphan_answers = [a for a in answers if a.question_id not in known_qids]
        assert not orphan_answers, f"Orphan answers (no matching question): {len(orphan_answers)}"

        print(f"  All assertions passed for {corpus_name}.")

    print("\n\nDone. Both corpora loaded successfully.")
