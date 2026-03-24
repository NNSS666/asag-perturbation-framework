---
phase: 01-foundation
plan: "03"
subsystem: infra
tags: [pydantic, jsonl, reproducibility, seeds, json-storage, importlib-metadata]

# Dependency graph
requires:
  - phase: 01-01
    provides: "QuestionRecord, AnswerRecord, PerturbationRecord Pydantic schema used by storage roundtrip tests"
provides:
  - "JSONL-based lossless storage for any Pydantic BaseModel list (save_records / load_records)"
  - "Pretty-printed JSON config file I/O (save_json / load_json)"
  - "Auto-named run directories: YYYY-MM-DD_HH-MM_corpus_seedN (make_run_dir)"
  - "Library version capture via importlib.metadata for 8 tracked packages + Python + platform (get_library_versions)"
  - "Per-component seed isolation: SeedConfig with independent split/perturb/train seeds"
  - "Full experiment config logging to config.json: ExperimentConfig + versions + timestamp (save_run_config / load_run_config)"
  - "asag.infra package with all 12 symbols re-exported from __init__.py"
affects:
  - 01-04-splitters
  - 02-perturbations
  - 03-graders
  - 04-training
  - 05-llm-graders
  - 06-evaluation

# Tech tracking
tech-stack:
  added:
    - "importlib.metadata (stdlib, Python 3.8+) for package version capture"
    - "platform (stdlib) for OS info capture"
  patterns:
    - "JSONL one-record-per-line with model_dump_json() / model_validate_json() for lossless Pydantic roundtrip"
    - "Run directory auto-naming: timestamp + corpus + seed — all experiments traceable from directory listing"
    - "Config-as-artifact: config.json captures exact experiment setup + library versions at run start"
    - "Seed isolation: pass seed via random_state parameter per component; set_global_seeds only as fallback"

key-files:
  created:
    - src/asag/infra/__init__.py
    - src/asag/infra/storage.py
    - src/asag/infra/seeds.py
    - src/asag/infra/versions.py
    - src/asag/infra/run_dir.py
    - src/asag/infra/config.py
  modified: []

key-decisions:
  - "JSONL format (not JSON array) for records — enables streaming large datasets and appending without re-reading"
  - "save_json uses default=str to handle datetime/Path in config files — avoids serialization errors with no information loss for metadata"
  - "make_run_dir uses exist_ok=False to prevent silent overwrites of previous experiment results"
  - "SeedConfig is not frozen (mutable Pydantic model) — seeds may be varied across runs in multi-seed experiments"
  - "load_run_config returns raw dict not ExperimentConfig — config.json contains extra keys (library_versions, timestamp) not in the model"
  - "TRACKED_PACKAGES covers all 4 phases' dependencies (pydantic, datasets, sklearn, numpy, torch, transformers, sentence-transformers, openai) — captures not_installed for missing ones"

patterns-established:
  - "Infra pattern: all intermediate outputs persisted as JSONL; load_records for typed retrieval"
  - "Reproducibility pattern: every experiment creates run_dir + config.json before any computation"
  - "Seed isolation pattern: SeedConfig.split_seed -> set_split_seeds(); SeedConfig.train_seed -> passed as random_state"

requirements-completed: [DATA-03, INFR-01, INFR-02]

# Metrics
duration: 4min
completed: 2026-02-20
---

# Phase 1 Plan 03: Reproducibility Infrastructure Summary

**JSONL Pydantic storage, auto-named run directories, importlib.metadata version capture, and per-component SeedConfig for isolated multi-seed experiments**

## Performance

- **Duration:** 4 min
- **Started:** 2026-02-20T19:38:11Z
- **Completed:** 2026-02-20T19:42:06Z
- **Tasks:** 2 of 2
- **Files modified:** 6

## Accomplishments

- JSONL storage with lossless Pydantic roundtrip verified for all three canonical record types (QuestionRecord, AnswerRecord, PerturbationRecord)
- Auto-named run directories following the `YYYY-MM-DD_HH-MM_corpus_seedN` convention with exist_ok=False guard against overwrites
- Library version capture (Python, platform + 8 tracked packages) using stdlib importlib.metadata — records "not_installed" for missing packages rather than failing
- ExperimentConfig dataclass serialized to config.json alongside library versions and timestamp, loadable for full audit trail
- Per-component SeedConfig with independent split/perturb/train seeds; set_global_seeds and set_split_seeds for libraries that don't accept random_state
- All 12 public symbols re-exported from asag.infra.__init__.py

## Task Commits

Each task was committed atomically:

1. **Task 1: JSON storage and seed management** - `e32346a` (feat)
2. **Task 2: Run directory creation, version capture, and experiment config** - `b2dbf34` (feat)

## Files Created/Modified

- `src/asag/infra/__init__.py` - Re-exports all 12 public infra symbols
- `src/asag/infra/storage.py` - save_records/load_records (JSONL) + save_json/load_json (config)
- `src/asag/infra/seeds.py` - SeedConfig, set_global_seeds, set_split_seeds
- `src/asag/infra/versions.py` - get_library_versions() with TRACKED_PACKAGES list
- `src/asag/infra/run_dir.py` - make_run_dir() auto-naming with FileExistsError guard
- `src/asag/infra/config.py` - ExperimentConfig, save_run_config, load_run_config

## Decisions Made

- JSONL format over JSON array for record storage — enables streaming large datasets and appending without re-reading the whole file
- `save_json` uses `json.dump(..., default=str)` to handle datetime/Path types in config files without errors
- `make_run_dir` uses `exist_ok=False` to prevent silent overwriting of previous experiment results
- `SeedConfig` is not frozen (unlike schema records) — seeds may need to be varied across runs in multi-seed ablations
- `load_run_config` returns raw dict rather than reconstructing ExperimentConfig — config.json contains extra keys (library_versions, timestamp) outside the model scope
- TRACKED_PACKAGES covers all 4 phases' dependencies upfront; missing packages recorded as "not_installed" rather than raising exceptions

## Deviations from Plan

None — plan executed exactly as written.

Note: The `__init__.py` initially caused import errors when testing sub-modules because it referenced `run_dir`, `versions`, and `config` before those modules were created. Resolved by implementing all Task 2 modules before running the final verification. This was an execution sequencing detail, not a plan deviation.

## Issues Encountered

- Initial verification attempt for Task 1 failed because `__init__.py` imported not-yet-created Task 2 modules. Fix: write all 5 modules before running any verification. No code changes required.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Full infra package ready for use: `from asag.infra import save_records, ExperimentConfig, make_run_dir, ...`
- Plan 01-04 (splitters) can use save_records to persist split outputs and SeedConfig for reproducible splits
- Phase 2 onward can call make_run_dir + save_run_config at experiment start for full audit trail
- All data flows through JSONL — no DataFrame intermediaries required

---
*Phase: 01-foundation*
*Completed: 2026-02-20*
