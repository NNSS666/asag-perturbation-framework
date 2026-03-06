# Methodological Proposal — ASAG Perturbation Framework

**Ferdinando Sasso** — Supervisor: Prof. Andrea De Mauro, LUISS Guido Carli
March 2026

---

## 1. Methodology

### Research question

Do Automated Short Answer Grading (ASAG) systems truly understand student response content, or do they rely on superficial cues? Traditional metrics (accuracy, QWK) cannot answer this question — they only measure agreement with human scores under normal conditions.

### Approach: controlled perturbations

The method builds on the CheckList taxonomy (Ribeiro et al., 2020 — ACL Best Paper), applied here for the first time to the ASAG domain. Systematic modifications are generated on student answers, and the grader's reaction is measured. Three perturbation families test three distinct dimensions:

**Invariance** — Changes that do NOT alter meaning (synonyms, typos). If the score changes, the grader is unstable.

**Sensitivity** — Changes that DO alter meaning (negations, key concept deletion, contradictions). If the score does not change, the grader is not understanding the content.

**Gaming** — Attempts to deceive the grader (keyword stuffing, fluent but wrong extensions). If the score increases, the grader is vulnerable to manipulation.

### Dual protocol

- **Protocol A (LOQO):** The grader is trained on all questions except one, and tested on the held-out question. This simulates real-world usage (unseen questions).
- **Protocol B (Within-question):** 80/20 split within each question. This measures performance under optimal conditions.

The comparison between A and B yields the **robustness drop**: the degree to which grader performance degrades on unseen questions. This delta is the framework's core contribution.

### Metrics

| Metric | Family | What it measures |
|--------|--------|-----------------|
| IVR_flip | Invariance | % of cases where the score changes when it should not |
| IVR_absdelta | Invariance | Mean magnitude of score change |
| SSR_directional | Sensitivity | % of cases where the score decreases after semantic alteration |
| ASR_thresholded | Gaming | % of failing answers that cross the pass threshold |

### Perturbation validation

Invariance perturbations pass through two quality gates:
- **Gate 1:** SBERT semantic similarity >= 0.85 (fixed threshold, not optimized)
- **Gate 2:** Heuristic check for accidental negations/antonyms

Rejected perturbations are not regenerated: the rejection rate is itself a research finding.

---

## 2. Experiment plan and first tests

### Planned models

| Model | Type | Status |
|-------|------|--------|
| HybridGrader (custom baseline) | Linguistic features + SBERT + logistic regression | **Tested** |
| DeBERTa-v3-base (Microsoft) | Fine-tuned transformer | Planned |
| ModernBERT-base (Answer.AI) | Fine-tuned transformer | Planned |
| GPT-4o (OpenAI) | Zero-shot LLM with rubric prompt | Planned |

### Datasets

SemEval 2013 Task 7: Beetle (42 questions, 5,199 answers) and SciEntsBank (195 questions, 10,804 answers). The system is designed to integrate additional datasets (including Prof. De Mauro's) via a dedicated loader module.

### First test completed

Full run on Beetle with HybridGrader — 41,378 perturbations generated, 7 types, both protocols.

| Metric | Proto B (seen questions) | Proto A (unseen questions) | Robustness Drop |
|--------|:---:|:---:|:---:|
| IVR_flip | 34.1% | **53.9%** | **+19.8 pp** |
| IVR_absdelta | 0.233 | **0.402** | **+16.9 pp** |
| SSR_directional | 16.6% | **32.3%** | **+15.7 pp** |
| ASR_thresholded | 19.2% | **18.0%** | -1.2 pp |

**Reading the results:** The baseline grader changes its score in 54% of cases after a simple synonym substitution (Proto A), and detects negations only 32% of the time. The consistent robustness drop (+16-20 pp) confirms that fragility worsens on unseen questions. These results establish the baseline; transformer models and GPT-4o will determine whether more sophisticated architectures are also more robust.

**Gate 1 rejection: 40.3%** — Nearly half of WordNet synonym substitutions alter meaning according to SBERT. This is an interesting finding in itself on the reliability of automatic synonym substitution.

### Next steps

1. Fine-tune DeBERTa-v3 and ModernBERT under LOQO (3 seeds per model)
2. Evaluate GPT-4o via API (zero-shot, rubric-driven prompt)
3. Statistical analysis (Wilcoxon signed-rank, Cliff's delta) and visualizations
4. Integrate Prof. De Mauro's dataset (after meeting with Gabriele)

---

## 3. References

- Ribeiro, M.T., Wu, T., Guestrin, C., Singh, S. (2020). Beyond Accuracy: Behavioral Testing of NLP Models with CheckList. *ACL 2020* (Best Paper).
- Filighera, A., et al. (2024). Cheating Automatic Short Answer Grading with the Adversarial Usage of Adjectives and Adverbs. *Int. J. of AI in Education*, 34(2).
- Burrows, S., Gurevych, I., Stein, B. (2015). The Eras and Trends of Automatic Short Answer Grading. *Int. J. of AI in Education*, 25(1).
- Sung, C., Dhamecha, T.I., Mukhi, N. (2019). Improving Short Answer Grading Using Transformer-Based Pre-Training. *AIED 2019*.
- Heilman, M., Madnani, N. (2015). The Impact of Training Data on Automated Short Answer Scoring Performance. *ETS Research Report Series*.
- Messick, S. (1989). Validity. In R.L. Linn (Ed.), *Educational Measurement* (3rd ed.).
- Kane, M.T. (2006). Validation. In R.L. Brennan (Ed.), *Educational Measurement* (4th ed.).

---

*All results are fully reproducible: `scripts/first_real_run.py`*
