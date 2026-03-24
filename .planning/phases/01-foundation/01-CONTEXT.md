# Phase 1: Foundation - Context

**Gathered:** 2026-02-20
**Status:** Ready for planning

<domain>
## Phase Boundary

Canonical three-object schema (QuestionRecord, AnswerRecord, PerturbationRecord), data pipeline for SemEval 2013 Task 7 (SciEntsBank + Beetle), dual-protocol splitters (Protocol A LOQO + Protocol B within-question), and reproducibility infrastructure. No models, no metrics, no perturbation generation — just the data foundation.

</domain>

<decisions>
## Implementation Decisions

### Project structure
- Claude's discretion on package layout (single src/ package with submodules recommended)
- Experiments run via **Jupyter notebooks** — notebooks/ directory for code, runs/ for outputs
- Dependencies managed with **requirements.txt** (pip)
- Python version: currently 3.9.6 on machine — note: may need 3.10+ for some Phase 4 libraries (ModernBERT); upgrade when needed
- Git for version control

### Data schema design
- **Pydantic models** for the three canonical objects — strict validation, fail fast on bad data
- **Unified grade scale** — all datasets normalized to a common scale for cross-dataset comparison
- Claude's discretion on dataset loader extensibility (plugin pattern for adding professor's future dataset)

### Storage format
- **JSON** for all intermediate outputs (perturbations, grades, metrics) — readable, debuggable, sufficient for small ASAG datasets
- **One directory per run** (e.g., runs/2026-02-20_14-30_beetle_seed42/) — each run self-contained
- Notebooks live in notebooks/, run outputs in runs/ — code and data kept separate

### Reproducibility setup
- **Automatic version logging** — every run records library versions (PyTorch, transformers, etc.) alongside config
- **Per-component seeds** — separate seeds for split, perturbation, and training (default all 42, independently variable for multi-seed experiments)
- **Auto-generated run names** with timestamp + dataset + seed info
- Git-tracked codebase

### Claude's Discretion
- Exact package/module layout
- Dataset loader architecture (plugin pattern specifics)
- Unified grade scale mapping details
- Config file format for experiment parameters

</decisions>

<specifics>
## Specific Ideas

- User is not deeply technical in software engineering — code should be well-commented and notebook-driven for accessibility
- Professor needs to understand and potentially run the code — keep it simple and well-documented
- User is on macOS with Python 3.9.6 — no GPU locally, Colab planned for Phase 4

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 01-foundation*
*Context gathered: 2026-02-20*
