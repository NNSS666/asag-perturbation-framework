# ASAG Perturbation Framework

Perturbation-based robustness evaluation framework for Automated Short Answer Grading (ASAG) systems.

Companion repository for the paper presented at **IFKAD 2026** (Budapest, 1-3 July):

> **Sasso, F. & De Mauro, A.** (2026). *[Title TBD]*. Proceedings of IFKAD 2026.

## Research question

Do ASAG systems truly understand student response content, or do they rely on superficial cues? Standard metrics (accuracy, QWK) only measure agreement with human scores under normal conditions but cannot detect brittleness. This framework tests grader behaviour under controlled perturbations and produces robustness metrics that complement traditional evaluation.

## How it works

The framework applies **7 perturbation types** across **3 families** to student answers and measures whether the grader reacts correctly:

| Family | Expected behaviour | Perturbation types |
|---|---|---|
| **Invariance** | Score must NOT change | Synonym substitution, typo insertion |
| **Sensitivity** | Score MUST decrease | Negation insertion, key concept deletion, semantic contradiction |
| **Gaming** | Score must NOT increase | Rubric keyword echoing, fluent wrong extension |

Each answer is perturbed, re-graded, and the original vs. perturbed scores are compared to compute four metrics:

- **IVR_flip**: percentage of invariance pairs where the score changed
- **IVR_absdelta**: mean magnitude of score change on invariance pairs
- **SSR_directional**: percentage of sensitivity pairs where the score decreased
- **ASR_thresholded**: percentage of gaming pairs where a failing answer crossed the pass threshold

Evaluation runs under two protocols:
- **Protocol A (LOQO)**: leave-one-question-out cross-validation (unseen questions)
- **Protocol B**: within-question 80/20 split (known questions)

The delta between A and B is the **robustness drop**, measuring how much grader fragility increases on unseen questions.

## Datasets

Built on the [SemEval 2013 Task 7](https://aclanthology.org/S13-2045/) benchmark:

| Corpus | Domain | Questions | Answers |
|---|---|---|---|
| Beetle | Electricity & circuits | 42 | 5,199 |
| SciEntsBank | General science | 195 | 10,804 |

The loader interface is pluggable: integrating a new dataset requires only a loader module that maps to the canonical schema.

## Results (Beetle corpus)

### HybridGrader (trained ML baseline)

| Metric | Protocol A | Protocol B | Drop |
|---|:---:|:---:|:---:|
| IVR_flip | 33.7% | 17.9% | +15.8 pp |
| IVR_absdelta | 0.242 | 0.125 | +11.8 pp |
| SSR_directional | 14.0% | 12.0% | +2.0 pp |
| ASR_thresholded | 18.8% | 11.5% | +7.4 pp |

### GPT-5.4 mini (zero-shot LLM)

| Metric | Level 0 | Level 1 | Effect of reference answer |
|---|:---:|:---:|:---:|
| IVR_flip | 24.3% | 13.4% | −45% (better) |
| SSR_directional | 42.0% | 46.1% | +10% (better) |
| ASR_thresholded | 6.7% | 11.8% | +76% (worse) |

Key findings: the LLM is 3x more sensitive to meaning changes (SSR) and 3x less vulnerable to gaming (ASR) than the trained baseline. Providing a reference answer reduces invariance violations but increases gaming susceptibility, a trade-off invisible to single-metric evaluation.

## Project structure

```
src/asag/
├── schema/            # Canonical data models (QuestionRecord, AnswerRecord, PerturbationRecord)
├── loaders/           # Dataset loaders (SemEval 2013)
├── splitters/         # Protocol A (LOQO) and Protocol B (within-question) splitters
├── graders/           # Grader interface + HybridGrader (SBERT + logistic regression)
├── metrics/           # MetricCalculator (IVR, SSR, ASR)
├── perturbations/     # PerturbationEngine, generators (7 types), quality gates, cache
│   └── generators/    # Invariance, sensitivity, and gaming generators
├── evaluation/        # EvaluationEngine (Protocol A/B loops, robustness drop)
└── infra/             # Seeds, storage, run directories, versioning
tests/                 # 77 unit + E2E tests
scripts/               # Experiment runner
bibliography/          # 33-entry annotated bibliography with BibTeX
docs/                  # Methodology proposal and project documentation
```

## Installation

```bash
pip install -e .
```

For LLM grader support (OpenAI, Anthropic, Google):

```bash
pip install -e ".[llm]"
```

Requires Python 3.9+. The SBERT model (`all-MiniLM-L6-v2`) and NLTK data are downloaded automatically on first use.

## Quick start

```python
from asag.loaders import SemEval2013Loader
from asag.graders import HybridGrader
from asag.perturbations import PerturbationEngine
from asag.evaluation import EvaluationEngine

# 1. Load a dataset
questions, answers = SemEval2013Loader("beetle").load()

# 2. Generate perturbations (cached after first run)
engine = PerturbationEngine(seed=42)
perturbations, gate_log = engine.generate_all(answers, questions)

# 3. Evaluate a grader under both protocols
grader = HybridGrader()
eval_engine = EvaluationEngine(grader, corpus="beetle")
result = eval_engine.run(questions, answers, perturbations, protocols=["A", "B"])

# 4. Inspect results
for agg in result.protocol_a_aggregate:
    print(f"{agg.family}: IVR={agg.ivr_flip}, SSR={agg.ssr_directional}, ASR={agg.asr_thresholded}")
```

### Using your own grader

Any grader that implements `GraderInterface` works with the framework:

```python
from asag.graders.base import GraderInterface, GradeResult

class MyGrader(GraderInterface):
    @property
    def grader_name(self) -> str:
        return "my_custom_grader"

    def grade(self, question, rubric, student_answer, **kwargs):
        # Your grading logic here
        return GradeResult(label="correct", score=1.0, confidence=0.9)
```

### Using an LLM grader

```python
from asag.graders import LLMGrader

# Level 0: no reference answer (question + student answer only)
grader_l0 = LLMGrader(provider="openai", model="gpt-5.4-mini", level=0)

# Level 1: with reference answer
grader_l1 = LLMGrader(provider="openai", model="gpt-5.4-mini", level=1)
```

Supported providers: `"openai"`, `"anthropic"`, `"google"`. API keys must be set as environment variables (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`).

## Running experiments

```bash
# HybridGrader on Beetle (full pipeline)
python -m scripts.first_real_run

# LLM graders (3 models x 2 levels)
python -m scripts.run_llm_experiments --models gpt-5.4-mini --levels 0 1
python -m scripts.run_llm_experiments --resume  # crash recovery
```

## Running tests

```bash
pytest              # all tests
pytest -m "not slow"  # skip E2E tests
```

## Grading models

| Model | Type | Status |
|---|---|---|
| HybridGrader | Linguistic features + SBERT + logistic regression | Done |
| LLMGrader | Zero-shot LLM (OpenAI, Anthropic, Google) | Done |

## Quality gates

Invariance perturbations pass through a two-stage validation to ensure meaning is preserved:

1. **Gate 1 (SBERT)**: cosine similarity >= 0.85 between original and perturbed answer (synonym substitution only; typos bypass by construction)
2. **Gate 2 (Negation/antonym heuristic)**: blocks perturbations that accidentally introduced negation markers or antonyms

Gate 1 rejects about 40% of synonym substitutions, itself a finding about the unreliability of naive synonym replacement.

## References

- Ribeiro, M.T. et al. (2020) "Beyond accuracy: Behavioral testing of NLP models with CheckList", ACL 2020 (Best Paper)
- Dzikovska, M. et al. (2013) "SemEval-2013 Task 7", SemEval 2013
- Filighera, A. et al. (2024) "Cheating automatic short answer grading", IJAIED
- Ferrara, S. and Qunbar, S. (2022) "Validity arguments for AI-based automated scores", JEM

Full bibliography (33 entries) in [`bibliography/`](bibliography/).

## Citation

If you use this framework in your research, please cite:

```bibtex
@inproceedings{sasso2026asag,
  title     = {[Title TBD]},
  author    = {Sasso, Ferdinando and De Mauro, Andrea},
  booktitle = {Proceedings of IFKAD 2026},
  year      = {2026},
  address   = {Budapest, Hungary},
}
```

## License

MIT License. See [LICENSE](LICENSE) for details.
