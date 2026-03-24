# Phase 1: Foundation - Research

**Researched:** 2026-02-20
**Domain:** Python data pipeline — Pydantic schema, XML/HuggingFace data loading, sklearn splitters, JSON storage, reproducibility infrastructure
**Confidence:** MEDIUM-HIGH (core Python libraries verified via official docs; SemEval XML schema partially reconstructed from HuggingFace mirrors + prior art)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **Project structure:** Experiments run via Jupyter notebooks — notebooks/ directory for code, runs/ for outputs. Dependencies managed with requirements.txt (pip). Python 3.9.6 on machine (may need 3.10+ for Phase 4 ModernBERT; upgrade deferred). Git for version control.
- **Data schema:** Pydantic models for the three canonical objects — strict validation, fail fast on bad data.
- **Unified grade scale:** All datasets normalized to a common scale for cross-dataset comparison.
- **Storage format:** JSON for all intermediate outputs (perturbations, grades, metrics) — readable, debuggable. One directory per run (e.g., runs/2026-02-20_14-30_beetle_seed42/) — each run self-contained. Notebooks in notebooks/, outputs in runs/.
- **Reproducibility:** Automatic version logging — every run records library versions alongside config. Per-component seeds (split, perturbation, training — default all 42, independently variable). Auto-generated run names with timestamp + dataset + seed info.

### Claude's Discretion

- Exact package/module layout within src/
- Dataset loader architecture (plugin pattern specifics)
- Unified grade scale mapping details (label-to-float mapping)
- Config file format for experiment parameters

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| SCHM-01 | Three-object canonical schema: QuestionRecord (question_id, prompt, rubric_text, reference_answers, score_scale), AnswerRecord (answer_id, question_id, student_answer, gold_score, annotator_id), PerturbationRecord (perturb_id, answer_id, family, type, generator, seed, text) | Pydantic v2 BaseModel pattern — verified via official docs |
| DATA-01 | Load SemEval 2013 Task 7 (SciEntsBank + Beetle) into canonical schema | HuggingFace datasets nkazi/Beetle + nkazi/SciEntsBank verified; original XML described below |
| DATA-02 | LOQO cross-validation splitter (Protocol A) | sklearn LeaveOneGroupOut — verified via official docs |
| DATA-03 | Structured storage for all intermediate results | Pydantic model_dump_json() → JSON files — verified via official docs |
| DATA-04 | Pluggable dataset interface | Python ABC (abstract base class) pattern — verified via standard library docs |
| DATA-05 | Within-question train/test splitter (Protocol B) | sklearn StratifiedShuffleSplit per question group — verified via official docs |
| INFR-01 | Fixed random seeds for all stochastic operations | Python random.seed(), numpy.random.seed(), torch.manual_seed() pattern |
| INFR-02 | Log experiment config (hyperparameters, prompts, model IDs, library versions) per run | importlib.metadata.version() — verified via Python 3.9 docs |
</phase_requirements>

---

## Summary

Phase 1 establishes the data foundation: a Pydantic-validated schema, a loader that reads SemEval 2013 Task 7 (Beetle + SciEntsBank), two splitting protocols, JSON-based storage, and reproducibility logging. All components are deterministic (seed-controlled), require no GPU, and are fully exercisable on the user's 2019 macOS Python 3.9.6 machine.

The SemEval 2013 Task 7 dataset is available in two access paths: (1) the original XML files distributed by the task organizers (myrosia/semeval-2013-task7 on GitHub) or the LDC/NIST distribution, and (2) HuggingFace mirrors (`nkazi/Beetle`, `nkazi/SciEntsBank`) that expose the same data as pandas-friendly DataFrames. The HuggingFace path removes the need to write an XML parser but introduces a `datasets` library dependency; the XML path gives full control with no new dependency beyond Python's stdlib `xml.etree.ElementTree`. Both paths are viable; the HuggingFace approach is recommended for speed and robustness.

The grade scale decision (Claude's discretion) is critical for cross-dataset portability. The most defensible choice, supported by recent literature (ASAG2024 benchmark, 2024), is normalizing all labels to a continuous float in [0.0, 1.0] representing degree of correctness, with an accompanying string enum (`GradeLabel`) for interpretability. This enables direct comparison across the 5-way SemEval labels, future binary datasets, and the professor's custom dataset.

**Primary recommendation:** Use HuggingFace `datasets` to load Beetle/SciEntsBank, map to Pydantic models immediately after load, use `sklearn.model_selection.LeaveOneGroupOut` for Protocol A and `StratifiedShuffleSplit` per-question for Protocol B, serialize everything with `model_dump_json()`, and use `importlib.metadata.version()` for version capture.

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pydantic | 2.x (2.12.5 current) | Schema definition, validation, JSON serialization | Fastest validation (Rust core), first-class JSON roundtrip, widely used in ML research tools |
| datasets (HuggingFace) | 2.x (3.x also available) | Load SemEval 2013 datasets | Pre-processed mirrors of Beetle + SciEntsBank are already on HuggingFace; avoids custom XML parser |
| scikit-learn | 1.5-1.8 | LeaveOneGroupOut (Protocol A), StratifiedShuffleSplit (Protocol B) | Standard splitter API; used in virtually all ASAG papers |
| importlib.metadata | stdlib (Python 3.8+) | Capture installed library versions | Built-in, no dependency; works on Python 3.9 |
| pathlib | stdlib | Run directory creation | Built-in, path manipulation |
| json | stdlib | Write/read JSON storage | Built-in; sufficient for small ASAG datasets |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| xml.etree.ElementTree | stdlib | Parse original SemEval XML if HuggingFace unavailable | Fallback if internet access is restricted or dataset not on HF |
| typing (Optional, List, Literal) | stdlib | Pydantic field annotations | Required for schema field definitions |
| datetime | stdlib | Auto-generated run names | Timestamp component of runs/YYYY-MM-DD_HH-MM_dataset_seed42/ |
| abc (ABC, abstractmethod) | stdlib | Dataset loader base class (DATA-04) | Defines the pluggable interface every loader must implement |
| numpy | latest compatible | Random seed management, array ops for splitters | Required by sklearn; use np.random.seed() for reproducibility |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| HuggingFace datasets | Raw XML + xml.etree | HF is easier but adds dependency; XML gives full control. Recommended: HF with XML fallback documented |
| pydantic v2 | dataclasses + marshmallow | Pydantic has faster validation and native JSON; dataclasses need extra serialization work |
| sklearn LeaveOneGroupOut | Custom question-group splitter | Reinventing the wheel; sklearn is already the standard for this in ASAG literature |
| stdlib json | orjson or ujson | Speed difference irrelevant for ASAG scale datasets (<50K rows total) |

**Installation:**
```bash
pip install pydantic>=2.0 datasets scikit-learn numpy
```

---

## Architecture Patterns

### Recommended Project Structure

```
src/
├── asag/                    # Main package
│   ├── __init__.py
│   ├── schema/
│   │   ├── __init__.py
│   │   ├── records.py       # QuestionRecord, AnswerRecord, PerturbationRecord
│   │   └── grade.py         # GradeLabel enum + unified score mapping
│   ├── loaders/
│   │   ├── __init__.py
│   │   ├── base.py          # DatasetLoader ABC
│   │   └── semeval2013.py   # SemEval 2013 loader (Beetle + SciEntsBank)
│   ├── splitters/
│   │   ├── __init__.py
│   │   ├── protocol_a.py    # LOQO splitter (LeaveOneGroupOut wrapper)
│   │   └── protocol_b.py    # Within-question splitter (StratifiedShuffleSplit wrapper)
│   └── infra/
│       ├── __init__.py
│       ├── run_dir.py       # Auto-named run directory creation
│       ├── config.py        # Experiment config dataclass
│       └── versions.py      # Library version capture
notebooks/
└── 01_data_pipeline.ipynb   # Phase 1 demonstration + validation notebook
runs/                        # All experiment outputs (git-ignored)
data/                        # Raw dataset files (git-ignored)
requirements.txt
```

### Pattern 1: Pydantic v2 Schema Definition

**What:** Define each canonical object as a `BaseModel` subclass with typed fields and Optional for nullable values.
**When to use:** At schema layer; all downstream code receives validated instances, never raw dicts.

```python
# Source: https://docs.pydantic.dev/latest/concepts/models/
from typing import Optional, List, Literal
from pydantic import BaseModel, ConfigDict, Field

class QuestionRecord(BaseModel):
    model_config = ConfigDict(frozen=True)  # immutable after creation

    question_id: str
    prompt: str
    rubric_text: Optional[str] = None
    reference_answers: List[str]
    score_scale: Literal["5way", "3way", "2way", "continuous"] = "5way"
    corpus: Optional[str] = None  # e.g. "beetle" or "scientsbank"

class AnswerRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    answer_id: str
    question_id: str
    student_answer: str
    gold_label: str          # raw label string, e.g. "correct"
    gold_score: float        # normalized [0.0, 1.0]
    annotator_id: Optional[str] = None

class PerturbationRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    perturb_id: str
    answer_id: str
    family: Literal["invariance", "sensitivity", "gaming"]
    type: str                # e.g. "synonym_substitution"
    generator: str           # e.g. "rule-based" or "gpt-4o"
    seed: int
    text: str
```

### Pattern 2: Dataset Loader ABC (DATA-04 Extensibility)

**What:** Abstract base class every loader must implement. Adding a new dataset = new subclass, no pipeline changes.
**When to use:** Whenever a new dataset source is added (professor's custom dataset, SRA v1, etc.)

```python
# Source: https://docs.python.org/3/library/abc.html
from abc import ABC, abstractmethod
from typing import Tuple, List
# from asag.schema.records import QuestionRecord, AnswerRecord

class DatasetLoader(ABC):
    """Base class all dataset loaders must implement."""

    @abstractmethod
    def load(self) -> Tuple[List[QuestionRecord], List[AnswerRecord]]:
        """Return (questions, answers) in canonical schema."""
        ...

    @property
    @abstractmethod
    def corpus_name(self) -> str:
        """Human-readable name, used in run directory naming."""
        ...
```

### Pattern 3: SemEval 2013 Loader via HuggingFace

**What:** Load Beetle/SciEntsBank via HF datasets library, map to canonical schema immediately.
**Key field mapping:**

Beetle and SciEntsBank expose these fields on HuggingFace:
- `id` → `answer_id` (needs question prefix for uniqueness)
- `question` → `QuestionRecord.prompt`
- `reference_answer` → `QuestionRecord.reference_answers` (list of one item per row; must deduplicate)
- `student_answer` → `AnswerRecord.student_answer`
- `label` → 5-way integer 0-4, maps to `gold_label` string + `gold_score` float

**5-way label → unified score mapping (Claude's discretion — recommendation):**

| Label int | Label string | gold_score |
|-----------|-------------|------------|
| 0 | correct | 1.0 |
| 2 | partially_correct_incomplete | 0.5 |
| 1 | contradictory | 0.0 |
| 3 | irrelevant | 0.0 |
| 4 | non_domain | 0.0 |

Rationale: ASAG2024 (2024) normalizes ASAG dataset labels to [0, 1]; this mapping is the most defensible for the 5-way scheme. `partially_correct_incomplete` at 0.5 is semantically correct (half credit). `contradictory`, `irrelevant`, and `non_domain` are all flavors of incorrect.

```python
# Source: https://huggingface.co/datasets/nkazi/Beetle
from datasets import load_dataset

LABEL_TO_SCORE = {
    "correct": 1.0,
    "partially_correct_incomplete": 0.5,
    "contradictory": 0.0,
    "irrelevant": 0.0,
    "non_domain": 0.0,
}
LABEL_NAMES = ["correct", "contradictory", "partially_correct_incomplete", "irrelevant", "non_domain"]

beetle_hf = load_dataset("nkazi/Beetle")
# Returns DatasetDict with splits: "train", "test_ua", "test_uq"
# Fields: id, question, reference_answer, student_answer, label (int 0-4), split
```

### Pattern 4: Protocol A — LOQO Splitter

**What:** sklearn `LeaveOneGroupOut` where groups = question_id. Yields (train_indices, test_indices) for each question held out.
**Leakage diagnostic:** After each split, assert no question_id from the test set appears in train QuestionRecord.prompt or reference_answers (text match check).

```python
# Source: https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.LeaveOneGroupOut.html
from sklearn.model_selection import LeaveOneGroupOut
import numpy as np

def protocol_a_splits(answers: List[AnswerRecord]):
    """Yields (train_indices, test_indices) with one question held out per fold."""
    question_ids = [a.question_id for a in answers]
    groups = np.array(question_ids)
    indices = np.arange(len(answers))

    logo = LeaveOneGroupOut()
    for train_idx, test_idx in logo.split(indices, groups=groups):
        yield train_idx, test_idx
    # n_splits = number of unique questions (56 for Beetle, 197 for SciEntsBank)
```

### Pattern 5: Protocol B — Within-Question Splitter

**What:** For each question independently, split its answers into train/test using `StratifiedShuffleSplit`. Stratify on `gold_label` to preserve class distribution.

```python
# Source: https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.StratifiedShuffleSplit.html
from sklearn.model_selection import StratifiedShuffleSplit
from collections import defaultdict

def protocol_b_splits(answers: List[AnswerRecord], test_size=0.2, random_state=42):
    """For each question, split its answers into train/test.
    Returns dict mapping question_id -> (train_answer_ids, test_answer_ids).
    """
    by_question = defaultdict(list)
    for a in answers:
        by_question[a.question_id].append(a)

    result = {}
    sss = StratifiedShuffleSplit(n_splits=1, test_size=test_size, random_state=random_state)

    for q_id, q_answers in by_question.items():
        labels = [a.gold_label for a in q_answers]
        indices = list(range(len(q_answers)))
        # Handle edge case: questions with too few samples for stratification
        if len(set(labels)) < 2 or len(q_answers) < 5:
            # Fall back to simple split for very small groups
            split_point = max(1, int(len(q_answers) * (1 - test_size)))
            train_ids = [q_answers[i].answer_id for i in indices[:split_point]]
            test_ids = [q_answers[i].answer_id for i in indices[split_point:]]
        else:
            for train_idx, test_idx in sss.split(indices, labels):
                train_ids = [q_answers[i].answer_id for i in train_idx]
                test_ids = [q_answers[i].answer_id for i in test_idx]

        result[q_id] = (train_ids, test_ids)

    return result
```

### Pattern 6: JSON Storage Roundtrip

**What:** Use Pydantic's `model_dump_json()` to write records; `model_validate_json()` to read back.

```python
# Source: https://docs.pydantic.dev/latest/concepts/serialization/
import json
from pathlib import Path

def save_records(records: List[BaseModel], path: Path) -> None:
    """Write list of Pydantic records to JSON, one per line (JSONL)."""
    with open(path, "w") as f:
        for record in records:
            f.write(record.model_dump_json() + "\n")

def load_records(path: Path, model_class) -> List:
    """Read JSONL back into Pydantic model instances."""
    records = []
    with open(path) as f:
        for line in f:
            records.append(model_class.model_validate_json(line.strip()))
    return records
```

### Pattern 7: Run Directory + Version Logging

**What:** Auto-name runs with timestamp + corpus + seed; capture all library versions at run start.

```python
# Source: https://docs.python.org/3.9/library/importlib.metadata.html
# Source: https://docs.python.org/3/library/pathlib.html
from datetime import datetime
from importlib.metadata import version, PackageNotFoundError
from pathlib import Path
import json, sys, platform

TRACKED_PACKAGES = ["pydantic", "datasets", "scikit-learn", "numpy", "torch", "transformers"]

def get_library_versions() -> dict:
    """Capture installed library versions at run start."""
    versions = {"python": sys.version}
    for pkg in TRACKED_PACKAGES:
        try:
            versions[pkg] = version(pkg)
        except PackageNotFoundError:
            versions[pkg] = "not_installed"
    return versions

def make_run_dir(base: Path, corpus: str, seed: int) -> Path:
    """Create a unique, self-documenting run directory."""
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M")
    run_name = f"{ts}_{corpus}_seed{seed}"
    run_dir = base / run_name
    run_dir.mkdir(parents=True, exist_ok=False)  # fail if exists — no overwriting
    return run_dir

def save_run_config(run_dir: Path, config: dict, seed: int) -> None:
    """Write config + versions + seed to run_dir/config.json."""
    config_record = {
        "seed": seed,
        "config": config,
        "library_versions": get_library_versions(),
        "platform": platform.platform(),
    }
    with open(run_dir / "config.json", "w") as f:
        json.dump(config_record, f, indent=2)
```

### Anti-Patterns to Avoid

- **Hard-coding grade label integers:** Never use raw `0`, `1`, `2`, `3`, `4` in business logic — always go through the LABEL_NAMES mapping so a new dataset with different label ordering doesn't silently corrupt scores.
- **Mutating Pydantic models:** Use `model_config = ConfigDict(frozen=True)` to prevent accidental field mutation after load.
- **Shared mutable state across folds:** Each LOQO fold must produce fresh copies of any fitted objects (vectorizers, scalers) — never fit on all data then split.
- **Question text in training-side objects after LOQO split:** The leakage diagnostic must check that held-out question_id's `prompt` and `reference_answers` text does not appear in any training-side string (e.g., as part of a feature or embedded text).
- **Using `split` column from HuggingFace for Protocol A/B:** The HuggingFace split names (`train`, `test_ua`, `test_uq`, `test_ud`) are the original SemEval splits, NOT the project's Protocol A/B splits. Load all rows and re-split programmatically using LOQO and within-question logic.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Cross-validation by group | Custom question-group iterator | `sklearn.LeaveOneGroupOut` | Edge cases in group counting, index alignment; sklearn is battle-tested |
| Stratified split per question | Custom label-frequency split | `sklearn.StratifiedShuffleSplit` | Handles label imbalance, small groups; degenerate case handling already built in |
| JSON serialization with type safety | Custom JSON encoder | `pydantic.model_dump_json()` / `model_validate_json()` | Handles Optional, nested models, datetime, enums correctly; roundtrip guaranteed |
| Library version capture | Parsing pip freeze output | `importlib.metadata.version()` | Built-in, no subprocess, works on Python 3.9+ |
| Dataset loading + caching | HTTP download + custom file cache | HuggingFace `datasets` | Handles download, caching, arrow format, incremental updates automatically |

**Key insight:** The "hard parts" of each component (group-aware splitting, type-safe JSON roundtrip, version introspection) all have stdlib or scikit-learn solutions. Hand-rolling these introduces subtle bugs that corrupt evaluation results.

---

## Common Pitfalls

### Pitfall 1: HuggingFace "split" Confusion with Protocol Splits

**What goes wrong:** Developer loads `load_dataset("nkazi/Beetle")["test_uq"]` thinking this is the Protocol A test set. In fact, `test_uq` is the original SemEval "unseen questions" split — a completely different partitioning from LOQO.
**Why it happens:** The HuggingFace dataset uses the original SemEval train/test split names; these do not correspond to the project's Protocol A (LOQO) or Protocol B (within-question) splits.
**How to avoid:** Load ALL rows from all HF splits into a single list (concatenate train + test_ua + test_uq + test_ud), then apply project-defined LOQO and within-question splitters. Document this explicitly in the loader.
**Warning signs:** Unusually high test accuracy, test set has a very different question distribution than expected.

### Pitfall 2: Question Deduplication During Schema Construction

**What goes wrong:** Each row in the HuggingFace dataset has `question` and `reference_answer` repeated for each student answer. If you create a `QuestionRecord` per row, you'll have 3,941 duplicate QuestionRecords for Beetle's training split.
**Why it happens:** The HF format is answer-centric (one row per student answer); the canonical schema is question-centric (one QuestionRecord per question, with multiple reference answers).
**How to avoid:** Group rows by `question` text (or a stable question_id), collect all `reference_answer` values into a list, and create exactly one `QuestionRecord` per unique question. Use `question` text as a temporary key if no question_id is available in HF.
**Warning signs:** `len(questions) == len(answers)` (should be len(questions) << len(answers)).

### Pitfall 3: Grade Scale Inconsistency Across Datasets

**What goes wrong:** Beetle uses 5-way labels; a future dataset uses float scores 0.0-3.0; another uses binary pass/fail. Comparing `gold_score` across datasets silently compares different scales.
**Why it happens:** Different ASAG datasets have fundamentally different annotation schemes.
**How to avoid:** The loader's responsibility is to normalize to [0.0, 1.0] using a documented per-dataset mapping. The `score_scale` field on `QuestionRecord` records what the original scale was. Every loader MUST document its mapping in its docstring.
**Warning signs:** IVR/SSR/ASR values differ inexplicably between datasets; `gold_score` values outside [0.0, 1.0].

### Pitfall 4: LOQO Leakage from Reference Answers

**What goes wrong:** A training-side text feature (e.g., TF-IDF vocabulary fitted on all answers) includes vocabulary from the held-out question's `reference_answers` or `prompt`. The model "knows" the held-out question's keywords without being told.
**Why it happens:** LOQO partitions by question_id but naive feature extraction ignores which text came from which question.
**How to avoid:** The leakage diagnostic must verify that: (1) no QuestionRecord for the held-out question_id is in the training QuestionRecord list, and (2) the text of the held-out question does not appear verbatim in any training-side string object. Run this check as an assertion before every LOQO fold.
**Warning signs:** Unnaturally consistent performance across folds; "unseen question" performance matches "seen question" performance.

### Pitfall 5: Protocol B Small-Group Edge Cases

**What goes wrong:** Some questions in Beetle have very few student answers (n < 5) or only one label class. `StratifiedShuffleSplit` raises an error or produces a degenerate split.
**Why it happens:** ASAG datasets are not uniformly distributed across questions; some questions have only 5-10 responses.
**How to avoid:** Implement the explicit fallback shown in Pattern 5: if a question has < 5 answers or < 2 distinct labels, fall back to a simple positional split. Log which questions hit this fallback.
**Warning signs:** `ValueError: The least populated class in y has only 1 member` from sklearn.

### Pitfall 6: Per-Component Seed Isolation

**What goes wrong:** Using a single global seed means that changing the split seed also changes the perturbation seed and the training seed — making it impossible to vary one while holding others fixed.
**Why it happens:** Calling `random.seed(42)` once seeds everything globally.
**How to avoid:** Pass explicit `random_state` to each component: `split_seed`, `perturb_seed`, `train_seed` (all default 42). Pass `random_state=split_seed` to LeaveOneGroupOut/StratifiedShuffleSplit and set `numpy.random.seed(split_seed)` at the start of the split function.

### Pitfall 7: Python 3.9 Compatibility

**What goes wrong:** Using `dict[str, int]` (lowercase generic types) or `X | Y` union syntax instead of `Dict[str, int]` or `Optional[X]` — these require Python 3.10+.
**Why it happens:** Python 3.9 does not support PEP 604 (X | Y union) or PEP 585 (dict/list generics without importing from typing).
**How to avoid:** Use `from typing import Optional, List, Dict, Tuple, Literal` everywhere; avoid `|` union syntax. Test on Python 3.9 locally before committing.

---

## Code Examples

Verified patterns from official sources:

### Full Pydantic Schema with Serialization

```python
# Source: https://docs.pydantic.dev/latest/concepts/models/ + https://docs.pydantic.dev/latest/concepts/serialization/
from typing import Optional, List, Literal
from pydantic import BaseModel, ConfigDict

class QuestionRecord(BaseModel):
    model_config = ConfigDict(frozen=True)
    question_id: str
    prompt: str
    rubric_text: Optional[str] = None
    reference_answers: List[str]
    score_scale: Literal["5way", "3way", "2way", "continuous"] = "5way"
    corpus: Optional[str] = None

class AnswerRecord(BaseModel):
    model_config = ConfigDict(frozen=True)
    answer_id: str
    question_id: str
    student_answer: str
    gold_label: str
    gold_score: float    # normalized [0.0, 1.0]
    annotator_id: Optional[str] = None

class PerturbationRecord(BaseModel):
    model_config = ConfigDict(frozen=True)
    perturb_id: str
    answer_id: str
    family: Literal["invariance", "sensitivity", "gaming"]
    type: str
    generator: str
    seed: int
    text: str

# Roundtrip test
q = QuestionRecord(
    question_id="beetle_q1",
    prompt="What happens when you connect a battery to a bulb?",
    reference_answers=["The bulb lights up because current flows."],
)
json_str = q.model_dump_json()
q2 = QuestionRecord.model_validate_json(json_str)
assert q == q2  # guaranteed by Pydantic
```

### Leakage Diagnostic

```python
def assert_no_leakage(train_questions: List[QuestionRecord], held_out_q: QuestionRecord) -> None:
    """Assert held-out question text does not appear in training-side data."""
    held_out_texts = {held_out_q.prompt} | set(held_out_q.reference_answers)
    for train_q in train_questions:
        assert train_q.question_id != held_out_q.question_id, \
            f"Leakage: held-out question {held_out_q.question_id} found in training set"
        for held_text in held_out_texts:
            for ref in train_q.reference_answers:
                assert held_text not in ref, \
                    f"Leakage: held-out text fragment found in training reference answer"
```

### Version Capture (Python 3.9 compatible)

```python
# Source: https://docs.python.org/3.9/library/importlib.metadata.html
from importlib.metadata import version, PackageNotFoundError

TRACKED_PACKAGES = ["pydantic", "datasets", "scikit-learn", "numpy"]

def capture_versions() -> dict:
    result = {"python": sys.version}
    for pkg in TRACKED_PACKAGES:
        try:
            result[pkg] = version(pkg)
        except PackageNotFoundError:
            result[pkg] = "not_installed"
    return result
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Custom XML parser for SemEval | HuggingFace datasets library | 2022-2023 | Pre-processed mirrors available; no XML needed |
| Pydantic v1 (`.dict()`, `.json()`) | Pydantic v2 (`model_dump()`, `model_dump_json()`) | Pydantic 2.0 (mid-2023) | v1 API still works but deprecated; v2 is ~17x faster due to Rust core |
| `pkg_resources.get_distribution().version` | `importlib.metadata.version()` | Python 3.8+ | `pkg_resources` is deprecated in newer pip/setuptools |
| sklearn 0.x splitter API | sklearn 1.x splitter API (`split(X, y, groups)`) | sklearn 0.22 (2019) | Old API identical; current version is 1.8.0 |
| Float grade normalization per-dataset | Unified [0,1] normalized scale | ASAG2024 benchmark (2024) | Enables cross-dataset comparison; consistent with current ASAG benchmarking practice |

**Deprecated/outdated:**
- `pydantic.BaseModel.dict()` and `.json()`: replaced by `model_dump()` and `model_dump_json()` in v2
- `pkg_resources.get_distribution()`: replaced by `importlib.metadata.version()`
- Using `Optional[X]` without `= None` default in Pydantic v2: In v2, `Optional[str]` does NOT automatically default to None (unlike v1) — must explicitly write `Optional[str] = None`

---

## Open Questions

1. **SemEval 2013 XML exact field names (if not using HuggingFace)**
   - What we know: The dataset contains question, reference answers, student answer, and 5-way label per row. HuggingFace mirrors use: `id`, `question`, `reference_answer`, `student_answer`, `label`.
   - What's unclear: The original XML file element names (e.g., `<question>`, `<studentAnswer>`, `<accuracy>`) are not documented publicly without downloading the raw files. Several ASAG papers (Filighera 2024, Heilman & Madnani 2013) describe loading it but don't publish their parser.
   - Recommendation: Use HuggingFace as primary access path. Only fall back to XML if HF access fails. If XML is needed, refer to original GitHub repo (myrosia/semeval-2013-task7) for the exact schema after downloading.

2. **Multiple reference answers per question in HuggingFace format**
   - What we know: The HuggingFace Beetle dataset has `reference_answer` as a single string per row. Beetle questions have multiple valid reference answers (best, good, minimal tiers in original XML).
   - What's unclear: Whether the HF mirror provides only one reference answer or multiple per question (data suggests one per row, may be multiple rows per question with different references).
   - Recommendation: When grouping rows by question, collect all distinct `reference_answer` values as a list. Log how many reference answers per question to confirm completeness.

3. **annotator_id availability**
   - What we know: SCHM-01 specifies `annotator_id` as a field on AnswerRecord.
   - What's unclear: The HF datasets do not expose annotator IDs. The original Beetle/SciEntsBank XML may contain annotator info.
   - Recommendation: Set `annotator_id = None` for SemEval rows. The field exists for future datasets (professor's custom data) that may have annotator information.

4. **question_id stable identifier in HuggingFace format**
   - What we know: HF uses `id` as answer identifier, not question identifier. Questions are identified only by their text content.
   - What's unclear: Whether the `id` field encodes the question structure (e.g., "beetle_q1_a001" vs an opaque hash).
   - Recommendation: Derive `question_id` by hashing the question text (deterministic): `question_id = f"beetle_{hashlib.md5(question_text.encode()).hexdigest()[:8]}"`. Log the mapping for auditability. Alternatively, assign sequential IDs after deduplication.

---

## Sources

### Primary (HIGH confidence)
- Pydantic v2 official docs (docs.pydantic.dev/latest) — models, serialization, strict mode, Optional fields
- scikit-learn 1.8.0 official docs (scikit-learn.org) — LeaveOneGroupOut, StratifiedShuffleSplit APIs
- Python 3.9 official docs (docs.python.org/3.9) — importlib.metadata, pathlib, abc module
- HuggingFace datasets hub: nkazi/Beetle and nkazi/SciEntsBank dataset cards — field names, label schema, splits, row counts

### Secondary (MEDIUM confidence)
- ASAG2024 benchmark (arxiv.org/abs/2409.18596, 2024) — confirms [0,1] normalized grading scale as current standard
- HuggingFace Beetle dataset card — label distribution (correct: 1665 train, 5-way scheme verified)
- HuggingFace SciEntsBank dataset card — 197 questions, 10,804 rows, splits (train/test_ua/test_uq/test_ud)
- Pmc.ncbi.nlm.nih.gov PMC7334174 (Filighera "Fooling ASAG") — 3-way labeling scheme confirmed; SciEntsBank domain usage confirmed

### Tertiary (LOW confidence — verify before use)
- SemEval XML format details: inferred from HuggingFace field names and ASAG literature; actual XML element names not directly verified without downloading dataset files
- Grade scale mapping (correct=1.0, partially_correct_incomplete=0.5, contradictory/irrelevant/non_domain=0.0) — logical derivation; ASAG2024 confirms [0,1] normalization but does not specify this exact mapping for 5-way labels

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — Pydantic v2, sklearn, HuggingFace datasets, importlib.metadata all verified via official docs
- Architecture: HIGH — patterns are direct translations of official API docs; anti-patterns derived from known ASAG literature pitfalls
- Data format (HuggingFace): HIGH — field names verified from live HuggingFace dataset cards
- Data format (original XML): LOW — not directly verified without downloading dataset files
- Grade scale mapping: MEDIUM — [0,1] range confirmed by ASAG2024; specific 5-way-to-float mapping is a logical derivation, not from primary source
- Pitfalls: HIGH — derived from ASAG literature, Pydantic v2 migration notes, sklearn docs

**Research date:** 2026-02-20
**Valid until:** 2026-08-20 (stable libraries; HuggingFace dataset links may change)
