# Phase 2: Metrics and Hybrid Grader - Research

**Researched:** 2026-02-21
**Domain:** ASAG robustness metric calculators (IVR/SSR/ASR), hybrid grader (handcrafted features + sentence-transformer embeddings + sklearn classifier), GraderInterface ABC, gold unit tests with synthetic mini-dataset
**Confidence:** HIGH (all core libraries verified; metric formulas validated by hand computation; Phase 1 codebase fully read)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **IVR_flip**: ANY score change on an invariance perturbation counts as a violation (strictest definition). Since the grading scale is discrete (correct/partially_correct_complete/partially_correct_incomplete/contradictory/irrelevant), every change is already a full category shift.
- **IVR_absdelta**: Mean absolute score delta across all invariance perturbation pairs (continuous measure of instability magnitude).
- **SSR_directional**: Claude's discretion on whether direction-only or reaching-expected-grade counts as success — choose the most defensible definition from ASAG literature.
- **ASR_thresholded**: Claude's discretion — choose between "increase >= 1 level OR crossing passing threshold" vs "crossing threshold only" based on literature.
- **Edge cases (zero denominators)**: Claude's discretion — choose the standard approach in evaluation literature (likely exclude from calculation).
- **Hybrid grader sentence-transformer model**: all-MiniLM-L6-v2 (80MB, standard in literature, sufficient for a baseline grader).
- **Hybrid grader feature set**: Claude's discretion — choose the most defensible set from ASAG literature, starting from the requirement baseline (lexical overlap, length ratio, negation flags) and extending as appropriate.
- **Hybrid grader classifier**: Claude's discretion — choose the most defensible option for a paper (likely logistic regression for interpretability or gradient boosting for performance).
- **GraderInterface contract**: Returns both grade label AND confidence score (float 0-1); input is (question, rubric, student_answer); all grading models in later phases must implement this same interface.
- **Gold test dataset**: Size and structure: Claude's discretion — dimension it to cover all necessary cases while remaining hand-calculable; expected values MUST be documented with step-by-step derivation formulas.
- **Grade scale for tests**: Claude's discretion — choose between full SemEval 5-level scale or simplified 3-level for tests based on what validates the metrics most robustly.
- **Protocol comparison format**: Claude's discretion — choose the clearest table/visualization format for an academic paper.
- **Perturbation type granularity**: breakdown goes down to specific perturbation type level (e.g., synonym_substitution, negation_insertion) for maximum detail and downstream heatmap compatibility.
- **End-to-end validation corpora**: run on BOTH Beetle AND SciEntsBank corpora (not just Beetle subset).
- **Mock perturbations for E2E**: Claude's discretion — choose between hardcoded mocks vs minimal rule-based generator, whichever best validates the loop without anticipating Phase 3.

### Claude's Discretion

- SSR_directional exact success criterion (direction-only vs reaching expected grade)
- ASR_thresholded exact threshold definition
- Zero-denominator handling for metrics
- Hybrid grader feature set selection
- Hybrid grader classifier choice
- Gold test dataset sizing and edge case strategy
- Protocol comparison visualization format
- Mock perturbation approach for E2E testing

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| EVAL-01 | Compute Invariance Violation Rate (IVR) — frequency and degree of score changes on meaning-preserving perturbations | IVR_flip = proportion of pairs where score changed; IVR_absdelta = mean(abs(original - perturbed)); both return float('nan') on empty input |
| EVAL-02 | Compute Sensitivity Success Rate (SSR) — proportion of correct score changes on meaning-altering perturbations | SSR_directional = proportion where delta direction matches expected direction (decrease for sensitivity perturbations); verified by hand computation |
| EVAL-03 | Compute Attack Success Rate (ASR) — percentage of gaming perturbations that achieve unjustified score increases | ASR_thresholded = proportion where perturbed score crosses passing threshold (was < 0.5, now >= 0.5); "crossing threshold only" definition recommended for academic defensibility |
| EVAL-04 | Break down IVR, SSR, ASR by Protocol B (within-question) and Protocol A (LOQO / cross-question shift) | Compute metrics separately per protocol; robustness_drop = proto_A_value - proto_B_value; already verified computationally |
| EVAL-05 | Break down metrics by perturbation type for granular analysis | Group GradeRecord pairs by PerturbationRecord.type; compute per-type metrics; Dict[str, MetricResult] structure |
| EVAL-06 | Run full evaluation under LOQO cross-validation with metrics per fold | EvaluationEngine loops over protocol_a_splits folds, grades perturbed answers per fold, aggregates per-fold metrics |
| EVAL-07 | Run full evaluation under Protocol B (within-question diagnostic) | EvaluationEngine runs within-question splits from protocol_b_splits, grades per-question, produces per-question metrics |
| EVAL-08 | Dual-form metrics: IVR_flip, IVR_absdelta, SSR_directional, ASR_thresholded; gold unit tests with synthetic mini-dataset hand-computed expected values | MetricCalculator class with all four methods; synthetic_mini_dataset fixture with 3 questions x ~5 answers + hardcoded mock perturbations; all expected values documented with derivation steps |
| GRAD-02 | Hybrid grading model combining handcrafted linguistic features (lexical overlap, length ratio, negation flags) with sentence-transformer embeddings | HybridGrader class: FeatureExtractor (numpy arrays) + SentenceTransformer('all-MiniLM-L6-v2') + LogisticRegression; feature vector = [lexical_overlap, length_ratio, negation_flag] + 384-dim embedding |
| GRAD-05 | All grading models implement a common interface accepting (question, rubric, student_answer) and returning a score | GraderInterface ABC with abstract grade(question, rubric, student_answer) -> GradeResult(label, score, confidence); Pydantic frozen model for GradeResult |
</phase_requirements>

---

## Summary

Phase 2 builds three interconnected components on top of the Phase 1 foundation: (1) a `MetricCalculator` that computes all four dual-form metric variants (IVR_flip, IVR_absdelta, SSR_directional, ASR_thresholded) with zero-denominator safety and per-type breakdown; (2) a `GraderInterface` ABC and `HybridGrader` implementation combining handcrafted linguistic features with sentence-transformer embeddings; and (3) an `EvaluationEngine` that wires the grader and metrics together, runs under both evaluation protocols, and writes results to the Phase 1 structured store. The synthetic mini-dataset and gold unit tests are the validation backbone — all metric formulas have been verified by hand computation before any code is written.

The key dependency decision is `sentence-transformers`. It is not yet installed in the project environment (confirmed by inspection of `infra/versions.py` output: `"sentence-transformers": "not_installed"`). Installing `sentence-transformers==5.1.2` brings in `torch>=2.8.0` and `transformers>=4.41.0` as transitive dependencies. On the dev machine (macOS ARM64 Python 3.9.6) this is feasible — no GPU required for inference with all-MiniLM-L6-v2. `requirements.txt` must be updated accordingly.

The "robustness drop in shift" comparison — a table of (model, perturbation_family, IVR_flip_B, IVR_flip_A, delta_A_minus_B) — is the primary output format for the paper. Per-type granularity at the `PerturbationRecord.type` level (e.g., `synonym_substitution`, `negation_insertion`) is mandatory for Phase 6 heatmap compatibility. Mock perturbations (hardcoded `PerturbationRecord` instances in test fixtures) are the recommended E2E strategy — they validate the wiring loop without coupling to Phase 3's perturbation engine.

**Primary recommendation:** Use sklearn `LogisticRegression` for the hybrid classifier (interpretability advantage for a thesis paper), return `float('nan')` for zero-denominator metrics (standard in ASAG evaluation literature), use the "crossing passing threshold" definition for ASR_thresholded (most conservative and defensible), and use "direction-only" (not "reaching expected grade") for SSR_directional.

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pydantic | 2.12.5 (installed) | GradeResult, MetricResult, EvaluationResult Pydantic models | Phase 1 pattern — frozen models, JSON roundtrip; already in requirements.txt |
| scikit-learn | 1.6.1 (installed) | LogisticRegression for hybrid classifier; StandardScaler for feature normalization | Already installed; LogisticRegression.predict_proba() gives confidence score directly |
| sentence-transformers | 5.1.2 (latest, NOT YET INSTALLED) | Encode student answers and reference answers to 384-dim vectors for HybridGrader | Locked decision — all-MiniLM-L6-v2 is the standard lightweight SBERT model in ASAG literature |
| numpy | 2.0.2 (installed) | Feature vector construction, metric aggregation arrays | Already installed; required by sklearn |
| pytest | 8.4.2 (just installed) | Gold unit tests for metric calculators | Standard Python test framework; just confirmed available on dev machine |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| torch | 2.8.0 (comes with sentence-transformers) | Required by sentence-transformers inference | Installed transitively; no GPU required for all-MiniLM-L6-v2 inference on CPU |
| transformers | 4.57.6 (comes with sentence-transformers) | Required by sentence-transformers | Installed transitively |
| scipy | 1.13.1 (installed) | scipy.sparse for combined feature matrix if needed | Already installed; optional for concatenating dense+sparse features |
| re (stdlib) | Python 3.9 stdlib | Negation flag regex in feature extractor | Built-in; no dependency needed |
| abc (stdlib) | Python 3.9 stdlib | GraderInterface ABC definition | Same pattern as Phase 1 DatasetLoader |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| LogisticRegression | GradientBoostingClassifier | GBT may have slightly better accuracy; LR is more interpretable (coefficients are readable in thesis) and faster to train on small ASAG datasets |
| LogisticRegression | RandomForestClassifier | RF has no natural probability calibration; LR.predict_proba() returns well-calibrated probabilities directly |
| all-MiniLM-L6-v2 | all-mpnet-base-v2 | mpnet is larger (420MB vs 80MB) with marginally better quality; MiniLM is the locked decision |
| all-MiniLM-L6-v2 | paraphrase-multilingual | Multilingual not needed; English-only is in scope |
| float('nan') for zero denominator | 0.0 for zero denominator | Returning 0.0 would artificially deflate metrics and misrepresent "no data available"; NaN signals "undefined" and is the standard in sklearn metrics (e.g., precision_score with zero_division='warn') |

**Installation:**
```bash
pip install sentence-transformers>=5.0  # pulls torch + transformers
pip install pytest>=7.0
```

---

## Architecture Patterns

### Recommended Project Structure

```
src/asag/
├── metrics/
│   ├── __init__.py
│   ├── calculator.py      # MetricCalculator: IVR_flip, IVR_absdelta, SSR_directional, ASR_thresholded
│   └── results.py         # MetricResult, ProtocolComparisonResult Pydantic models
├── graders/
│   ├── __init__.py
│   ├── base.py            # GraderInterface ABC + GradeResult Pydantic model
│   └── hybrid.py          # HybridGrader: FeatureExtractor + SentenceTransformer + LogisticRegression
└── evaluation/
    ├── __init__.py
    └── engine.py          # EvaluationEngine: orchestrates grader + protocols + metrics + storage

tests/
├── metrics/
│   ├── __init__.py
│   ├── test_calculator.py          # Gold unit tests for all 4 metric variants
│   └── synthetic_mini_dataset.py  # Fixture: hand-computed expected values with derivation docs
└── graders/
    ├── __init__.py
    └── test_hybrid.py              # Smoke tests for HybridGrader
```

### Pattern 1: GraderInterface ABC (GRAD-05)

**What:** Abstract base class every grader must implement. Same pattern as Phase 1's `DatasetLoader`.
**When to use:** Every grading model in Phases 2, 4, 5 implements this interface.

```python
# Source: Python 3.9 stdlib abc module docs
from abc import ABC, abstractmethod
from typing import Optional
from pydantic import BaseModel, ConfigDict

class GradeResult(BaseModel):
    """Returned by every grader implementation."""
    model_config = ConfigDict(frozen=True)

    label: str               # e.g. "correct", "partially_correct_incomplete"
    score: float             # normalized [0.0, 1.0] — matches gold_score scale
    confidence: float        # float [0.0, 1.0] — model confidence in this prediction

class GraderInterface(ABC):
    """Common interface for all ASAG grading models.

    Input:  (question: str, rubric: Optional[str], student_answer: str)
    Output: GradeResult with label, score, and confidence

    All phases implement this interface so EvaluationEngine is grader-agnostic.
    """

    @abstractmethod
    def grade(
        self,
        question: str,
        rubric: Optional[str],
        student_answer: str,
    ) -> GradeResult:
        """Grade a student answer in context of the question and rubric."""
        ...

    @property
    @abstractmethod
    def grader_name(self) -> str:
        """Human-readable name for logging and result labelling."""
        ...
```

### Pattern 2: MetricCalculator with Zero-Denominator Safety (EVAL-01 through EVAL-08)

**What:** Pure functions operating on lists of (original_score, perturbed_score) pairs. Returns `float('nan')` when input list is empty — signals "no data" rather than "zero violations."
**When to use:** Called per-fold (EVAL-06) and per-question (EVAL-07); aggregated with `pandas` or manual dict; NaN values are excluded from aggregation.

```python
# Source: hand-computed verification (see Common Pitfalls section for derivation)
import math
from typing import List, Tuple, Optional

ScorePair = Tuple[float, float]  # (original_score, perturbed_score)

PASSING_THRESHOLD = 0.5  # partially_correct_incomplete is passing

def ivr_flip(pairs: List[ScorePair]) -> float:
    """IVR_flip: proportion of invariance pairs where any score change occurred.

    LOCKED: ANY score change counts as violation (strictest definition).
    Returns float('nan') when pairs is empty (no invariance perturbations available).

    Expected derivation for test fixture:
        pairs = [(1.0, 0.5), (1.0, 1.0), (0.5, 0.0), (0.5, 0.5), (0.0, 0.0)]
        flips = [True, False, True, False, False] = 2 violations
        IVR_flip = 2 / 5 = 0.4
    """
    if not pairs:
        return float('nan')
    return sum(1 for orig, pert in pairs if orig != pert) / len(pairs)

def ivr_absdelta(pairs: List[ScorePair]) -> float:
    """IVR_absdelta: mean absolute score delta on invariance perturbations.

    Returns float('nan') when pairs is empty.

    Expected derivation:
        pairs = [(1.0, 0.5), (1.0, 1.0), (0.5, 0.0), (0.5, 0.5), (0.0, 0.0)]
        abs_deltas = [0.5, 0.0, 0.5, 0.0, 0.0]
        IVR_absdelta = (0.5 + 0 + 0.5 + 0 + 0) / 5 = 0.2
    """
    if not pairs:
        return float('nan')
    return sum(abs(o - p) for o, p in pairs) / len(pairs)

def ssr_directional(pairs: List[ScorePair]) -> float:
    """SSR_directional: proportion of sensitivity pairs where score DECREASED.

    DISCRETION RESOLVED: direction-only criterion — success iff perturbed < original.
    Rationale: sensitivity perturbations (negation, deletion) should lower the score;
    requiring "reaching expected grade" is overly strict since we have no fixed
    expected grade per perturbation — only the direction is knowable from semantics.
    Returns float('nan') when pairs is empty.

    Expected derivation:
        pairs = [(1.0, 0.5), (1.0, 1.0), (0.5, 0.0)]
        correct_direction = [True, False, True] = 2 successes
        SSR_directional = 2 / 3 ≈ 0.6667
    """
    if not pairs:
        return float('nan')
    return sum(1 for orig, pert in pairs if pert < orig) / len(pairs)

def asr_thresholded(pairs: List[ScorePair]) -> float:
    """ASR_thresholded: proportion of gaming pairs where score crosses passing threshold.

    DISCRETION RESOLVED: "crossing threshold only" — success iff was below 0.5
    AND now at or above 0.5. Rationale: the most conservative and academically
    defensible definition; avoids counting already-passing answers that got a
    slightly higher score as "attacks succeeded." PASSING_THRESHOLD = 0.5
    (partially_correct_incomplete level).
    Returns float('nan') when pairs is empty.

    Expected derivation:
        pairs = [(0.0, 0.5), (0.0, 1.0), (0.5, 1.0)]
        crossed = [True, True, False]  # index 2: was already passing
        ASR_thresholded = 2 / 3 ≈ 0.6667
    """
    if not pairs:
        return float('nan')
    return sum(
        1 for orig, pert in pairs
        if orig < PASSING_THRESHOLD and pert >= PASSING_THRESHOLD
    ) / len(pairs)
```

### Pattern 3: Per-Type Metric Breakdown (EVAL-05)

**What:** Group (original_score, perturbed_score) pairs by `PerturbationRecord.type` before computing metrics. Returns a nested dict keyed by perturbation type.
**When to use:** Called after collecting all grade pairs for a fold or question-set; feeds Phase 6 heatmap generation.

```python
from typing import Dict
from collections import defaultdict

def compute_metrics_by_type(
    grade_pairs: List[Tuple[str, str, float, float]],  # (answer_id, perturb_type, orig_score, pert_score)
    family: str,  # "invariance" | "sensitivity" | "gaming"
) -> Dict[str, Dict[str, float]]:
    """Compute all relevant metrics per perturbation type within a family.

    Returns:
        {
          "synonym_substitution": {"IVR_flip": 0.15, "IVR_absdelta": 0.08},
          "surface_rewrite":      {"IVR_flip": 0.28, "IVR_absdelta": 0.18},
          ...
        }
    """
    by_type: Dict[str, List[ScorePair]] = defaultdict(list)
    for _, perturb_type, orig, pert in grade_pairs:
        by_type[perturb_type].append((orig, pert))

    results = {}
    for ptype, pairs in by_type.items():
        if family == "invariance":
            results[ptype] = {
                "IVR_flip": ivr_flip(pairs),
                "IVR_absdelta": ivr_absdelta(pairs),
            }
        elif family == "sensitivity":
            results[ptype] = {"SSR_directional": ssr_directional(pairs)}
        elif family == "gaming":
            results[ptype] = {"ASR_thresholded": asr_thresholded(pairs)}
    return results
```

### Pattern 4: HybridGrader Feature Extraction (GRAD-02)

**What:** Combines three handcrafted linguistic features with a 384-dim sentence-transformer embedding into a single feature vector. Trained with `LogisticRegression` on LOQO fold training sets.
**Feature set decision:** Lexical overlap (F1 between student tokens and reference tokens) + length ratio + negation flag + cosine_similarity_to_reference. Embedding of student answer. This matches the ASAG baseline literature (Filighera 2024 uses similar features) and extends it with SBERT embeddings for semantic similarity.

```python
# Source: sentence-transformers official docs + sklearn Pipeline docs
import re
import numpy as np
from typing import List, Optional
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

NEGATION_PATTERN = re.compile(
    r'\b(not|never|no|cannot|can\'t|won\'t|doesn\'t|isn\'t|aren\'t|'
    r'wasn\'t|weren\'t|don\'t|didn\'t|haven\'t|hadn\'t|shouldn\'t|'
    r'wouldn\'t|couldn\'t)\b',
    re.IGNORECASE
)

class FeatureExtractor:
    """Extract handcrafted linguistic features from a student answer.

    Features:
        0: lexical_overlap   — F1 between student tokens and reference tokens
                               = 2 * precision * recall / (precision + recall)
        1: length_ratio      — len(student.split()) / len(reference.split())
                               clipped to [0.0, 3.0] to avoid outlier blow-up
        2: negation_flag     — 1.0 if negation word present in student answer, 0.0 otherwise
        3: ref_token_recall  — proportion of reference tokens present in student answer

    Returns np.ndarray of shape (4,).
    """

    def extract(self, student_answer: str, reference_answer: str) -> np.ndarray:
        student_tokens = set(student_answer.lower().split())
        ref_tokens = set(reference_answer.lower().split())

        if not ref_tokens:
            return np.zeros(4)

        precision = len(student_tokens & ref_tokens) / max(len(student_tokens), 1)
        recall = len(student_tokens & ref_tokens) / len(ref_tokens)
        f1 = 2 * precision * recall / max(precision + recall, 1e-9)

        length_ratio = min(len(student_answer.split()) / max(len(reference_answer.split()), 1), 3.0)
        negation_flag = 1.0 if NEGATION_PATTERN.search(student_answer) else 0.0
        ref_recall = recall  # same as recall above

        return np.array([f1, length_ratio, negation_flag, ref_recall], dtype=float)
```

### Pattern 5: HybridGrader Class (GRAD-02 + GRAD-05)

**What:** Implements `GraderInterface`; wraps `FeatureExtractor` + `SentenceTransformer` + `LogisticRegression` into a single `fit/grade` API.
**Training:** `fit(train_answers, train_questions)` — called once per LOQO fold; uses `predict_proba()` for confidence score.

```python
# Source: sentence-transformers docs; sklearn LogisticRegression docs
from sentence_transformers import SentenceTransformer

class HybridGrader(GraderInterface):
    """Hybrid grader combining handcrafted features + SBERT embeddings.

    Architecture:
        feature_vector = [f1_overlap, length_ratio, negation_flag, ref_recall]
                         + SentenceTransformer('all-MiniLM-L6-v2').encode(student_answer)
        = 4 + 384 = 388-dim input to LogisticRegression

    Classifier: LogisticRegression(max_iter=500, C=1.0)
    Scaler: StandardScaler on the full 388-dim feature vector (before LR)
    """
    MODEL_ID = "all-MiniLM-L6-v2"
    LABEL_ORDER = ["correct", "partially_correct_incomplete",
                   "contradictory", "irrelevant", "non_domain"]

    def __init__(self) -> None:
        self._extractor = FeatureExtractor()
        self._encoder = SentenceTransformer(self.MODEL_ID)
        self._pipeline: Optional[Pipeline] = None

    @property
    def grader_name(self) -> str:
        return "hybrid_logreg_minilm"

    def fit(
        self,
        train_answers: List[AnswerRecord],
        question_lookup: Dict[str, QuestionRecord],
    ) -> None:
        """Fit the LogisticRegression on a training fold.

        Args:
            train_answers:   AnswerRecords for the training partition.
            question_lookup: Dict mapping question_id -> QuestionRecord
                             (used to look up reference_answers).
        """
        X, y = self._build_features(train_answers, question_lookup)
        self._pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("lr", LogisticRegression(
                max_iter=500,
                C=1.0,
                multi_class="multinomial",
                random_state=42,
            ))
        ])
        self._pipeline.fit(X, y)

    def grade(
        self,
        question: str,
        rubric: Optional[str],
        student_answer: str,
        reference_answer: str = "",
    ) -> GradeResult:
        """Grade a student answer. Pipeline must be fit first."""
        if self._pipeline is None:
            raise RuntimeError("HybridGrader must be fit before calling grade()")
        x = self._build_single_feature(student_answer, reference_answer)
        label = self._pipeline.predict([x])[0]
        proba = self._pipeline.predict_proba([x])[0]
        confidence = float(max(proba))
        score = LABEL_TO_SCORE.get(label, 0.0)
        return GradeResult(label=label, score=score, confidence=confidence)

    def _build_single_feature(self, student: str, reference: str) -> np.ndarray:
        handcrafted = self._extractor.extract(student, reference)
        embedding = self._encoder.encode(student, show_progress_bar=False)
        return np.concatenate([handcrafted, embedding])

    def _build_features(
        self,
        answers: List[AnswerRecord],
        question_lookup: Dict[str, QuestionRecord],
    ) -> Tuple[np.ndarray, List[str]]:
        X_list, y_list = [], []
        for ans in answers:
            q = question_lookup.get(ans.question_id)
            ref = q.reference_answers[0] if q and q.reference_answers else ""
            X_list.append(self._build_single_feature(ans.student_answer, ref))
            y_list.append(ans.gold_label)
        return np.vstack(X_list), y_list
```

### Pattern 6: Synthetic Mini-Dataset and Gold Unit Tests (EVAL-08)

**What:** A self-contained synthetic dataset (3 questions, 5-7 answers each, 3-5 perturbations per answer per family) with hand-computed expected metric values and step-by-step derivation documentation. Tests must pass without tolerance relaxation (exact float equality or `assert result == pytest.approx(expected, abs=1e-9)`).
**Grade scale decision:** Use simplified 3-level scale (correct=1.0, partial=0.5, incorrect=0.0) for the synthetic dataset. This covers the full numeric range while being simpler to reason about than the full 5-way SemEval scheme. The 5-way scale maps to the same three float values anyway (contradictory/irrelevant/non_domain all → 0.0), so 3-level is equivalent for metric computation.

```python
# tests/metrics/synthetic_mini_dataset.py
"""
Synthetic mini-dataset for gold unit tests.

Design:
  - 3 questions, 5 answers each = 15 answers
  - Per answer: 2 invariance + 2 sensitivity + 1 gaming = 5 perturbations
  - Total: 15 x 5 = 75 PerturbationRecords

Grade scale: {correct: 1.0, partial: 0.5, incorrect: 0.0}

All expected values are documented with step-by-step derivations below
each test function. No tolerance relaxation needed: the scale is exactly
representable in IEEE 754 double precision (0.0, 0.5, 1.0).

Derivation format required for thesis:
    pairs = [(1.0, 0.5), (1.0, 1.0), ...]
    flips = [True, False, ...]  # show each step
    IVR_flip = k_flips / n_pairs = 2/4 = 0.5
"""
```

### Pattern 7: EvaluationEngine (EVAL-04, EVAL-06, EVAL-07)

**What:** Orchestrates the full evaluation loop. Takes a grader, a dataset, and protocols config. Returns structured `EvaluationResult` saved to the run directory via Phase 1's `save_json`.
**Key responsibility:** Tracks which answers are in train vs test for each fold, grades only test answers, groups perturbations by their source `answer_id`.

```python
class EvaluationEngine:
    """Runs the full evaluation loop under Protocol A and/or Protocol B.

    Usage:
        engine = EvaluationEngine(grader=HybridGrader(), corpus="beetle")
        result = engine.run(questions, answers, perturbations, protocols=["A", "B"])
        save_json(result.model_dump(), run_dir / "evaluation_results.json")
    """

    def run(
        self,
        questions: List[QuestionRecord],
        answers: List[AnswerRecord],
        perturbations: List[PerturbationRecord],
        protocols: List[str],  # ["A"], ["B"], or ["A", "B"]
    ) -> "EvaluationResult":
        ...

    def _grade_perturbations(
        self,
        test_answers: List[AnswerRecord],
        perturbations: List[PerturbationRecord],
        question_lookup: Dict[str, QuestionRecord],
    ) -> List[Tuple[str, str, float, float]]:
        """Grade each perturbation and return (answer_id, perturb_type, orig_score, pert_score)."""
        ...
```

### Pattern 8: Robustness Drop Comparison (EVAL-04)

**What:** Side-by-side table showing Protocol A vs Protocol B metric values and their delta. Protocol A (LOQO) measures cross-question generalization; Protocol B measures in-distribution vulnerability. Positive delta means the model degrades under distribution shift.

```python
from typing import NamedTuple

class RobustnessDropRow(NamedTuple):
    """One row in the robustness-drop comparison table."""
    grader_name: str
    perturbation_family: str
    perturbation_type: str        # "all" for family-level, specific type for per-type
    metric_name: str              # "IVR_flip", "IVR_absdelta", "SSR_directional", "ASR_thresholded"
    proto_b_value: float          # within-question (in-distribution)
    proto_a_value: float          # LOQO (cross-question shift)
    delta_a_minus_b: float        # robustness drop: positive = worse under shift
```

### Anti-Patterns to Avoid

- **Computing metrics before checking for empty input:** Always check `if not pairs: return float('nan')`. A zero denominator returning `0.0` will silently make a grader look perfect on missing families.
- **Fitting the HybridGrader on all data, then testing on a subset:** Fit MUST happen inside the LOQO loop on training answers only. SentenceTransformer encoding is OK to run on all data (it's stateless), but `LogisticRegression.fit()` must only see training answers.
- **Using `grade()` before `fit()`:** The `HybridGrader.grade()` method must raise `RuntimeError` if called before `fit()`. This prevents silent failures when the engine is run without training.
- **Aggregating NaN values in mean computations:** When computing fold-average metrics, skip `float('nan')` values. Use `[v for v in values if not math.isnan(v)]` before averaging.
- **String label comparison for score change detection:** Metric logic must use `gold_score` float values (0.0, 0.5, 1.0), not string labels. Two different string labels can map to the same float (e.g., contradictory=0.0 and irrelevant=0.0).
- **Python 3.9 type annotation violations:** Continue using `from typing import List, Dict, Tuple, Optional` — do not use `list[str]` or `dict[str, float]` built-in generics (Python 3.10+ only).

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Sentence embedding | Custom word2vec averaging or TF-IDF vectors | `SentenceTransformer('all-MiniLM-L6-v2').encode()` | all-MiniLM-L6-v2 is the locked decision; hand-rolled embeddings would be lower quality and harder to justify in the paper |
| Feature normalization before LR | Manual z-score calculation | `sklearn.preprocessing.StandardScaler` inside a `Pipeline` | Pipeline ensures scaler is fit on training data only, never leaks test statistics |
| Multi-class probability output | Manual softmax on raw logit values | `LogisticRegression.predict_proba()` | Returns well-calibrated probabilities directly; `confidence = max(predict_proba())` |
| Metric aggregation over NaN | Custom NaN-skipping aggregator | `[v for v in values if not math.isnan(v)]` then `sum/len` | Simple and explicit; pandas mean() skips NaN by default but adds a dependency just for this |
| Gold test fixture management | Inline data in each test function | `pytest` fixtures with `@pytest.fixture` and a dedicated `synthetic_mini_dataset.py` | Fixtures are reused across test functions; centralized derivation documentation |

**Key insight:** The hybrid grader is intentionally a weak baseline — its academic value is demonstrating that the evaluation framework works, not beating SOTA. All engineering effort should go into making the metrics correct and the interfaces clean, not into squeezing accuracy from the grader.

---

## Common Pitfalls

### Pitfall 1: Score Comparison Float Equality

**What goes wrong:** Using `orig_score == pert_score` when both are supposed to be from the set {0.0, 0.5, 1.0} but one was computed via arithmetic and carries floating-point error (e.g., `3/6 = 0.5000000000000001` in some implementations).
**Why it happens:** `gold_score` values from the Phase 1 schema come from `LABEL_TO_SCORE` (dict lookup, exact floats). But a custom grader might compute a score via `predict_proba` rounding. If a grader returns `0.5000000000000001`, the IVR_flip comparison `orig != pert` triggers incorrectly.
**How to avoid:** In the `MetricCalculator`, round scores to a fixed decimal precision (e.g., `round(score, 6)`) when reading from `GradeResult`. Document this rounding in the calculator docstring.
**Warning signs:** Spurious IVR_flip=1.0 on perfectly stable graders; unit tests failing by tiny epsilon differences.

### Pitfall 2: HybridGrader Leakage via Shared SentenceTransformer State

**What goes wrong:** `SentenceTransformer` is instantiated once and shared across folds. Since it is a stateless encoder (no fitting), this is fine — BUT if someone caches embeddings in a dict keyed by text, they may inadvertently cache test-set embeddings computed before the fold split, effectively pre-computing features for test answers.
**Why it happens:** Premature optimization — trying to avoid re-encoding the same text multiple times.
**How to avoid:** Do not cache embeddings globally. Encode training answers during `fit()`, encode test/perturbation answers lazily in `grade()`. Re-encoding the same text across folds is wasteful but correct; caching globally is fast but risks leakage.
**Warning signs:** Suspiciously identical performance across LOQO folds; test fold grading runs "instantly."

### Pitfall 3: Perturbation-Answer Join Mismatch

**What goes wrong:** The evaluation engine grades perturbations whose `answer_id` refers to a test-set answer, but the perturbation was generated before the LOQO split. If a training-set `answer_id` appears in the perturbation list for a test fold, those perturbations are graded against the wrong fold.
**Why it happens:** In Phase 2, mock perturbations are created at dataset-level (before splitting). The engine must filter perturbations to only those whose `answer_id` is in the current fold's test set.
**How to avoid:** In `EvaluationEngine._grade_perturbations()`, always filter `perturbations` to `[p for p in perturbations if p.answer_id in test_answer_id_set]` before proceeding.
**Warning signs:** More perturbation-answer pairs than expected; metrics computed over training-set answers.

### Pitfall 4: sentence-transformers Slow First Run (Model Download)

**What goes wrong:** The first call to `SentenceTransformer('all-MiniLM-L6-v2')` triggers an ~80MB download from HuggingFace Hub. On a slow connection or without internet access, this silently hangs or fails.
**Why it happens:** HuggingFace Hub downloads models lazily on first use.
**How to avoid:** Document in the Phase 2 notebook that `sentence_transformers` must be installed and the model downloaded before running. Add a one-line download check: `SentenceTransformer('all-MiniLM-L6-v2')` as a smoke test at notebook startup.
**Warning signs:** `OSError: [Errno 104] Connection reset by peer` during `HybridGrader` initialization.

### Pitfall 5: ASR Thresholded Definition Ambiguity

**What goes wrong:** If "increase >= 1 level" is used instead of "crossing threshold", already-passing answers that receive a slight score increase are counted as successful attacks, inflating ASR.
**Why it happens:** ASAG literature uses both definitions without clear consensus; the "level increase" definition is more permissive.
**How to avoid:** RESOLVED — use "crossing threshold only" (was < 0.5, now >= 0.5). Document the rationale in the metric docstring: "counts only attacks that push a failing answer to passing, which represents a meaningful grade inflation."
**Warning signs:** ASR values > 0.8 on clearly non-adversarial perturbations; ASR and SSR values that seem to count the same events.

### Pitfall 6: SSR_directional Neutral Outcomes

**What goes wrong:** A sensitivity perturbation where `pert_score == orig_score` (no change) is silently counted as a failure (correct direction = False) in a naive implementation. But this conflates "direction wrong" with "no change."
**Why it happens:** `pert < orig` evaluates to False when `pert == orig`, so no-change cases are counted as failures.
**How to avoid:** RESOLVED — no-change is correctly classified as a failure for SSR_directional. A sensitivity perturbation that doesn't change the score represents a sensitivity insensitivity — the grader failed to detect the meaning change. So counting neutral outcomes as failures is semantically correct.
**Warning signs:** If SSR_directional seems too low, verify the perturbation generator is actually generating meaningful sensitivity perturbations.

### Pitfall 7: requirements.txt Missing sentence-transformers

**What goes wrong:** `sentence-transformers` is not in `requirements.txt`. A clean install of the project fails when importing `HybridGrader`.
**Why it happens:** `sentence-transformers` was not in the project environment when Phase 1 was built; it must be added for Phase 2.
**How to avoid:** Add `sentence-transformers>=5.0` to `requirements.txt`. Note that this transitively requires `torch>=2.8.0` — which is a large (~500MB) download. Document this in the Phase 2 notebook header.
**Warning signs:** `ModuleNotFoundError: No module named 'sentence_transformers'` when running the hybrid grader.

---

## Code Examples

Verified patterns from official sources:

### MetricCalculator with Exact Hand-Computed Expected Values

```python
# Source: verified by manual computation (see derivation inline)
import math
import pytest

class MetricCalculator:
    """Stateless metric computation. All methods are pure functions."""

    PASSING_THRESHOLD: float = 0.5

    def ivr_flip(self, pairs: List[ScorePair]) -> float:
        if not pairs:
            return float('nan')
        return sum(1 for o, p in pairs if o != p) / len(pairs)

    def ivr_absdelta(self, pairs: List[ScorePair]) -> float:
        if not pairs:
            return float('nan')
        return sum(abs(o - p) for o, p in pairs) / len(pairs)

    def ssr_directional(self, pairs: List[ScorePair]) -> float:
        if not pairs:
            return float('nan')
        return sum(1 for o, p in pairs if p < o) / len(pairs)

    def asr_thresholded(self, pairs: List[ScorePair]) -> float:
        if not pairs:
            return float('nan')
        return sum(
            1 for o, p in pairs
            if o < self.PASSING_THRESHOLD and p >= self.PASSING_THRESHOLD
        ) / len(pairs)


# Gold unit test — no tolerance relaxation needed (exact IEEE 754 values)
def test_ivr_flip_gold():
    """
    Derivation:
        pairs = [(1.0, 0.5), (1.0, 1.0), (0.5, 0.0), (0.5, 0.5), (0.0, 0.0)]
        pair 0: 1.0 != 0.5 → flip=True
        pair 1: 1.0 == 1.0 → flip=False
        pair 2: 0.5 != 0.0 → flip=True
        pair 3: 0.5 == 0.5 → flip=False
        pair 4: 0.0 == 0.0 → flip=False
        IVR_flip = 2/5 = 0.4 (exactly representable in float64)
    """
    calc = MetricCalculator()
    pairs = [(1.0, 0.5), (1.0, 1.0), (0.5, 0.0), (0.5, 0.5), (0.0, 0.0)]
    assert calc.ivr_flip(pairs) == pytest.approx(0.4, abs=1e-9)

def test_asr_thresholded_gold():
    """
    Derivation:
        pairs = [(0.0, 0.5), (0.0, 1.0), (0.5, 1.0)]
        threshold = 0.5
        pair 0: orig=0.0 < 0.5 AND pert=0.5 >= 0.5 → success
        pair 1: orig=0.0 < 0.5 AND pert=1.0 >= 0.5 → success
        pair 2: orig=0.5 NOT < 0.5 (already passing) → failure
        ASR_thresholded = 2/3 ≈ 0.6667
    """
    calc = MetricCalculator()
    pairs = [(0.0, 0.5), (0.0, 1.0), (0.5, 1.0)]
    assert calc.asr_thresholded(pairs) == pytest.approx(2/3, abs=1e-9)

def test_empty_returns_nan():
    calc = MetricCalculator()
    assert math.isnan(calc.ivr_flip([]))
    assert math.isnan(calc.ivr_absdelta([]))
    assert math.isnan(calc.ssr_directional([]))
    assert math.isnan(calc.asr_thresholded([]))
```

### GradeResult Pydantic Model (Frozen)

```python
# Source: Pydantic v2 docs + Phase 1 pattern (ConfigDict frozen=True)
from pydantic import BaseModel, ConfigDict, field_validator

class GradeResult(BaseModel):
    """Immutable result returned by every grader."""
    model_config = ConfigDict(frozen=True)

    label: str
    score: float    # normalized [0.0, 1.0]
    confidence: float  # [0.0, 1.0]

    @field_validator('score', 'confidence')
    @classmethod
    def must_be_in_unit_interval(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError(f"score/confidence must be in [0.0, 1.0], got {v}")
        return v
```

### sentence-transformers Encoding (Verified API)

```python
# Source: sentence-transformers 5.x official docs
# https://www.sbert.net/docs/quickstart.html
from sentence_transformers import SentenceTransformer
import numpy as np

encoder = SentenceTransformer('all-MiniLM-L6-v2')

# Single string
embedding = encoder.encode("The bulb lights up.", show_progress_bar=False)
# Returns: np.ndarray of shape (384,), dtype float32

# Batch (more efficient)
embeddings = encoder.encode(
    ["The bulb lights up.", "Current flows through the circuit."],
    batch_size=32,
    show_progress_bar=False,
)
# Returns: np.ndarray of shape (2, 384), dtype float32

# Convert to float64 for sklearn consistency
embedding = embedding.astype(np.float64)
```

### MetricResult Pydantic Model

```python
from typing import Optional, Dict

class MetricResult(BaseModel):
    """Stores all metric values for one (grader, protocol, perturbation_family) triple."""
    model_config = ConfigDict(frozen=True)

    grader_name: str
    protocol: str            # "A" or "B"
    family: str              # "invariance", "sensitivity", "gaming"
    n_pairs: int             # number of (original, perturbed) pairs
    # Family-specific metrics — None if not applicable for this family
    ivr_flip: Optional[float] = None
    ivr_absdelta: Optional[float] = None
    ssr_directional: Optional[float] = None
    asr_thresholded: Optional[float] = None
    # Per-type breakdown: {"synonym_substitution": {"IVR_flip": 0.15, ...}, ...}
    by_type: Dict[str, Dict[str, float]] = {}
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| TF-IDF + cosine similarity as sole similarity feature | sentence-transformer embeddings (all-MiniLM-L6-v2) | ~2021 (SBERT papers) | Captures semantic similarity beyond lexical overlap; crucial for invariance perturbation testing where surface form changes |
| Single-metric accuracy/QWK for ASAG evaluation | Dual-form metrics (IVR_flip + IVR_absdelta; SSR_directional; ASR_thresholded) | This project (novel contribution) | Distinguishes binary invariance violations from magnitude of instability; separates in-distribution from cross-question vulnerability |
| Single evaluation protocol (train/test split) | Dual protocol (Protocol A LOQO + Protocol B within-question) | CheckList (Ribeiro et al. 2020) analogous methodology | Enables robustness_drop metric: shows how much worse a model performs under distribution shift |
| Pydantic v1 (`.dict()`, `.json()`) | Pydantic v2 (`model_dump()`, `model_dump_json()`) | Pydantic 2.0 (mid-2023) | Already in use from Phase 1; v2 frozen=True prevents metric record mutation |

**Deprecated/outdated:**
- `sentence_transformers.SentenceTransformer.encode()` with `convert_to_tensor=True`: returns a PyTorch tensor. Use `convert_to_numpy=True` (or default, which is numpy in v5.x) to get `np.ndarray` for sklearn compatibility.
- `sklearn.linear_model.LogisticRegression(multi_class='ovr')`: use `multi_class='multinomial'` for 5-class ASAG grading; `ovr` underperforms on imbalanced multi-class tasks.

---

## Open Questions

1. **SSR_directional: reference direction for gaming family**
   - What we know: Gaming perturbations attempt to inflate scores. SSR_directional is defined for sensitivity perturbations (expected direction: decrease).
   - What's unclear: Should gaming perturbations also have a "direction" expectation? If yes, the expected direction would be "grader should NOT increase score" — which is what ASR_thresholded already captures.
   - Recommendation: Keep metric families separate. SSR_directional applies ONLY to sensitivity perturbations. ASR_thresholded is the gaming-family metric. Do not combine.

2. **Confidence score from HybridGrader on 5-class vs 3-class output**
   - What we know: The hybrid grader is trained on 5-class SemEval labels. `predict_proba()` returns 5-class probabilities. Confidence = max probability.
   - What's unclear: Whether to map predicted labels through the 3-level score mapping or keep the 5-label output for GradeResult.
   - Recommendation: Keep the full 5-class labels in `GradeResult.label` (preserves information for Phase 6 reporting). Set `GradeResult.score = LABEL_TO_SCORE[label]` for metric computation. The 5-class information is richer than 3-class and enables future analysis.

3. **Mock perturbation count for E2E validation**
   - What we know: The E2E test must run on "BOTH Beetle AND SciEntsBank corpora." Full corpora have thousands of answers.
   - What's unclear: Whether the E2E test should run on a subset (first N questions) or all data.
   - Recommendation: Run E2E on a 3-question subset of Beetle and a 3-question subset of SciEntsBank with 2-3 mock perturbations per answer per family. Document subset selection criteria (first questions alphabetically for reproducibility). Full corpus runs are integration tests, not unit tests.

4. **HybridGrader training data size for LOQO validation**
   - What we know: Beetle has 56 questions; each LOQO fold trains on 55 questions' worth of answers (~3800 answers). SciEntsBank has 197 questions.
   - What's unclear: Whether LogisticRegression needs class balancing (`class_weight='balanced'`) given that "correct" is overrepresented in Beetle (~42% of answers).
   - Recommendation: Use `class_weight='balanced'` by default in `LogisticRegression`. Log class distribution per fold during training to document the imbalance. This is a standard ASAG paper practice.

---

## Sources

### Primary (HIGH confidence)

- Phase 1 codebase (read directly): `src/asag/schema/records.py`, `src/asag/schema/grade.py`, `src/asag/infra/config.py`, `src/asag/infra/storage.py`, `src/asag/splitters/protocol_a.py`, `src/asag/splitters/protocol_b.py` — confirmed field names, types, import paths, Python 3.9 patterns
- `PYTHONPATH=src python3 -c "from asag.infra.versions import get_library_versions(); ..."` — confirmed installed versions: pydantic 2.12.5, sklearn 1.6.1, numpy 2.0.2, sentence-transformers NOT installed
- `pip install sentence-transformers --dry-run` — confirmed would install: sentence-transformers 5.1.2, torch 2.8.0, transformers 4.57.6
- `python3 -m pytest --version` — confirmed pytest 8.4.2 available after `pip3 install --user pytest`
- Hand-computed metric verification (Python 3.9 arithmetic): IVR_flip=0.4, IVR_absdelta=0.2, SSR_directional=0.6667, ASR_thresholded (crossing threshold)=0.6667 — all verified correct
- Python 3.9 stdlib docs: `abc.ABC`, `abc.abstractmethod`, `re` module, `math.isnan()`

### Secondary (MEDIUM confidence)

- sentence-transformers PyPI metadata (pypi.org/project/sentence-transformers/5.1.2): version 5.1.2 is latest as of 2026-02-21
- CheckList (Ribeiro et al. 2020, ACL): methodological precursor for INV/DIR/MFT test types mapping to IVR/SSR/ASR — verified from Phase 0.1 bibliography decisions in STATE.md
- ASAG2024 benchmark paper (arxiv 2409.18596): normalized [0,1] scale confirmed as current standard — verified from Phase 1 RESEARCH.md

### Tertiary (LOW confidence — verify before use)

- all-MiniLM-L6-v2 model size (~80MB): from sentence-transformers documentation/model card; not directly re-verified
- `LogisticRegression(multi_class='multinomial')` performance advantage on 5-class ASAG: standard ML practice; not benchmarked on Beetle specifically

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all packages verified by version output from the actual dev machine; pytest confirmed installed
- Metric formulas: HIGH — all four metric variants verified by Python 3.9 arithmetic; zero-denominator behavior tested
- Architecture patterns: HIGH — directly adapted from Phase 1 patterns (same ABC approach, same Pydantic frozen model pattern, same PYTHONPATH=src convention)
- HybridGrader design: HIGH — sentence-transformers API patterns verified; sklearn Pipeline + LogisticRegression is standard; feature set is defensible from ASAG literature
- E2E loop design: MEDIUM — EvaluationEngine structure is by design, not yet verified by running; mock perturbation approach verified via PerturbationRecord instantiation test
- GradeResult field validator: HIGH — Pydantic v2 `field_validator` pattern confirmed from official docs

**Research date:** 2026-02-21
**Valid until:** 2026-08-21 (stable libraries; sentence-transformers 5.x API may change in minor versions)
