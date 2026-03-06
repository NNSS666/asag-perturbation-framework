# ASAG Perturbation Framework

Perturbation-first evaluation framework for Automated Short Answer Grading (ASAG) systems.

This is the companion repository for my Master's thesis at LUISS Guido Carli, supervised by Prof. Andrea De Mauro.

## Research question

Do ASAG systems truly understand student response content, or do they rely on superficial cues? Standard metrics (accuracy, QWK) only measure agreement with human scores under normal conditions — they cannot detect brittleness. This framework tests grader behaviour under controlled perturbations and produces robustness metrics that complement traditional evaluation.

## How it works

The framework applies **7 perturbation types** across **3 families** to student answers and measures whether the grader reacts correctly:

| Family | Expected behaviour | Perturbation types |
|---|---|---|
| **Invariance** | Score must NOT change | Synonym substitution, typo insertion |
| **Sensitivity** | Score MUST decrease | Negation insertion, key concept deletion, semantic contradiction |
| **Gaming** | Score must NOT increase | Rubric keyword echoing, fluent wrong extension |

Each answer is perturbed, re-graded, and the original vs. perturbed scores are compared to compute four metrics:

- **IVR_flip** — % of invariance pairs where the score changed
- **IVR_absdelta** — mean magnitude of score change on invariance pairs
- **SSR_directional** — % of sensitivity pairs where the score decreased
- **ASR_thresholded** — % of gaming pairs where a failing answer crossed the pass threshold

Evaluation runs under two protocols:
- **Protocol A (LOQO)** — leave-one-question-out cross-validation (unseen questions)
- **Protocol B** — within-question 80/20 split (known questions)

The delta between A and B is the **robustness drop**, measuring how much grader fragility increases on unseen questions.

## Datasets

Built on the [SemEval 2013 Task 7](https://aclanthology.org/S13-2045/) benchmark:

| Corpus | Domain | Questions | Answers |
|---|---|---|---|
| Beetle | Electricity & circuits | 42 | 5,199 |
| SciEntsBank | General science | 195 | 10,804 |

The loader interface is pluggable — integrating a new dataset requires only a loader module that maps to the canonical schema.

## Preliminary results (HybridGrader × Beetle)

| Metric | Protocol B | Protocol A | Drop |
|---|:---:|:---:|:---:|
| IVR_flip | 34.1% | 53.9% | +19.8 pp |
| IVR_absdelta | 0.233 | 0.402 | +16.9 pp |
| SSR_directional | 16.6% | 32.3% | +15.7 pp |
| ASR_thresholded | 19.2% | 18.0% | −1.2 pp |

On unseen questions, the grader flips its score after a synonym swap in 54% of cases and detects negation only 32% of the time.

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

## Setup

```bash
pip install -r requirements.txt
```

Requires Python 3.9+. The SBERT model (`all-MiniLM-L6-v2`) and NLTK data are downloaded automatically on first use.

## Running an experiment

```bash
cd src
python -m scripts.first_real_run
```

This runs the full pipeline on Beetle with the HybridGrader: loads data, generates ~41k perturbations (with SBERT quality gates), evaluates under both protocols, and prints the results table. Takes ~80 min on Apple M1.

## Running tests

```bash
pytest
```

77 tests covering all modules. E2E tests are marked with `@pytest.mark.slow`.

## Grading models

| Model | Type | Status |
|---|---|---|
| HybridGrader | Linguistic features + SBERT + logistic regression | Done |
| DeBERTa-v3-base | Fine-tuned transformer | Next |
| ModernBERT-base | Fine-tuned transformer | Planned |
| GPT-4o | Zero-shot LLM with rubric prompt | Planned |

## Quality gates

Invariance perturbations pass through a two-stage validation to ensure meaning is preserved:

1. **Gate 1 (SBERT)** — cosine similarity ≥ 0.85 between original and perturbed answer (synonym substitution only; typos bypass by construction)
2. **Gate 2 (Negation/antonym heuristic)** — blocks perturbations that accidentally introduced negation markers or antonyms

Gate 1 rejects ~40% of synonym substitutions — itself a finding about the unreliability of naive synonym replacement.

## References

- Ribeiro, M.T. et al. (2020) "Beyond accuracy: Behavioral testing of NLP models with CheckList", ACL 2020 (Best Paper)
- Dzikovska, M. et al. (2013) "SemEval-2013 Task 7", SemEval 2013
- Filighera, A. et al. (2024) "Cheating automatic short answer grading", IJAIED
- Ferrara, S. and Qunbar, S. (2022) "Validity arguments for AI-based automated scores", JEM

Full bibliography (33 entries) in [`bibliography/`](bibliography/).

## License

This project is part of ongoing academic research. Please contact the author before reuse.
