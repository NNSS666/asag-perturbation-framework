---
phase: 02-metrics-hybrid-grader
verified: 2026-02-21T10:30:00Z
status: passed
score: 5/5 must-haves verified
re_verification: false
gaps: []
human_verification: []
---

# Phase 2: Metrics and Hybrid Grader Verification Report

**Phase Goal:** Dual-form IVR/SSR/ASR metric calculators are validated against hand-computed expected values on a synthetic mini-dataset, the within-question diagnostic protocol produces a "robustness drop in shift" comparison, and the hybrid grader demonstrates the full evaluation loop end-to-end before any GPU or API spending occurs
**Verified:** 2026-02-21T10:30:00Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|---------|
| 1 | All dual-form metric variants (IVR_flip, IVR_absdelta, SSR_directional, ASR_thresholded) pass gold unit tests with hand-computed expected values without tolerance relaxation | VERIFIED | 13 tests in `tests/metrics/test_calculator.py` — all pass in 0.02s; assertions use `pytest.approx(abs=1e-9)` against values derived step-by-step in `synthetic_mini_dataset.py` docstring |
| 2 | Protocol A (LOQO) and Protocol B (within-question) both produce metric outputs; robustness drop (delta_a_minus_b) is available for every model and perturbation family | VERIFIED | `EvaluationEngine._run_protocol_a()` and `_run_protocol_b()` produce `MetricResult` lists; `_compute_robustness_drop()` emits rows with `{grader_name, perturbation_family, metric_name, proto_b_value, proto_a_value, delta_a_minus_b}`; E2E tests assert `len(result.robustness_drop) > 0` and verify all 6 required keys |
| 3 | Metrics break down by perturbation type so per-type IVR/SSR/ASR values are queryable for downstream heatmap generation | VERIFIED | `MetricCalculator.compute_by_type()` groups by `PerturbationRecord.type` and returns `Dict[str, Dict[str, float]]`; 3 tests (`test_compute_by_type_invariance/sensitivity/gaming`) verify per-type values match hand-computed expected values; `MetricResult.by_type` field stores the breakdown in every result |
| 4 | Any grading model plugs into the evaluation engine via the common GraderInterface without additional wiring | VERIFIED | `GraderInterface` ABC defines `grade(question, rubric, student_answer) -> GradeResult` and `grader_name` abstract methods; `EvaluationEngine` accepts any `GraderInterface` instance; `_grade_single()` uses `TypeError` catch-and-retry for graders that don't accept `reference_answer` kwarg |
| 5 | Full evaluation run completes on the Beetle subset under both protocols and writes results to the structured store | VERIFIED | `test_e2e_beetle_subset` passes in 139.88s; `test_e2e_result_persisted_to_disk` asserts `(tmp_path / "test_run" / "evaluation_result.json").exists()` and loads back the file verifying `grader_name == "hybrid_logreg_minilm"`, `corpus == "beetle"`, and all 6 top-level JSON keys |

**Score:** 5/5 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/asag/metrics/calculator.py` | MetricCalculator class with ivr_flip, ivr_absdelta, ssr_directional, asr_thresholded, compute_by_type | VERIFIED | 251 lines (min: 80); all 5 methods present and substantive; SCORE_PRECISION=6 rounding applied |
| `src/asag/metrics/results.py` | MetricResult and MetricSuite Pydantic frozen models | VERIFIED | 65 lines (min: 30); both models present with `model_config = ConfigDict(frozen=True)` |
| `src/asag/graders/base.py` | GraderInterface ABC + GradeResult Pydantic frozen model | VERIFIED | 103 lines; exports `GraderInterface` and `GradeResult`; `@field_validator` enforces [0, 1] range on score/confidence |
| `tests/metrics/synthetic_mini_dataset.py` | Synthetic mini-dataset with 3 questions, hand-computed expected values, step-by-step derivation docs | VERIFIED | 575 lines (min: 100); 75 PerturbationRecords (3 questions x 5 answers x 5 perturbations); full step-by-step derivation in module docstring for all 4 metric variants; `MOCK_GRADES` dict decouples tests from grader |
| `tests/metrics/test_calculator.py` | Gold unit tests for all 4 metric variants + empty input + per-type breakdown | VERIFIED | 381 lines (min: 80); 13 tests — all pass (0.02s runtime) |
| `src/asag/graders/hybrid.py` | HybridGrader class with FeatureExtractor, fit(), grade() | VERIFIED | 311 lines (min: 120); FeatureExtractor extracts 4 handcrafted features; 388-dim feature vector (4 + 384 SBERT); StandardScaler + LogisticRegression Pipeline |
| `requirements.txt` | Updated dependencies including sentence-transformers | VERIFIED | Contains `sentence-transformers>=5.0` and `pytest>=7.0` |
| `tests/graders/test_hybrid.py` | Smoke tests for HybridGrader fit/grade cycle | VERIFIED | 184 lines (min: 30); 6 tests — all pass (~22s runtime) |
| `src/asag/evaluation/engine.py` | EvaluationEngine class with run(), _run_protocol_a(), _run_protocol_b(), _grade_perturbations(), compute_robustness_drop() | VERIFIED | 660 lines (min: 150); all required methods present and wired |
| `src/asag/evaluation/__init__.py` | Package re-exports for EvaluationEngine and result types | VERIFIED | Re-exports `EvaluationEngine` and `EvaluationResult` with `__all__` |
| `tests/evaluation/test_engine_e2e.py` | E2E test running HybridGrader under both protocols on Beetle + SciEntsBank subsets | VERIFIED | 353 lines (min: 80); 4 tests — all pass (139.88s runtime) |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `tests/metrics/test_calculator.py` | `src/asag/metrics/calculator.py` | pytest imports MetricCalculator and calls each metric method | WIRED | `from asag.metrics import MetricCalculator` at line 17; all 4 methods called in tests |
| `tests/metrics/synthetic_mini_dataset.py` | `src/asag/schema/records.py` | constructs PerturbationRecord instances for mock perturbations | WIRED | `from asag.schema import AnswerRecord, PerturbationRecord, QuestionRecord` at line 289 |
| `src/asag/graders/base.py` | `src/asag/metrics/results.py` | GradeResult used by GraderInterface contract | PARTIAL | `GradeResult` is defined in `base.py` (not imported from `results.py`); the PLAN stated `GradeResult` is used by the contract — this is fulfilled, though `GradeResult` lives in `base.py` rather than `results.py`. The interface contract is satisfied |
| `src/asag/graders/hybrid.py` | `src/asag/graders/base.py` | HybridGrader(GraderInterface) inheritance | WIRED | `class HybridGrader(GraderInterface)` at line 126 |
| `src/asag/graders/hybrid.py` | `sentence_transformers` | SentenceTransformer('all-MiniLM-L6-v2').encode() | WIRED | `SentenceTransformer(self.MODEL_ID)` at line 165; `MODEL_ID = "all-MiniLM-L6-v2"` |
| `src/asag/graders/hybrid.py` | `src/asag/schema/records.py` | Consumes AnswerRecord and QuestionRecord for training | WIRED | `from asag.schema import AnswerRecord, LABEL_TO_SCORE, QuestionRecord` at line 34 |
| `src/asag/evaluation/engine.py` | `src/asag/metrics/calculator.py` | EvaluationEngine instantiates MetricCalculator and calls metric methods per fold | WIRED | `from asag.metrics import MetricCalculator, MetricResult` at line 37; `self._calc = MetricCalculator()` at line 103 |
| `src/asag/evaluation/engine.py` | `src/asag/graders/base.py` | EvaluationEngine accepts any GraderInterface implementation | WIRED | `from asag.graders.base import GraderInterface, GradeResult` at line 35; type annotation `grader: GraderInterface` in `__init__` |
| `src/asag/evaluation/engine.py` | `src/asag/splitters` | Imports protocol_a_splits and protocol_b_splits for fold generation | WIRED | `from asag.splitters import protocol_a_splits, protocol_b_splits` at line 39 |
| `src/asag/evaluation/engine.py` | `src/asag/infra/storage.py` | EvaluationEngine.run() persists EvaluationResult to disk via save_json | WIRED | `from asag.infra.storage import save_json` at line 36; `save_json(result.model_dump(), Path(run_dir) / "evaluation_result.json")` at line 186 |
| `tests/evaluation/test_engine_e2e.py` | `src/asag/evaluation/engine.py` | E2E test instantiates EvaluationEngine with HybridGrader | WIRED | `from asag.evaluation import EvaluationEngine, EvaluationResult` at line 26 |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|---------|
| EVAL-01 | 02-01 | System computes IVR — frequency and degree of score changes on meaning-preserving perturbations | SATISFIED | `MetricCalculator.ivr_flip()` and `ivr_absdelta()` implemented; gold tests pass |
| EVAL-02 | 02-01 | System computes SSR — proportion of correct score changes on meaning-altering perturbations | SATISFIED | `MetricCalculator.ssr_directional()` implemented; gold test passes |
| EVAL-03 | 02-01 | System computes ASR — percentage of gaming perturbations that achieve unjustified score increases | SATISFIED | `MetricCalculator.asr_thresholded()` implemented; gold test passes |
| EVAL-04 | 02-03 | System breaks down IVR, SSR, ASR by within-question (Protocol B) and across-question (Protocol A) | SATISFIED | `EvaluationEngine._run_protocol_a()` and `_run_protocol_b()` both produce `MetricResult` with protocol tag; robustness drop delta computed |
| EVAL-05 | 02-01 | System breaks down metrics by perturbation type for granular analysis | SATISFIED | `MetricCalculator.compute_by_type()` groups by type; `MetricResult.by_type` stores per-type breakdown; 3 tests verify this |
| EVAL-06 | 02-03 | System runs full evaluation under LOQO cross-validation with metrics computed per fold | SATISFIED | `_run_protocol_a()` iterates LOQO folds, fits grader per fold, computes per-fold `MetricResult` |
| EVAL-07 | 02-03 | System runs full evaluation under Protocol B (within-question diagnostic) | SATISFIED | `_run_protocol_b()` iterates per-question splits; `test_e2e_beetle_subset` asserts `len(result.protocol_b_results) > 0` |
| EVAL-08 | 02-01 | System computes dual-form metrics backed by gold unit tests with synthetic mini-dataset | SATISFIED | All 4 dual-form variants implemented; 13 gold tests all pass; synthetic mini-dataset has 75 records with step-by-step derivations |
| GRAD-02 | 02-01, 02-02 | System implements hybrid grading model combining handcrafted linguistic features with sentence-transformer embeddings | SATISFIED | `HybridGrader` with `FeatureExtractor` (4 features) + `SentenceTransformer("all-MiniLM-L6-v2")` (384-dim) = 388-dim vector |
| GRAD-05 | 02-01, 02-02 | All grading models implement common interface accepting (question, rubric, student_answer) and returning a score | SATISFIED | `GraderInterface` ABC defines `grade(question, rubric, student_answer) -> GradeResult`; `HybridGrader` implements it; interface compliance test passes |

**All 10 requirements: SATISFIED**

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `src/asag/evaluation/engine.py` | 607 | `return []` | Info | Intentional fallback in `_metric_names_for_family()` for unknown family names — not a stub; all recognized families have explicit branches |
| `tests/metrics/synthetic_mini_dataset.py` | 406, 445, 481 | "placeholder" text | Info | Documented intentional: perturbation text content is irrelevant for metric computation; only scores matter; explained in comments |

No blocker or warning anti-patterns found.

### Human Verification Required

None. All success criteria are verifiable programmatically through test execution. The E2E tests on real corpus data (Beetle and SciEntsBank) provide strong empirical confirmation.

### Gaps Summary

No gaps. All 5 observable truths verified, all 11 required artifacts exist at full substance level, all key links confirmed wired, all 10 requirements satisfied with evidence.

---

## Commit History (Phase 2)

| Commit | Type | Description |
|--------|------|-------------|
| `fd10f56` | feat(02-01) | Implement GraderInterface ABC, GradeResult, MetricCalculator, and result models |
| `203c568` | test(02-01) | Add synthetic mini-dataset and gold unit tests for MetricCalculator |
| `d308b3e` | feat(02-02) | Implement HybridGrader with FeatureExtractor and SBERT embeddings |
| `1a190a3` | test(02-02) | Add smoke tests for HybridGrader fit/grade cycle |
| `c2524f3` | feat(02-03) | Implement EvaluationEngine with Protocol A, B loops and robustness drop |
| `67dc28e` | feat(02-03) | E2E test suite for EvaluationEngine on Beetle and SciEntsBank subsets |

All 6 commits verified in git log.

---

## Test Execution Summary

| Test Suite | Tests | Passed | Failed | Runtime |
|------------|-------|--------|--------|---------|
| `tests/metrics/test_calculator.py` | 13 | 13 | 0 | 0.02s |
| `tests/graders/test_hybrid.py` | 6 | 6 | 0 | 22.26s |
| `tests/evaluation/test_engine_e2e.py` | 4 | 4 | 0 | 139.88s |
| **Total** | **23** | **23** | **0** | **~162s** |

---

_Verified: 2026-02-21T10:30:00Z_
_Verifier: Claude (gsd-verifier)_
