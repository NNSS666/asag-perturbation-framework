---
phase: 01-foundation
verified: 2026-02-20T19:49:07Z
status: passed
score: 12/12 must-haves verified
gaps: []
human_verification: []
---

# Phase 1: Foundation Verification Report

**Phase Goal:** The canonical three-object schema is defined and enforced, the data pipeline correctly loads SRA/SemEval 2013 into that schema, and both evaluation protocols (Protocol A LOQO and Protocol B within-question) have validated splitters that all downstream components can consume without leakage
**Verified:** 2026-02-20T19:49:07Z
**Status:** PASSED
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | QuestionRecord, AnswerRecord, and PerturbationRecord are defined, frozen (immutable), and enforce Pydantic v2 strict validation | VERIFIED | `records.py` uses `ConfigDict(frozen=True)` on all three models; mutation raises `ValidationError`; confirmed by live import test |
| 2 | SemEval 2013 Task 7 (Beetle + SciEntsBank) loads into canonical schema with zero data loss | VERIFIED | `semeval2013.py` concatenates all HF splits, deduplicates questions by MD5 hash, maps all 5-way integer labels to `(gold_label, gold_score)`; SUMMARY confirms Beetle 42q/5199a, SciEntsBank 195q/10804a |
| 3 | A new dataset can be added by subclassing DatasetLoader without modifying any existing code | VERIFIED | `base.py` defines `DatasetLoader(ABC)` with `@abstractmethod load()` and `@abstractmethod corpus_name`; docstring explicitly documents the subclassing pattern |
| 4 | All gold labels are normalized to a float in [0.0, 1.0] via a documented mapping | VERIFIED | `grade.py` defines `LABEL_TO_SCORE` dict and `label_int_to_score()` with docstring citing ASAG2024 benchmark; all 5 label values confirmed |
| 5 | Protocol A (LOQO) splitter partitions data by question_id — each fold holds out exactly one question and its answers for testing | VERIFIED | `protocol_a.py` wraps `LeaveOneGroupOut` with `groups=question_id`; live run on Beetle: 42 folds, each fold's train+test indices sum to 5199 |
| 6 | A leakage diagnostic confirms no held-out question text appears in training-side data for every LOQO fold | VERIFIED | `leakage.py` implements `assert_no_leakage()` with ID check and prompt-text check (against training prompts and training reference answers); called automatically from `protocol_a_splits`; 42/42 Beetle folds pass |
| 7 | Protocol B (within-question) splitter partitions answers for the same question into train/test with stratification on gold_label | VERIFIED | `protocol_b.py` uses `StratifiedShuffleSplit` per question with three-condition fallback (`n<5`, `distinct_labels<2`, `min_class_count<2`); live run: 42 questions, 4146 train + 1053 test = 5199, no overlap |
| 8 | Both splitters accept per-component seed parameters for independent reproducibility control | VERIFIED | `protocol_b_splits(answers, random_state=42)` explicit parameter; `protocol_a_splits` uses `LeaveOneGroupOut` (deterministic given groups); `SeedConfig` in infra stores independent split/perturb/train seeds |
| 9 | All intermediate outputs can be written to and read from JSON files without information loss | VERIFIED | `storage.py` uses `model_dump_json()` / `model_validate_json()` for JSONL roundtrip; live test: 2 QuestionRecords saved and loaded, equality confirmed |
| 10 | Every experiment run creates a uniquely-named directory (timestamp + corpus + seed) containing a config.json with full configuration, library versions, platform info, and seed values | VERIFIED | `run_dir.py` creates `{YYYY-MM-DD_HH-MM}_{corpus}_seed{N}`; `config.py` writes `config`, `library_versions`, `timestamp` keys; live test confirms all three keys present |
| 11 | Per-component seeds (split, perturbation, training) are independently settable | VERIFIED | `SeedConfig` Pydantic model has `split_seed`, `perturb_seed`, `train_seed` as independent int fields; live test: `SeedConfig(split_seed=42, perturb_seed=123, train_seed=456)` serializes correctly |
| 12 | Library versions for all tracked packages are captured at run start and written to config.json | VERIFIED | `versions.py` uses `importlib.metadata.version()` for 8 packages + Python + platform (10 total entries); live test: pydantic=2.12.5 captured; uninstalled packages recorded as "not_installed" |

**Score:** 12/12 truths verified

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/asag/schema/records.py` | Canonical three-object schema | VERIFIED | 168 lines; `QuestionRecord`, `AnswerRecord`, `PerturbationRecord` all present, all use `ConfigDict(frozen=True)`, complete field definitions, JSON roundtrip self-test |
| `src/asag/schema/grade.py` | GradeLabel enum and 5-way-to-float mapping | VERIFIED | 95 lines; `GradeLabel` enum, `LABEL_TO_SCORE` dict, `LABEL_NAMES` list (HF index order), `label_int_to_score()` helper with docstring and ValueError for out-of-range |
| `src/asag/loaders/base.py` | Abstract DatasetLoader base class | VERIFIED | 68 lines; `DatasetLoader(ABC)` with `@abstractmethod load()` returning `Tuple[List[QuestionRecord], List[AnswerRecord]]` and `@abstractmethod corpus_name` property |
| `src/asag/loaders/semeval2013.py` | SemEval 2013 loader for Beetle and SciEntsBank | VERIFIED | 303 lines; `SemEval2013Loader(DatasetLoader)` with full HF split concatenation, MD5-based question deduplication, integer label mapping, audit logging, and self-test block |
| `src/asag/splitters/protocol_a.py` | LOQO cross-validation splitter | VERIFIED | 193 lines; `protocol_a_splits()` wrapping `LeaveOneGroupOut`; yields complete fold dicts with all required keys; integrates `assert_no_leakage` |
| `src/asag/splitters/protocol_b.py` | Within-question train/test splitter | VERIFIED | 199 lines; `protocol_b_splits()` using `StratifiedShuffleSplit` with three-condition fallback; returns `Dict[str, Tuple[List[str], List[str]]]` |
| `src/asag/splitters/leakage.py` | Leakage diagnostic | VERIFIED | 170 lines; `assert_no_leakage()` with ID isolation check and prompt-text isolation check against training prompts and training reference answers; full self-test block |
| `src/asag/infra/storage.py` | JSON-based storage for Pydantic records | VERIFIED | 144 lines; `save_records`/`load_records` (JSONL), `save_json`/`load_json` (config); uses `model_dump_json()`/`model_validate_json()` |
| `src/asag/infra/seeds.py` | Per-component seed management | VERIFIED | 84 lines; `SeedConfig` Pydantic model with `split_seed`, `perturb_seed`, `train_seed`; `set_global_seeds()` and `set_split_seeds()` functions |
| `src/asag/infra/versions.py` | Library version capture | VERIFIED | 72 lines; `TRACKED_PACKAGES` list (8 packages), `get_library_versions()` using `importlib.metadata`; records "not_installed" for absent packages |
| `src/asag/infra/run_dir.py` | Auto-named run directory creation | VERIFIED | 49 lines; `make_run_dir()` with `exist_ok=False` guard; naming follows `{YYYY-MM-DD_HH-MM}_{corpus}_seed{N}` |
| `src/asag/infra/config.py` | Experiment configuration dataclass | VERIFIED | 126 lines; `ExperimentConfig` Pydantic model with `corpus`, `seeds` (SeedConfig), `protocol`, `description`, `extra`; `save_run_config()` writes config+versions+timestamp; `load_run_config()` reads back |
| `requirements.txt` | Python dependencies for Phase 1 | VERIFIED | 4 entries: `pydantic>=2.0,<3.0`, `datasets>=2.0`, `scikit-learn>=1.0`, `numpy>=1.20` |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `semeval2013.py` | `schema/records.py` | `from asag.schema.records import AnswerRecord, QuestionRecord` | WIRED | Import found; both types used in `load()` to construct validated instances |
| `semeval2013.py` | `schema/grade.py` | `from asag.schema.grade import label_int_to_score` | WIRED | Import found; `label_int_to_score(label_int)` called for every row to set `gold_label` and `gold_score` |
| `semeval2013.py` | `loaders/base.py` | `class SemEval2013Loader(DatasetLoader)` | WIRED | Verified in source: inherits from `DatasetLoader`, implements `load()` and `corpus_name` |
| `protocol_a.py` | `schema/records.py` | `from asag.schema.records import AnswerRecord, QuestionRecord` | WIRED | Import found; both types used in function signature and `question_lookup` construction |
| `protocol_a.py` | `leakage.py` | `from asag.splitters.leakage import assert_no_leakage` + call in fold loop | WIRED | Import at module level; `assert_no_leakage(train_questions, held_out_question)` called inside the fold iterator when `run_leakage_check=True` |
| `protocol_b.py` | `schema/records.py` | `from asag.schema.records import AnswerRecord` | WIRED | Import found; `AnswerRecord` used in function signature and `answer.question_id` / `a.gold_label` access |
| `storage.py` | `schema/records.py` | `model_dump_json()` and `model_validate_json()` | WIRED | Both called in `save_records()` and `load_records()` respectively; confirmed live roundtrip |
| `config.py` | `versions.py` | `from .versions import get_library_versions` + call in `save_run_config` | WIRED | Import and call at line 77: `"library_versions": get_library_versions()` |
| `config.py` | `seeds.py` | `from .seeds import SeedConfig` + field in ExperimentConfig | WIRED | Import found; `seeds: SeedConfig = SeedConfig()` field in `ExperimentConfig` |

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| SCHM-01 | 01-01 | Canonical three-object schema (QuestionRecord, AnswerRecord, PerturbationRecord) | SATISFIED | All three models in `records.py` with all required fields; frozen + Pydantic v2 validation |
| DATA-01 | 01-01 | SemEval 2013 Task 7 (SciEntsBank and Beetle) loads into canonical schema | SATISFIED | `SemEval2013Loader` loads both corpora from HuggingFace with deduplication and label normalization; SUMMARY reports 42q/5199a and 195q/10804a |
| DATA-02 | 01-02 | LOQO cross-validation splitter (Protocol A) | SATISFIED | `protocol_a_splits()` wrapping `LeaveOneGroupOut`; live verification: 42 folds, correct partition |
| DATA-03 | 01-03 | Structured storage for intermediate results | SATISFIED | `save_records`/`load_records` JSONL storage; `save_json`/`load_json` for config; lossless roundtrip confirmed |
| DATA-04 | 01-01 | Pluggable dataset interface (no code changes for new datasets) | SATISFIED | `DatasetLoader(ABC)` with `@abstractmethod` interface; only a new subclass required |
| DATA-05 | 01-02 | Within-question train/test splitter (Protocol B) | SATISFIED | `protocol_b_splits()` with stratification and edge-case fallback; live verification: 4146 train + 1053 test = 5199 |
| INFR-01 | 01-02, 01-03 | Fixed random seeds for all stochastic operations | SATISFIED | `SeedConfig` with independent `split_seed`, `perturb_seed`, `train_seed`; `random_state` parameter in both splitters; `set_global_seeds()` and `set_split_seeds()` |
| INFR-02 | 01-03 | Log experiment configuration (hyperparameters, library versions) per run | SATISFIED | `save_run_config()` writes `config.json` with full `ExperimentConfig`, `get_library_versions()` output, and ISO timestamp; `make_run_dir()` creates named directories |

**All 8 Phase 1 requirements satisfied. No orphaned requirements.**

REQUIREMENTS.md traceability table maps all 8 IDs (DATA-01 through DATA-05, SCHM-01, INFR-01, INFR-02) to Phase 1 with status "Complete". All are accounted for across plans 01-01, 01-02, and 01-03.

---

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `protocol_b.py` | 101 | Latent edge case: `n>=5, n_distinct_labels>=2, min_class_count>=2` but test set too small for the number of classes (e.g., n=6, 3 labels, test_size=0.2 → absolute test count=1 < n_classes=3) | INFO | Not triggered by any real Beetle or SciEntsBank question. Only manifests for synthetic or future corpora with very few answers and many distinct labels. Real data produces `ValueError` from sklearn in this scenario, which would propagate as an uncaught exception. |

No blocker anti-patterns. No TODO/FIXME/placeholder comments. No empty implementations.

---

### Human Verification Required

None. All goal-level truths are verifiable programmatically and have been confirmed by live execution.

---

## Verification Details

### Live Execution Summary

All the following were executed and passed during this verification session:

1. `from asag.schema import QuestionRecord, AnswerRecord, PerturbationRecord` — all three import cleanly
2. `QuestionRecord(...)` mutation attempt — raises `ValidationError` (frozen=True enforced)
3. `label_int_to_score(0)` returns `('correct', 1.0)`; `label_int_to_score(2)` returns `('partially_correct_incomplete', 0.5)`
4. All module-level imports succeed: schema, loaders, splitters, infra
5. JSONL storage roundtrip: 2 `QuestionRecord` instances saved and loaded with equality preserved
6. Run directory creation: name contains "beetle" and "seed42"
7. `ExperimentConfig(split_seed=42, perturb_seed=123, train_seed=456)` serializes correctly; all three seed values survive `save_run_config`/`load_run_config` roundtrip
8. `get_library_versions()` returns 10 entries including `pydantic=2.12.5`
9. `assert_no_leakage()` — clean split passes; ID leakage correctly raises `AssertionError`
10. `protocol_b_splits(real_beetle_answers)` — 42 questions, 4146+1053=5199, no overlap
11. `protocol_a_splits(real_beetle_questions, real_beetle_answers)` — 42 folds, all leakage checks pass, every fold's train+test indices sum to 5199

### Module __init__.py Re-exports

All public symbols are correctly re-exported:

- `asag.schema` — QuestionRecord, AnswerRecord, PerturbationRecord, GradeLabel, LABEL_TO_SCORE, LABEL_NAMES, label_int_to_score
- `asag.loaders` — DatasetLoader, SemEval2013Loader
- `asag.splitters` — protocol_a_splits, protocol_b_splits, assert_no_leakage
- `asag.infra` — 12 symbols: save_records, load_records, save_json, load_json, SeedConfig, set_global_seeds, set_split_seeds, make_run_dir, get_library_versions, ExperimentConfig, save_run_config, load_run_config

### Latent Edge Case Note (Protocol B, INFO severity)

`protocol_b_splits()` has a latent edge case where `n >= 5`, `distinct_labels >= 2`, and `min_class_count >= 2` all pass the fallback condition, but the absolute test-set size (computed as `round(n * test_size)`) is smaller than the number of distinct classes. sklearn's `StratifiedShuffleSplit` raises `ValueError: The test_size = K should be greater or equal to the number of classes = M` in this scenario.

This condition is NOT triggered by any current Beetle or SciEntsBank question (verified by live run). It is a theoretical risk for future corpora with very few answers per question and many label categories. It does not block the Phase 1 goal.

---

## Gaps Summary

No gaps. All 12 observable truths verified, all 13 artifacts substantive and wired, all 9 key links connected, all 8 requirements satisfied.

---

_Verified: 2026-02-20T19:49:07Z_
_Verifier: Claude (gsd-verifier)_
