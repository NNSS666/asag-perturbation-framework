# Architecture Research

**Domain:** Perturbation-based ASAG evaluation framework (academic research, Python/PyTorch)
**Researched:** 2026-02-20
**Confidence:** HIGH

---

## Standard Architecture

### System Overview

The framework is a pipeline of five sequential subsystems. Data flows left to right; no subsystem reaches backward.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              ORCHESTRATION LAYER                             │
│            Experiment Config (YAML/Hydra) + Seed Manager + CLI              │
└─────────────────────┬───────────────────────────────────────────────────────┘
                      │ drives
          ┌───────────┼───────────────────────────────┐
          v           v                               v
┌─────────────────┐  ┌─────────────────────────────┐  ┌───────────────────────┐
│  DATA PIPELINE  │  │   PERTURBATION ENGINE        │  │   GRADING MODELS      │
│                 │  │                              │  │                       │
│ DatasetLoader   │→ │  PerturbationRegistry        │→ │  TransformerGrader    │
│ Preprocessor    │  │  InvariancePerturbations     │  │  HybridGrader         │
│ DataSplitter    │  │  SensitivityPerturbations    │  │  LLMGrader            │
│ (LOQO folds)    │  │  GamingPerturbations         │  │  GraderInterface      │
└─────────────────┘  └─────────────────────────────┘  └───────────────────────┘
                                    │                           │
                                    └──────────┬────────────────┘
                                               v
                              ┌────────────────────────────────┐
                              │      EVALUATION ENGINE          │
                              │                                │
                              │  PerturbationRunner            │
                              │  IVRCalculator                 │
                              │  SSRCalculator                 │
                              │  ASRCalculator                 │
                              │  LOQOValidator                 │
                              │  ResultAggregator              │
                              └──────────────┬─────────────────┘
                                             │
                                             v
                              ┌────────────────────────────────┐
                              │       REPORTING LAYER           │
                              │                                │
                              │  TableGenerator                │
                              │  FigureGenerator               │
                              │  StatisticsRunner              │
                              │  ReportCompiler                │
                              └────────────────────────────────┘
```

---

### Component Responsibilities

| Component | Responsibility | Communicates With |
|-----------|----------------|-------------------|
| **Orchestrator** | Parses config, seeds RNG, launches pipeline, manages experiment lifecycle | All subsystems (drives, does not process data) |
| **DatasetLoader** | Loads raw SRA / SemEval 2013 / custom datasets; normalises to canonical schema | Preprocessor |
| **Preprocessor** | Tokenization, lowercasing, deduplication, label normalisation | DataSplitter |
| **DataSplitter** | Produces LOQO fold definitions; materialises train/test splits by question | PerturbationEngine, GradingModels |
| **PerturbationRegistry** | Central registry of all perturbation functions, tagged by family | PerturbationRunner |
| **InvariancePerturbations** | Generates meaning-preserving changes (paraphrase, synonym swap, whitespace, casing, contraction, back-translation) | PerturbationRegistry |
| **SensitivityPerturbations** | Generates meaning-altering changes (word deletion, negation insertion, key-concept swap, partial answer) | PerturbationRegistry |
| **GamingPerturbations** | Generates gaming attempts (keyword stuffing, trigger injection, answer elongation, irrelevant sentence append) | PerturbationRegistry |
| **TransformerGrader** | Fine-tunes BERT/RoBERTa on LOQO train fold; outputs grade for original + all perturbed variants | EvaluationEngine |
| **HybridGrader** | Computes handcrafted features (SBERT cosine similarity, lexical overlap, length ratio) + XGBoost/LR head; no fine-tuning required | EvaluationEngine |
| **LLMGrader** | Rubric-driven zero-shot/few-shot prompting of commercial and open-source LLMs via API; logs prompts and responses | EvaluationEngine |
| **GraderInterface** | Abstract base class enforcing `grade(question, reference, student_answer) -> score`; all graders implement this | TransformerGrader, HybridGrader, LLMGrader |
| **PerturbationRunner** | For each (answer, perturbation), calls every registered grader; batches calls for efficiency | EvaluationEngine metrics |
| **IVRCalculator** | Computes Invariance Rate: fraction of invariance perturbations where grade does NOT change | ResultAggregator |
| **SSRCalculator** | Computes Sensitivity Rate: fraction of sensitivity perturbations where grade DOES change | ResultAggregator |
| **ASRCalculator** | Computes Attack Success Rate: fraction of gaming perturbations where grade increases unjustifiably | ResultAggregator |
| **LOQOValidator** | Iterates LOQO folds, coordinates training and evaluation per fold, collects fold-level results | ResultAggregator |
| **ResultAggregator** | Merges per-fold, per-question, per-perturbation-family results into a unified result store (parquet/JSON) | ReportingLayer |
| **TableGenerator** | Renders per-model, per-perturbation-family metric tables in LaTeX and CSV | ReportCompiler |
| **FigureGenerator** | Renders bar charts, heatmaps, and per-question breakdown plots (matplotlib/seaborn) | ReportCompiler |
| **StatisticsRunner** | Runs Wilcoxon signed-rank tests and confidence interval estimation across LOQO folds | ReportCompiler |
| **ReportCompiler** | Assembles all tables and figures into a final output directory ready for paper inclusion | (end output) |

---

## Recommended Project Structure

```
tesi/
├── config/                        # Experiment configuration (Hydra)
│   ├── experiment.yaml            # Default experiment config
│   ├── datasets/                  # Dataset-specific configs
│   │   ├── sra.yaml
│   │   └── semeval2013.yaml
│   ├── models/                    # Grader configs
│   │   ├── transformer.yaml
│   │   ├── hybrid.yaml
│   │   └── llm.yaml
│   └── perturbations/             # Perturbation family configs
│       ├── invariances.yaml
│       ├── sensitivities.yaml
│       └── gaming.yaml
│
├── src/
│   ├── data/                      # Data pipeline
│   │   ├── __init__.py
│   │   ├── loaders.py             # DatasetLoader: SRA, SemEval, custom CSV
│   │   ├── preprocessor.py        # Tokenization, cleaning, label normalisation
│   │   ├── schema.py              # Canonical dataclass: Question, Answer, Label
│   │   └── splitter.py            # LOQO fold generator
│   │
│   ├── perturbations/             # Perturbation engine
│   │   ├── __init__.py
│   │   ├── base.py                # BasePerturbation abstract class
│   │   ├── registry.py            # PerturbationRegistry
│   │   ├── invariances/           # Invariance family
│   │   │   ├── paraphrase.py      # LLM-assisted paraphrase
│   │   │   ├── synonym_swap.py    # Rule-based synonym substitution
│   │   │   ├── casing.py          # Case normalisation variants
│   │   │   ├── contraction.py     # Expand/contract contractions
│   │   │   └── back_translation.py
│   │   ├── sensitivities/         # Sensitivity family
│   │   │   ├── word_deletion.py
│   │   │   ├── negation.py        # Insert/remove negation
│   │   │   ├── concept_swap.py    # Swap key concept for related-but-wrong
│   │   │   └── partial_answer.py  # Truncate answer at key information
│   │   └── gaming/                # Gaming family
│   │       ├── keyword_stuffing.py
│   │       ├── trigger_injection.py
│   │       └── answer_elongation.py
│   │
│   ├── models/                    # Grading models
│   │   ├── __init__.py
│   │   ├── base.py                # GraderInterface abstract base class
│   │   ├── transformer_grader.py  # BERT/RoBERTa fine-tune + inference
│   │   ├── hybrid_grader.py       # SBERT features + sklearn head
│   │   └── llm_grader.py          # LLM API wrapper + prompt templates
│   │
│   ├── evaluation/                # Evaluation engine
│   │   ├── __init__.py
│   │   ├── runner.py              # PerturbationRunner: pairs answers x perturbations x models
│   │   ├── metrics.py             # IVR, SSR, ASR calculators
│   │   ├── loqo.py                # LOQO cross-validation coordinator
│   │   └── aggregator.py          # Merge fold results → result store
│   │
│   └── reporting/                 # Reporting layer
│       ├── __init__.py
│       ├── tables.py              # LaTeX + CSV table generation
│       ├── figures.py             # matplotlib/seaborn plots
│       ├── statistics.py          # Wilcoxon tests, CIs
│       └── compiler.py            # Assembles final output directory
│
├── scripts/
│   ├── run_experiment.py          # CLI entrypoint (calls Orchestrator)
│   ├── generate_perturbations.py  # Standalone: generate + cache perturbations
│   └── generate_report.py         # Standalone: re-run reporting from saved results
│
├── data/
│   ├── raw/                       # Raw downloaded datasets (gitignored)
│   ├── processed/                 # Preprocessed canonical format
│   └── perturbations/             # Cached perturbation outputs (jsonl per answer)
│
├── results/                       # Experiment outputs (gitignored, or DVC-tracked)
│   ├── {experiment_id}/
│   │   ├── fold_results.parquet
│   │   ├── aggregated_metrics.json
│   │   ├── tables/
│   │   └── figures/
│
├── tests/
│   ├── test_data/
│   ├── test_perturbations/
│   ├── test_models/
│   └── test_evaluation/
│
├── notebooks/                     # Exploratory analysis only (not pipeline)
│
├── pyproject.toml
├── requirements.txt
└── README.md
```

### Structure Rationale

- **`src/data/`:** Isolated from all other subsystems. Changing dataset format only touches this module.
- **`src/perturbations/`:** Each perturbation is a file. Adding a new perturbation = adding one file and registering it. The registry is the only coupling point.
- **`src/models/`:** The GraderInterface ensures evaluation engine never depends on concrete model types. New graders plug in without touching evaluation logic.
- **`src/evaluation/`:** Pure computation — no I/O except reading from data and writing results. Keeps the critical path fast and testable.
- **`src/reporting/`:** Reads only from the result store. Can be re-run independently without re-running experiments.
- **`data/perturbations/`:** Perturbations are generated once and cached. LLM-assisted perturbations are expensive; caching prevents redundant API calls and ensures reproducibility.
- **`results/`:** Experiment outputs keyed by experiment ID. One run = one directory. Never overwrite.

---

## Architectural Patterns

### Pattern 1: Registry Pattern for Perturbations

**What:** A central `PerturbationRegistry` maps string names to perturbation function objects. The runner iterates the registry, not individual files.

**When to use:** Always — this enables adding, disabling, or grouping perturbations via config YAML without changing pipeline code.

**Trade-offs:** Slight indirection, but enormous flexibility. Trivially supports ablations (run with only one family) and extensibility (custom perturbations).

**Example:**
```python
# src/perturbations/registry.py
class PerturbationRegistry:
    def __init__(self):
        self._perturbations: dict[str, BasePerturbation] = {}

    def register(self, name: str, family: str, fn: BasePerturbation) -> None:
        self._perturbations[name] = fn
        fn.family = family

    def get_family(self, family: str) -> list[BasePerturbation]:
        return [p for p in self._perturbations.values() if p.family == family]

    def get_all(self) -> list[BasePerturbation]:
        return list(self._perturbations.values())

# src/perturbations/invariances/synonym_swap.py
class SynonymSwapPerturbation(BasePerturbation):
    def apply(self, answer: str) -> str:
        # rule-based NLTK WordNet synonym swap
        ...

# registered at startup:
registry.register("synonym_swap", family="invariance", fn=SynonymSwapPerturbation())
```

### Pattern 2: GraderInterface (Abstract Base Class)

**What:** All three grader types implement a single interface. The evaluation runner calls only `grader.grade(question, reference, answer) -> float`.

**When to use:** Always — the evaluation engine must be model-agnostic. Statistical analysis is identical across grader types.

**Trade-offs:** Forces conformity on heterogeneous implementations (transformer requires GPU, LLM requires API key, hybrid requires sklearn). Minor complexity at implementation time, major gain at evaluation time.

**Example:**
```python
# src/models/base.py
from abc import ABC, abstractmethod

class GraderInterface(ABC):
    @abstractmethod
    def grade(self, question: str, reference: str, answer: str) -> float:
        """Return normalised score in [0, 1]."""
        ...

    def batch_grade(self, records: list[dict]) -> list[float]:
        """Default: loop. Override for batched GPU inference."""
        return [self.grade(**r) for r in records]
```

### Pattern 3: Cache-First Perturbation Generation

**What:** Perturbations are generated in a separate, deterministic step and stored as JSONL files keyed by (dataset, answer_id, perturbation_name). The evaluation runner reads from cache; it never generates perturbations.

**When to use:** Always — LLM-assisted perturbations (paraphrase, back-translation) are expensive and non-deterministic on repeated calls. Caching ensures reproducibility and saves API budget.

**Trade-offs:** Extra storage (~100MB for 10-15 perturbations per answer on a 10K-answer dataset), but saves hours of API calls on re-runs.

**Example:**
```python
# Cache key: (dataset_id, answer_id, perturbation_name)
# data/perturbations/sra/beetle/q001_a042/paraphrase.jsonl
{
  "original": "The switch completes the circuit",
  "perturbed": "Closing the switch allows current to flow",
  "perturbation": "paraphrase",
  "family": "invariance",
  "model": "gpt-4o",
  "seed": 42,
  "generated_at": "2026-02-20T10:00:00Z"
}
```

### Pattern 4: LOQO as Outer Loop

**What:** Leave-one-question-out CV is the outermost loop of the experiment. For each fold, the question is held out, the grader trains (or is configured) on all other questions, then evaluated on the held-out question's original + perturbed answers.

**When to use:** Always — this is the methodologically correct cross-question generalisation evaluation per Heilman & Madnani (2015). Without it, results overfit to seen questions.

**Trade-offs:** N-fold compute cost (N = number of unique questions). For TransformerGrader this is expensive — plan for GPU parallelism or cloud compute. HybridGrader and LLMGrader are cheaper (no fine-tuning per fold).

```python
# src/evaluation/loqo.py
class LOQOValidator:
    def run(self, dataset, grader, runner):
        questions = dataset.unique_questions()
        fold_results = []
        for held_out_q in questions:
            train = dataset.exclude_question(held_out_q)
            test  = dataset.only_question(held_out_q)
            grader.fit(train)             # no-op for LLMGrader
            results = runner.evaluate(test, grader)
            fold_results.append(results)
        return fold_results
```

---

## Data Flow

### Full Pipeline Flow

```
[Config YAML + CLI args]
        |
        v
[Orchestrator: seed RNG, resolve config, create experiment_id]
        |
        v
[DatasetLoader: load SRA/SemEval XML → canonical schema]
        |
        v
[Preprocessor: clean, normalise labels → AnswerRecord list]
        |
        v
[DataSplitter: generate LOQO fold definitions]
        |
        v
[PerturbationRunner: for each answer, load/generate perturbations from cache]
        |
        v  (parallel across grader types)
[TransformerGrader.grade()]  [HybridGrader.grade()]  [LLMGrader.grade()]
        |                            |                        |
        └────────────────────────────┴────────────────────────┘
                                     |
                                     v
             [GradingResultStore: answer_id x grader x perturbation → score]
                                     |
                                     v
              [IVRCalculator / SSRCalculator / ASRCalculator]
                                     |
                                     v
                    [LOQOValidator: aggregate across folds]
                                     |
                                     v
                      [ResultAggregator: write results/]
                                     |
                                     v
            [TableGenerator + FigureGenerator + StatisticsRunner]
                                     |
                                     v
                       [ReportCompiler: output/]
```

### Canonical Data Schema

The common data representation used between all subsystems:

```python
# src/data/schema.py
@dataclass
class AnswerRecord:
    dataset_id: str           # "sra_beetle" | "semeval2013" | "custom"
    question_id: str          # Unique per question
    answer_id: str            # Unique per student answer
    question_text: str
    reference_answer: str
    student_answer: str
    gold_label: float         # Normalised to [0, 1]
    original_label_str: str   # Keep original for debugging

@dataclass
class PerturbedAnswerRecord:
    base: AnswerRecord
    perturbation_name: str    # e.g. "synonym_swap"
    family: str               # "invariance" | "sensitivity" | "gaming"
    perturbed_text: str
    expected_grade_change: str  # "none" | "decrease" | "increase"

@dataclass
class GradingResult:
    answer_id: str
    perturbation_name: str    # "original" for baseline
    grader_name: str
    score: float              # Normalised [0, 1]
    raw_response: str | None  # LLM raw output if applicable
```

### Metric Computation Flow

```
GradingResult rows (original score + perturbed scores)
        |
        v
IVR = |{invariance perturbations where |score_perturbed - score_original| < threshold}|
      / |{all invariance perturbations}|

SSR = |{sensitivity perturbations where score changed in expected direction}|
      / |{all sensitivity perturbations}|

ASR = |{gaming perturbations where score_perturbed > score_original}|
      / |{all gaming perturbations}|
        |
        v
Computed per-question, per-grader, per-perturbation-family
Aggregated via LOQO: mean ± std across folds
        |
        v
Statistical test: Wilcoxon signed-rank (paired, non-parametric)
comparing grader A vs grader B across fold-level metric vectors
```

---

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| OpenAI API (GPT-4o, GPT-4-turbo) | Synchronous REST via `openai` Python SDK; retry with backoff | Log every prompt + response; cache results to avoid re-billing |
| Hugging Face Hub | `transformers.AutoModel.from_pretrained()` for BERT/RoBERTa | Pin model hash in config for reproducibility |
| Open-source LLM APIs (Mistral, LLaMA via together.ai or local vLLM) | Same `openai`-compatible interface; switch via base_url config | Use same LLMGrader class, different config |
| NLTK / WordNet | Local; used for synonym swap | Download `wordnet` corpus once at setup |
| SemEval 2013 dataset | XML files from GitHub (myrosia/semeval-2013-task7); parsed by DatasetLoader | Structure: Beetle + SciEntsBank subsets; 3-way or 5-way labels |
| Custom dataset (professor) | CSV/Excel → DatasetLoader with custom adapter | Adapter pattern: implement `DatasetLoader.load_custom()` |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| DataPipeline → PerturbationEngine | `list[AnswerRecord]` passed directly | No shared state; pure function call |
| PerturbationEngine → EvaluationEngine | Cached JSONL files on disk; runner reads cache | Decoupling: perturbations can be regenerated without re-running evaluation |
| EvaluationEngine → GradingModels | `GraderInterface.grade()` calls | Graders are stateless after fitting; thread-safe for batch evaluation |
| EvaluationEngine → ReportingLayer | Parquet result store on disk | Reporter reads from files; can be re-run on saved results without re-grading |
| Orchestrator → All | Hydra config dict; experiment_id | One-way: Orchestrator passes config down, never receives results back |

---

## Suggested Build Order

Build bottom-up: each layer depends on the one above.

| Order | Component | Reason |
|-------|-----------|--------|
| 1 | **Canonical schema + DatasetLoader (SRA/SemEval)** | Everything else depends on having real data. Validates dataset assumptions early. |
| 2 | **Preprocessor + DataSplitter (LOQO)** | LOQO logic must be correct before any metrics are computed. Establish fold definitions once and freeze. |
| 3 | **GraderInterface + HybridGrader** | Fastest grader to implement (no GPU, no API). Use it to validate evaluation machinery end-to-end before adding complexity. |
| 4 | **Evaluation metrics (IVR, SSR, ASR) + ResultAggregator** | Build and unit-test metrics on dummy grading results. Pin expected values with hand-computed examples. |
| 5 | **PerturbationRegistry + rule-based perturbations (invariances, sensitivities, gaming)** | Rule-based first — deterministic, no API cost. LLM-assisted last (expensive, non-deterministic). |
| 6 | **PerturbationRunner + end-to-end integration (HybridGrader + rule perturbations)** | First complete pipeline run. Smoke-test with small data slice. |
| 7 | **TransformerGrader (BERT/RoBERTa fine-tuning)** | Requires GPU. Build after pipeline is validated so training is purposeful, not exploratory. |
| 8 | **LLMGrader + LLM-assisted perturbations** | Last — API budget and latency. Cache all outputs on first run. |
| 9 | **Reporting layer (tables, figures, stats)** | After all results are stable. Statistical tests require finalized result data. |
| 10 | **Custom dataset adapter** | Plug in when professor's dataset arrives. DatasetLoader adapter pattern makes this a one-file addition. |

---

## Anti-Patterns

### Anti-Pattern 1: Entangled Pipeline Stages

**What people do:** Write one large script that loads data, generates perturbations, grades, computes metrics, and plots all in sequence, with intermediate results in memory.

**Why it's wrong:** A crash at step 6 of 8 loses all work. LLM API calls are non-idempotent and billable. Debugging requires re-running the whole experiment. Perturbation generation and model evaluation run at very different speeds.

**Do this instead:** Materialise outputs between every major stage (preprocessed data as parquet, perturbations as JSONL, grading results as parquet). Each stage reads from disk, writes to disk. Stages are independently re-runnable.

### Anti-Pattern 2: Grader-Specific Evaluation Logic

**What people do:** Write IVR computation inside the transformer grader, SSR inside the LLM grader, ASR inside the hybrid grader.

**Why it's wrong:** Metrics become impossible to compare consistently across graders. Any change to the metric definition requires changes in multiple places.

**Do this instead:** All graders output only `score: float`. All metric computation lives exclusively in `src/evaluation/metrics.py`. Graders are black boxes to the evaluation engine.

### Anti-Pattern 3: Non-Deterministic Perturbation on Every Run

**What people do:** Call the LLM API inside the PerturbationRunner, generating new perturbations each evaluation run.

**Why it's wrong:** Results are not reproducible. API costs multiply with every re-run. Academic papers require the exact perturbation set used to be fixable.

**Do this instead:** Run `scripts/generate_perturbations.py` once, cache to `data/perturbations/`, commit the cache (or DVC-track it). The runner reads from cache; generation is a one-time operation.

### Anti-Pattern 4: Computing Metrics on Full Dataset (Not Per-Fold)

**What people do:** Compute IVR/SSR/ASR on the full test set, then aggregate. Report one number per grader.

**Why it's wrong:** This leaks question-level information across folds and inflates confidence. Statistical tests require per-fold vectors, not a single aggregate.

**Do this instead:** Compute metrics at fold level (per held-out question). Aggregation (mean, std) and statistical tests operate on the fold-level vector of N metric values, where N = number of unique questions.

### Anti-Pattern 5: Hardcoding Dataset-Specific Logic in Core Pipeline

**What people do:** Write `if dataset == "sra": ... elif dataset == "semeval": ...` conditionals scattered throughout the preprocessor, runner, and metrics code.

**Why it's wrong:** Adding the custom professor dataset requires changes in multiple files. Dataset quirks contaminate clean pipeline logic.

**Do this instead:** All dataset differences are handled inside `DatasetLoader` adapters. The canonical `AnswerRecord` schema is the contract. After loading, the pipeline is dataset-agnostic.

---

## Scaling Considerations

This is a research tool, not a production system. Scaling concerns are compute-oriented, not user-load-oriented.

| Concern | At small scale (SRA Beetle, ~200 answers) | At medium scale (full SemEval 2013, ~10K answers) | At full scale (custom + public datasets) |
|---------|------------------------------------------|--------------------------------------------------|----------------------------------------|
| Perturbation generation | Run inline, minutes | Cache mandatory; LLM calls ~hours | Parallelize with async API calls |
| TransformerGrader training | CPU feasible for smoke test | GPU required (LOQO = N fine-tunes) | GPU cluster or cloud spot instances |
| LLM API costs | Negligible | Budget-sensitive; ~$5-50 depending on model | Rate-limit + cost-cap in LLMGrader |
| Metric computation | In-memory | In-memory | Pandas/Polars on parquet; still in-memory |
| Result storage | JSON fine | Parquet mandatory for efficient query | Parquet; consider DuckDB for interactive analysis |

### Scaling Priorities

1. **First bottleneck:** TransformerGrader LOQO training — N fine-tuning runs (N = number of questions). Mitigate by using a fast backbone (distilBERT for development, full RoBERTa for final results) and parallelising folds across GPUs.
2. **Second bottleneck:** LLM API rate limits during perturbation generation and LLM grading. Mitigate with async batching (`asyncio` + `httpx`), exponential backoff, and caching.

---

## Sources

- Ribeiro et al. (2020), "Beyond Accuracy: Behavioral Testing of NLP Models with CheckList" — [ACL Anthology](https://aclanthology.org/2020.acl-main.442/) — Establishes INV/DIR/MFT perturbation taxonomy; direct precedent for this framework's three perturbation families. MEDIUM confidence.
- Heilman & Madnani (2015), "The Impact of Training Data on Automated Short Answer Scoring Performance" — [ACL Anthology](https://aclanthology.org/W15-0610/) — Establishes LOQO as gold standard for cross-question evaluation. MEDIUM confidence.
- Filighera et al. (2024), adversarial ASAG (per PROJECT.md reference) — Black-box adversarial attack on BERT/RoBERTa ASAG; confirms sensitivity of transformer graders to surface-level perturbations. MEDIUM confidence (paper referenced in project, not directly verified via fetch).
- GradingAttack (2025) — [arxiv 2602.00979](https://arxiv.org/html/2602.00979) — Grading Input Alignment + Adversarial Prompt Generation + Evaluation component architecture; informs GraderInterface and evaluation design. HIGH confidence (directly fetched).
- ASAG2024 Benchmark — [arXiv 2409.18596](https://arxiv.org/abs/2409.18596) — Canonical schema: question, reference answer, student answer, normalized label. Informs AnswerRecord schema. MEDIUM confidence (abstract verified).
- Hybrid ASAG approach (MDPI 2024) — [ResearchGate](https://www.researchgate.net/publication/381911595_A_Hybrid_Approach_for_Automated_Short_Answer_Grading) — SBERT cosine similarity + XGBoost head pattern; validates HybridGrader design. MEDIUM confidence.
- "Reproducibility in ML" best practices — [neptune.ai](https://neptune.ai/blog/how-to-solve-reproducibility-in-ml) — Seed logging, config versioning, environment pinning. MEDIUM confidence.
- SemEval 2013 Task 7 dataset — [GitHub myrosia/semeval-2013-task7](https://github.com/myrosia/semeval-2013-task7) — Beetle + SciEntsBank subsets, XML format, CC-BY-SA license. HIGH confidence (official source).

---

*Architecture research for: Perturbation-based ASAG evaluation framework*
*Researched: 2026-02-20*
