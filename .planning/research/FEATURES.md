# Feature Research

**Domain:** Perturbation-based ASAG evaluation framework (academic research tool)
**Researched:** 2026-02-20
**Confidence:** MEDIUM-HIGH (grounded in published papers; IVR/SSR/ASR terminology is project-specific, not yet canonized in literature)

---

## Feature Landscape

### Table Stakes (Reviewers and Co-Authors Expect These)

Features that must exist for the paper to be credible. Missing these = the contribution looks incomplete or methodologically weak.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Perturbation engine: invariance family | Any robustness paper must test meaning-preserving changes; the entire IVR metric depends on it | MEDIUM | Synonym substitution, paraphrase, back-translation, casing/whitespace; rule-based is sufficient for deterministic invariances |
| Perturbation engine: sensitivity family | Any robustness paper must test meaning-changing changes; the SSR metric depends on it | MEDIUM | Negation insertion, key-concept deletion, wrong-entity substitution; must demonstrably change the correct grade |
| Perturbation engine: gaming/adversarial family | Filighera 2024 and Ding 2020 establish gaming perturbations as table stakes for ASAG robustness papers; the ASR metric depends on it | MEDIUM-HIGH | Adjective/adverb stuffing, universal trigger phrases, irrelevant-but-plausible content; rule-based + LLM-assisted hybrid |
| Semantic preservation check for perturbations | Without this, reviewers will question whether "invariance" perturbations actually preserve meaning | MEDIUM | SBERT cosine similarity threshold (>= 0.85 recommended); applied post-generation as filter |
| IVR computation (Invariance Violation Rate) | Core novel metric; the paper's central claim hinges on showing graders fail on meaning-preserving inputs | LOW | Fraction of invariance perturbations where grader changes its score vs. original; per-perturbation-type and aggregate |
| SSR computation (Sensitivity Success Rate) | Paired metric to IVR; measures whether graders respond correctly to meaning-changing inputs | LOW | Fraction of sensitivity perturbations where grader score changes in correct direction; per-perturbation-type and aggregate |
| ASR computation (Attack Success Rate) | Standard adversarial metric; measures gaming vulnerability; used in GradingAttack 2025, Ding 2020, Filighera 2024 | LOW | Fraction of gaming perturbations where incorrect answers receive passing grade from grader |
| SRA / SemEval 2013 dataset support | The paper needs to be validated on standard benchmarks; SciEntsBank and Beetle are the canonical ASAG evaluation corpora | MEDIUM | The SemEval 2013 task 7 protocol defines unseen-answers (A), unseen-questions (Q), unseen-domains (D) splits — use Q and D |
| Supervised transformer-based grading model | BERT-family fine-tuned on the training split is the baseline every ASAG paper tests against | HIGH | Training, LOQO cross-validation, inference; use HuggingFace Transformers |
| LLM-based rubric-driven grading model | "Rubric-Conditioned LLM Grading" (arXiv 2601.08843) establishes this as the modern comparison point | MEDIUM | Zero-shot and few-shot with rubric in prompt; test at least 2 LLMs (GPT-4o and one open-source) |
| Leave-one-question-out (LOQO) cross-validation | Heilman & Madnani 2015 establish LOQO as the gold standard for cross-question generalization eval in ASAG | HIGH | Train on all-but-one question, test on held-out; repeat for all questions; expensive but non-negotiable |
| Within-question and cross-question metric breakdowns | Reviewers will ask whether robustness differences hold across question types; SemEval 2013 protocol already partitions this | MEDIUM | Report IVR, SSR, ASR per question, per domain, and aggregate; not just aggregate |
| Seed-based reproducibility | Required for academic rigor; NLP reproducibility standards require it (EMNLP 2020 reproducibility checklist) | LOW | Fix random seeds for model init, data shuffling, LLM temperature=0; log all seeds |
| Experiment configuration logging | Reviewers may ask to reproduce specific runs; LLM API reproducibility is hard without logging | LOW | Log hyperparameters, prompts, model IDs, library versions to files per run |
| Result tables for paper | The paper needs LaTeX-ready tables showing IVR/SSR/ASR per model, per perturbation family, per question set | LOW | Auto-generate from stored results; pandas to LaTeX |
| Statistical significance testing | Any claims about model A > model B require significance testing; Wilcoxon or McNemar depending on metric type | MEDIUM | Wilcoxon signed-rank for continuous metrics (e.g., score delta); McNemar for binary flip rates |

---

### Differentiators (Competitive Advantage for the Paper)

Features that set this paper's contribution apart. Not universally expected, but make the paper stronger and more publishable.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Hybrid grading model (handcrafted linguistic features + embeddings) | Adds a third grading model type between pure supervised and pure LLM; allows comparison across three model families in one framework | HIGH | Combine SBERT cosine similarity, lexical overlap, negation flags, length ratio with learned layer; shows the hybrid is more or less robust |
| Hybrid perturbation generation (rule-based + LLM-assisted) | Rules give determinism for low-level perturbations; LLMs generate realistic semantic paraphrases that rule-based cannot; documented in PROJECT.md as a key decision | MEDIUM | Use GPT-4o or similar for paraphrase generation with fixed seed; store outputs; do not regenerate on each run |
| Per-perturbation-type metric decomposition | Most papers only report aggregate robustness; breaking IVR/SSR/ASR by perturbation type reveals which linguistic phenomena each model struggles with | MEDIUM | Add perturbation_type field to results schema; groupby analysis at reporting time |
| Radar/spider chart visualization per model | Standard in robustness evaluation papers (e.g., GREAT Score NeurIPS 2024); gives reviewers at-a-glance multi-dimensional comparison | LOW | One radar per model showing IVR/SSR/ASR across perturbation families; matplotlib or seaborn |
| Ranking stability analysis (Kendall's tau) | Borrowed from leaderboard evaluation literature (arXiv 2602.17316); shows whether perturbations change model ranking — powerful evidence that traditional metrics mislead | LOW | Compute Kendall's tau between model rankings on clean vs. perturbed inputs; tau < 0.8 = strong evidence of instability |
| Trust curve / uncertainty-accuracy tradeoff for LLM graders | Rubric-Conditioned LLM Grading (2601.08843) introduces this; filtering low-confidence LLM predictions to improve accuracy demonstrates calibration awareness | MEDIUM | Requires LLM to output confidence scores or run consensus across multiple temperatures; adds depth to LLM analysis |
| Stored perturbation outputs (reusable artifact) | Generates a dataset of perturbed student answers that other researchers can use; elevates paper from methodology-only to resource contribution | LOW | Store all perturbations with metadata (type, original answer, question ID, semantic similarity score) as JSON/CSV |
| Custom dataset ingestion interface | Allows paper to report results on both public (SRA/SemEval) and custom (LUISS student responses) datasets in same framework | MEDIUM | Pluggable dataset loader; validate schema at load time; document format clearly |
| Perturbation quality human validation sample | A small human validation study (~50-100 perturbations rated for quality) strengthens the claim that perturbations are realistic | HIGH (effort, not code) | Manual annotation step; requires co-author time; can be deferred if deadline is tight |

---

### Anti-Features (Deliberately NOT Building These)

Features to explicitly exclude to protect scope, timeline, and paper focus.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| Real-time / production grading system | Out of scope per PROJECT.md; adds deployment complexity (API, auth, latency) that doesn't serve the research question | Report offline batch evaluation results; make code available for researchers to run locally |
| Web interface or dashboard | Zero academic value; adds significant frontend complexity; reviewers don't evaluate dashboards | Generate static PDF/PNG visualizations and LaTeX tables; all output is paper-ready files |
| Grading model optimization / SOTA pursuit | The thesis is about evaluation methodology, not benchmark-beating; pursuing SOTA accuracy distracts from robustness analysis | Use standard well-documented baselines; report accuracy only as context for robustness discussion |
| Multi-language support | English only for IFKAD 2026 per PROJECT.md; multilingual adds dataset complexity without strengthening the core argument | Note as future work in the paper |
| Neural perturbation generation (adversarial suffix optimization) | GradingAttack-style token-level optimization (e.g., 500 iterations gradient descent) is compute-intensive and hard to interpret; the paper needs human-readable perturbations | Use rule-based and LLM-prompted perturbations that produce readable, explainable text changes |
| Fully automated adversarial training / defense | Defense evaluation is a separate research question; including it doubles scope without clear contribution | Mention as future work; analysis of vulnerability is the contribution, not the fix |
| Character-level noise perturbations (typos, OCR errors) | Tests surface-level spelling robustness, not grading semantics; orthogonal to the paper's argument about meaning preservation | Include only if a gaming perturbation (intentional typo to avoid detection); do not include as an invariance test |
| New grading dataset construction | Requires IRB, student consent pipeline, and annotation; the custom LUISS dataset is incoming from professor and should be plug-in | Build pluggable dataset loader; wait for professor's dataset rather than constructing a new one |
| Per-student longitudinal analysis | Requires tracking individual students across responses; not needed for evaluating grading model behavior | Treat responses as independent instances; no student-level tracking |
| LLM fine-tuning for grading | Fine-tuned LLM grading is expensive, slow, and blurs the line between "grading model" and the perturbation evaluation framework | Use LLMs in zero-shot / few-shot rubric-conditioned mode only |

---

## Feature Dependencies

```
[Perturbation Engine: Invariance Family]
    └──required by──> [IVR Computation]
                          └──required by──> [Within-question / Cross-question Breakdown]
                                                └──required by──> [Statistical Significance Testing]
                                                └──required by──> [Result Tables]

[Perturbation Engine: Sensitivity Family]
    └──required by──> [SSR Computation]
                          └──required by──> [Within-question / Cross-question Breakdown]

[Perturbation Engine: Gaming Family]
    └──required by──> [ASR Computation]
                          └──required by──> [Within-question / Cross-question Breakdown]

[Semantic Preservation Check]
    └──gates──> [Perturbation Engine: Invariance Family] (filter bad perturbations before use)

[SRA / SemEval 2013 Dataset Support]
    └──required by──> [LOQO Cross-validation]
    └──required by──> [Supervised Transformer Grading Model] (training data)
    └──required by──> [Within-question / Cross-question Breakdown] (Q and D splits)

[Supervised Transformer Grading Model]
    └──required by──> [IVR, SSR, ASR Computation] (one of the graders being evaluated)
    └──requires──> [LOQO Cross-validation] (proper evaluation)

[LLM-Based Rubric-Driven Grading Model]
    └──required by──> [IVR, SSR, ASR Computation] (second grader type)
    └──enhances──> [Trust Curve / Uncertainty Analysis] (requires confidence output)

[Hybrid Grading Model]
    └──required by──> [IVR, SSR, ASR Computation] (third grader type)
    └──requires──> [Supervised Transformer Grading Model] (builds on embeddings)

[Stored Perturbation Outputs]
    └──enables──> [Custom Dataset Ingestion Interface] (same schema)
    └──enables──> [Perturbation Quality Human Validation] (sample from stored outputs)

[Ranking Stability Analysis]
    └──requires──> [IVR, SSR, ASR Computation] (needs metric values per model)

[Seed-based Reproducibility]
    └──required by──> [Experiment Configuration Logging] (seeds must be logged to be useful)

[Result Tables]
    └──enhances──> [Statistical Significance Testing] (tables include p-values)
    └──enhances──> [Radar/Spider Chart Visualization] (visual complement to tables)
```

### Dependency Notes

- **IVR, SSR, ASR all require perturbation engine first:** Do not design metrics before the perturbation schema is fixed — the metric definitions depend on knowing which perturbations change the label and which do not.
- **LOQO requires the full dataset to be loaded:** The cross-validation scheme wraps the entire experiment loop; build it into the runner from day one, not as an afterthought.
- **Semantic preservation check gates invariance perturbations:** A perturbation classified as "invariance" that actually changes meaning will corrupt IVR; the filter must run before results are recorded.
- **Hybrid model requires the transformer model:** The hybrid uses transformer embeddings as one of its components; the transformer training pipeline must be complete first.
- **Stored perturbation outputs enable the custom dataset path:** Using the same storage schema for both SRA perturbations and future LUISS perturbations avoids a rewrite when the custom dataset arrives.

---

## MVP Definition

### Launch With (v1) — Required for IFKAD 2026 Submission

Minimum viable framework that produces credible, publishable results.

- [ ] Perturbation engine: invariance family (synonym substitution, paraphrase via LLM, negation = sensitivity, so this covers 2 families at minimum) — required to compute IVR and SSR
- [ ] Perturbation engine: gaming family (adjective/adverb stuffing, trigger phrase insertion) — required to compute ASR
- [ ] Semantic preservation check via SBERT similarity — required to validate invariance perturbations
- [ ] Supervised transformer grading model (BERT fine-tuned, LOQO) — baseline; every ASAG paper has this
- [ ] LLM-based rubric-driven grading model (GPT-4o zero-shot + one open-source) — modern comparison; makes the multi-grader comparison credible
- [ ] IVR, SSR, ASR metric computation — the paper's core metrics
- [ ] SRA / SemEval 2013 dataset support — standard benchmark; makes results comparable to prior work
- [ ] LOQO cross-validation — cross-question generalization; non-negotiable per Heilman & Madnani 2015
- [ ] Within-question and cross-question breakdown — required by the paper's argument about question-level heterogeneity
- [ ] Seed-based reproducibility + experiment config logging — academic rigor minimum
- [ ] Statistical significance testing (Wilcoxon) — required to claim A > B
- [ ] Result tables (LaTeX export) — paper-ready output

### Add After Core Validation (v1.x) — Before Final Submission

Features to add once the core experiment pipeline is running and producing sensible numbers.

- [ ] Hybrid grading model — adds a third model family; strengthens the multi-grader comparison
- [ ] Per-perturbation-type metric decomposition — adds analytical depth to the results section
- [ ] Ranking stability analysis (Kendall's tau) — strong supporting evidence for the paper's central claim
- [ ] Radar/spider chart visualization — makes figures section stronger
- [ ] Stored perturbation outputs (artifact release) — add metadata and export; low cost once results are stored
- [ ] Custom dataset ingestion interface — needed when LUISS student responses arrive; build schema now, activate when data available

### Future Consideration (v2+ / post-IFKAD) — Explicit Deferrals

- [ ] Trust curve / uncertainty analysis for LLM graders — interesting but adds experiment complexity; defer to journal extension
- [ ] Perturbation quality human validation study — requires co-author annotation time; flag as "future work" in paper
- [ ] Additional LLMs (Llama 3, Gemini) — more LLMs strengthens the multi-rater comparison but adds API costs; add if budget permits after core is working

---

## Feature Prioritization Matrix

| Feature | Academic Value | Implementation Cost | Priority |
|---------|---------------|---------------------|----------|
| Perturbation engine (all 3 families) | HIGH | MEDIUM | P1 |
| Semantic preservation check (SBERT) | HIGH | LOW | P1 |
| IVR / SSR / ASR metrics | HIGH | LOW | P1 |
| Supervised transformer grader (BERT + LOQO) | HIGH | HIGH | P1 |
| LLM rubric-driven grader | HIGH | MEDIUM | P1 |
| SRA / SemEval 2013 dataset support | HIGH | MEDIUM | P1 |
| Within/cross-question breakdown | HIGH | LOW | P1 |
| Seed reproducibility + config logging | HIGH | LOW | P1 |
| Statistical significance testing | HIGH | LOW | P1 |
| Result tables (LaTeX) | HIGH | LOW | P1 |
| Hybrid grading model | MEDIUM | HIGH | P2 |
| Per-perturbation-type decomposition | MEDIUM | LOW | P2 |
| Ranking stability (Kendall's tau) | MEDIUM | LOW | P2 |
| Radar chart visualization | MEDIUM | LOW | P2 |
| Stored perturbation artifact | MEDIUM | LOW | P2 |
| Custom dataset ingestion | MEDIUM | MEDIUM | P2 |
| Trust curve / uncertainty analysis | LOW | MEDIUM | P3 |
| Human validation study | MEDIUM | HIGH (effort) | P3 |
| Additional LLMs (Llama 3, etc.) | LOW | LOW (API calls) | P3 |

**Priority key:**
- P1: Must have for IFKAD 2026 paper submission
- P2: Should have; add during active development phase
- P3: Nice to have; defer to post-submission or journal extension

---

## Prior Work Feature Analysis

Papers surveyed to determine what is established practice vs. novel in this framework.

| Feature | Filighera 2024 (IJAIED) | Ding 2020 (PMC) / Fooling ASAG | GradingAttack 2025 (arXiv 2602) | Rubric-LLM 2025 (arXiv 2601) | ASAG2024 Benchmark | **This Paper** |
|---------|------------------------|-------------------------------|--------------------------------|------------------------------|-------------------|----------------|
| Invariance perturbations | Partial (adjective stuffing) | Universal triggers (not invariance) | Prompt-level attacks | Synonym substitution, paraphrase | None | Full family |
| Sensitivity perturbations | None | None | None | None | None | Novel contribution |
| Gaming perturbations | Yes (adjective/adverb) | Yes (universal triggers) | Yes (token suffix, prompt injection) | Adversarial naive inputs | None | Extends all 3 |
| IVR metric | No | No | No | No | No | Novel |
| SSR metric | No | No | No | No | No | Novel |
| ASR metric | Implicit (accuracy drop) | Implicit (flip count) | Yes (CAS extends ASR) | Implicit | No | Formalizes |
| Multi-model comparison | No (BERT and T5 only) | No | 7 LLMs | 1 LLM | Multiple | 3 model families |
| LOQO cross-validation | No | No | No | No | Partial (cross-dataset) | Yes |
| Statistical significance | No | No | No | No | No | Yes |
| Stored perturbation artifact | No | No | No | No | No | Yes |

**Implication:** IVR and SSR are genuinely novel metric formalizations. The full three-family perturbation framework evaluated across multiple model families with LOQO and statistical testing is not present in any single prior paper. The paper's contribution is real and defensible.

---

## Sources

- Filighera et al. (2024). "Cheating Automatic Short Answer Grading with the Adversarial Usage of Adjectives and Adverbs." *International Journal of Artificial Intelligence in Education*, 34(2). [ERIC EJ1426308](https://eric.ed.gov/?q=automatic&ff1=dtySince_2024&id=EJ1426308) — MEDIUM confidence (abstract only)
- Ding et al. (2020). "Fooling Automatic Short Answer Grading Systems." PMC. [PMC7334174](https://pmc.ncbi.nlm.nih.gov/articles/PMC7334174/) — HIGH confidence (full paper fetched)
- GradingAttack (2025). "Attacking Large Language Models Towards Short Answer Grading Ability." arXiv 2602.00979. [arXiv](https://arxiv.org/html/2602.00979) — HIGH confidence (full paper fetched)
- Rubric-Conditioned LLM Grading (2025). arXiv 2601.08843. [arXiv](https://arxiv.org/html/2601.08843) — HIGH confidence (full paper fetched)
- Auditing ASAG with RL (2024). EDM 2024. [arXiv 2405.07087](https://arxiv.org/html/2405.07087v1) — HIGH confidence (full paper fetched)
- Ribeiro et al. (2020). "Beyond Accuracy: Behavioral Testing of NLP Models with CheckList." ACL 2020 Best Paper. [ACL Anthology](https://aclanthology.org/2020.acl-main.442.pdf) — HIGH confidence (framework verified)
- Heilman & Madnani (2015). "The Impact of Training Data on Automated Short Answer Scoring Performance." BEA 2015. [ACL Anthology](https://aclanthology.org/W15-0610/) — MEDIUM confidence (abstract/metadata only; LOQO methodology attributed via citation in PROJECT.md)
- ASAG2024 Benchmark (2024). arXiv 2409.18596. [arXiv](https://arxiv.org/abs/2409.18596) — MEDIUM confidence (abstract + partial PDF)
- Same Meaning, Different Scores (2026). arXiv 2602.17316. [arXiv](https://arxiv.org/html/2602.17316) — HIGH confidence (full paper fetched; Kendall's tau for ranking stability)
- Tramer et al. (2020). "Fundamental Tradeoffs between Invariance and Sensitivity to Adversarial Perturbations." ICML 2020. [arXiv 2002.04599](https://arxiv.org/abs/2002.04599) — MEDIUM confidence (abstract; theoretical basis for invariance/sensitivity distinction)
- SemEval 2013 Task 7 (SRA). [ACL Anthology S13-2045](http://www.aclweb.org/anthology/S13-2045) — HIGH confidence (standard benchmark, well-established)

---

*Feature research for: Perturbation-based ASAG evaluation framework*
*Researched: 2026-02-20*
