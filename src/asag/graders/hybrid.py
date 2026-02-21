"""
HybridGrader — Linguistic features + Sentence-BERT embeddings + LogisticRegression.

Combines 4 handcrafted linguistic features with 384-dim sentence embeddings from
all-MiniLM-L6-v2 into a 388-dim feature vector, then trains LogisticRegression
with StandardScaler normalization.

Design rationale:
  - Interpretable: LogisticRegression coefficients are readable for thesis analysis
  - Baseline-quality: not SOTA, but demonstrates end-to-end evaluation framework
  - Efficient: MiniLM-L6-v2 is fast and ~80MB; suitable for LOQO cross-val loops
  - Class-weighted: balanced class_weight handles label imbalance in SemEval data

Feature breakdown (388-dim total):
  [0]   lexical_overlap   — F1 between student/reference token sets
  [1]   length_ratio      — student/reference word count ratio, clipped to 3.0
  [2]   negation_flag     — 1.0 if student answer contains negation word
  [3]   ref_token_recall  — proportion of reference tokens found in student answer
  [4:388] SBERT embedding — 384-dim all-MiniLM-L6-v2 sentence embedding of student answer

Python 3.9 compatible: uses typing.Optional/Dict/List/Tuple (not X | Y syntax).
"""

import re
from typing import Dict, List, Optional, Tuple

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sentence_transformers import SentenceTransformer

from asag.graders.base import GradeResult, GraderInterface
from asag.schema import AnswerRecord, LABEL_TO_SCORE, QuestionRecord


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Negation words that indicate a student answer may contradict the reference.
# Pattern is compiled once at module import for efficiency.
NEGATION_PATTERN = re.compile(
    r"\b(not|never|no|cannot|can't|won't|doesn't|isn't|aren't|wasn't|weren't"
    r"|don't|didn't|haven't|hadn't|shouldn't|wouldn't|couldn't)\b",
    re.IGNORECASE,
)

# Reverse mapping of LABEL_TO_SCORE — used for converting predicted float scores
# back to labels when needed. Note: 0.0 maps to three labels (contradictory is
# the canonical choice for the reverse direction).
SCORE_TO_LABEL: Dict[float, str] = {
    1.0: "correct",
    0.5: "partially_correct_incomplete",
    0.0: "contradictory",
}


# ---------------------------------------------------------------------------
# FeatureExtractor
# ---------------------------------------------------------------------------

class FeatureExtractor:
    """Extracts 4 handcrafted linguistic features from a student/reference pair.

    All features are computed purely from token sets (lowercased, whitespace-split).
    This keeps extraction fast and deterministic — no external models required.

    Output shape: (4,) float64 array.
    Features:
        [0] lexical_overlap   — F1 between student and reference token sets
        [1] length_ratio      — student/reference word count, clipped to [0, 3.0]
        [2] negation_flag     — 1.0 if negation word found in student_answer
        [3] ref_token_recall  — |intersection| / |reference_tokens|
    """

    def extract(self, student_answer: str, reference_answer: str) -> np.ndarray:
        """Compute 4 handcrafted features.

        Args:
            student_answer:   Raw student response text.
            reference_answer: Reference/model answer text.

        Returns:
            np.ndarray of shape (4,) with dtype float64.
            Returns np.zeros(4) when reference_tokens is empty (no reference provided).
        """
        student_tokens = set(student_answer.lower().split())
        ref_tokens = set(reference_answer.lower().split())

        # Guard: if no reference tokens, features are undefined — return zeros.
        if not ref_tokens:
            return np.zeros(4, dtype=np.float64)

        intersection = student_tokens & ref_tokens

        # Feature 0: Lexical overlap (F1 between token sets)
        precision = len(intersection) / max(len(student_tokens), 1)
        recall = len(intersection) / len(ref_tokens)
        lexical_overlap = (
            2 * precision * recall / max(precision + recall, 1e-9)
        )

        # Feature 1: Length ratio (clipped to [0.0, 3.0] to avoid extreme outliers)
        length_ratio = min(
            len(student_answer.split()) / max(len(reference_answer.split()), 1),
            3.0,
        )

        # Feature 2: Negation flag (1.0 if student answer contains a negation word)
        negation_flag = 1.0 if NEGATION_PATTERN.search(student_answer) else 0.0

        # Feature 3: Recall of reference tokens in student answer
        ref_token_recall = recall

        return np.array(
            [lexical_overlap, length_ratio, negation_flag, ref_token_recall],
            dtype=np.float64,
        )


# ---------------------------------------------------------------------------
# HybridGrader
# ---------------------------------------------------------------------------

class HybridGrader(GraderInterface):
    """Hybrid grader combining handcrafted features with SBERT embeddings.

    Architecture:
        - 4 handcrafted linguistic features (FeatureExtractor)
        - 384-dim all-MiniLM-L6-v2 sentence embedding of student answer
        - Concatenated into 388-dim feature vector
        - StandardScaler → LogisticRegression(class_weight='balanced', multinomial)

    The grade() method extends the GraderInterface base with an optional
    reference_answer kwarg needed for feature extraction. Other graders (e.g. LLM)
    do not need this parameter. The default value of "" ensures backward compatibility
    with callers that follow the base interface signature.

    Usage:
        grader = HybridGrader()
        grader.fit(train_answers, question_lookup)
        result = grader.grade(
            question="What happens when...",
            rubric=None,
            student_answer="The bulb lights up.",
            reference_answer="Current flows and the bulb lights up.",
        )

    Note: HybridGrader must be fit before calling grade(). A RuntimeError is raised
    otherwise to prevent silent prediction failures.
    """

    MODEL_ID = "all-MiniLM-L6-v2"
    LABEL_ORDER = [
        "correct",
        "partially_correct_incomplete",
        "contradictory",
        "irrelevant",
        "non_domain",
    ]

    def __init__(self) -> None:
        self._extractor = FeatureExtractor()
        self._encoder = SentenceTransformer(self.MODEL_ID)
        self._pipeline: Optional[Pipeline] = None

    # ------------------------------------------------------------------
    # GraderInterface abstract members
    # ------------------------------------------------------------------

    @property
    def grader_name(self) -> str:
        """Unique identifier for this grader.

        Returns:
            str: "hybrid_logreg_minilm"
        """
        return "hybrid_logreg_minilm"

    def grade(
        self,
        question: str,
        rubric: Optional[str],
        student_answer: str,
        reference_answer: str = "",
    ) -> GradeResult:
        """Grade a student answer using the fitted hybrid pipeline.

        HybridGrader extends the base interface with an optional reference_answer
        kwarg needed for feature extraction. Other graders (LLM) do not need this
        parameter.

        Args:
            question:         The question text shown to the student.
            rubric:           Optional grading rubric (unused by HybridGrader —
                              the model learns from training labels instead).
            student_answer:   The raw text of the student's response.
            reference_answer: Reference answer used for handcrafted feature
                              extraction. Defaults to "" (no reference).

        Returns:
            GradeResult with label, score in [0.0, 1.0], and confidence.

        Raises:
            RuntimeError: If called before fit().
        """
        if self._pipeline is None:
            raise RuntimeError(
                "HybridGrader must be fit before calling grade(). "
                "Call grader.fit(train_answers, question_lookup) first."
            )

        x = self._build_single_feature(student_answer, reference_answer)
        label: str = self._pipeline.predict([x])[0]
        proba = self._pipeline.predict_proba([x])[0]
        confidence = float(max(proba))
        score = LABEL_TO_SCORE.get(label, 0.0)

        return GradeResult(label=label, score=score, confidence=confidence)

    # ------------------------------------------------------------------
    # Training
    # ------------------------------------------------------------------

    def fit(
        self,
        train_answers: List[AnswerRecord],
        question_lookup: Dict[str, QuestionRecord],
    ) -> None:
        """Train the hybrid pipeline on a list of AnswerRecords.

        Builds a 388-dim feature matrix (4 handcrafted + 384 SBERT per answer),
        then fits StandardScaler + LogisticRegression.

        Args:
            train_answers:   List of AnswerRecord instances to train on.
            question_lookup: Dict mapping question_id → QuestionRecord.
                             Used to retrieve the first reference answer for
                             handcrafted feature extraction.

        Side effect:
            Sets self._pipeline to the fitted sklearn Pipeline.
        """
        X, y = self._build_features(train_answers, question_lookup)

        pipeline = Pipeline(
            [
                ("scaler", StandardScaler()),
                (
                    "lr",
                    LogisticRegression(
                        max_iter=500,
                        C=1.0,
                        multi_class="multinomial",
                        class_weight="balanced",
                        random_state=42,
                    ),
                ),
            ]
        )
        pipeline.fit(X, y)
        self._pipeline = pipeline

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_single_feature(self, student: str, reference: str) -> np.ndarray:
        """Concatenate handcrafted (4-dim) and SBERT embedding (384-dim) features.

        Args:
            student:   Student answer text.
            reference: Reference answer text (used for handcrafted features only).

        Returns:
            np.ndarray of shape (388,) with dtype float64.
        """
        handcrafted = self._extractor.extract(student, reference)  # (4,)
        embedding = self._encoder.encode(
            student, show_progress_bar=False
        ).astype(np.float64)  # (384,)
        return np.concatenate([handcrafted, embedding])  # (388,)

    def _build_features(
        self,
        answers: List[AnswerRecord],
        question_lookup: Dict[str, QuestionRecord],
    ) -> Tuple[np.ndarray, List[str]]:
        """Build feature matrix and label list from a list of AnswerRecords.

        Args:
            answers:         List of AnswerRecord instances.
            question_lookup: Dict mapping question_id → QuestionRecord.

        Returns:
            Tuple of:
                X: np.ndarray of shape (n_answers, 388)
                y: List[str] of gold labels
        """
        X_list: List[np.ndarray] = []
        y_list: List[str] = []

        for ans in answers:
            q = question_lookup.get(ans.question_id)
            ref = q.reference_answers[0] if (q and q.reference_answers) else ""
            x = self._build_single_feature(ans.student_answer, ref)
            X_list.append(x)
            y_list.append(ans.gold_label)

        return np.vstack(X_list), y_list
