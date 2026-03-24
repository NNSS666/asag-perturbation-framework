# Project Research Summary

**Project:** Perturbation-based ASAG Evaluation Framework (IFKAD 2026)
**Domain:** Academic NLP research tool — automated short answer grading robustness evaluation
**Researched:** 2026-02-20
**Confidence:** MEDIUM-HIGH

## Executive Summary

This project builds a research evaluation framework that systematically tests the robustness of Automatic Short Answer Grading (ASAG) models using three families of text perturbations: invariance-preserving changes (which should not alter the grade), sensitivity-revealing changes (which should alter the grade), and gaming/adversarial attacks (which test whether incorrect answers can be disguised as correct ones). The framework introduces two genuinely novel metrics — Invariance Violation Rate (IVR) and Sensitivity Success Rate (SSR) — alongside the established Attack Success Rate (ASR), and evaluates three model families (supervised transformer, hybrid linguistic, LLM rubric-driven) across these metrics using leave-one-question-out (LOQO) cross-validation on the SRA/SemEval 2013 benchmark. Prior work confirms that no single paper covers all three perturbation families, all three model families, LOQO, and statistical significance testing simultaneously, making this a defensible and novel contribution.

The recommended technical approach is a staged pipeline built on Python 3.11, PyTorch 2.10, HuggingFace Transformers 5.x/sentence-transformers, and litellm for multi-LLM routing. The architecture must be designed as a series of independently re-runnable stages — data ingestion, perturbation generation (cached), grading, metric computation, and reporting — because mixing these stages is the single most common cause of irreproducible results and wasted compute budgets. DeBERTa-v3-base is the recommended primary supervised grader; ModernBERT-base is a strong alternative worth including for comparison. LLM grading should route through litellm with all prompts and responses logged to JSONL for academic reproducibility.

The critical risks are methodological, not technical: data leakage in the LOQO implementation (preprocessing must happen inside each fold), LLM output non-determinism (even temperature=0 is not fully deterministic; report variance across 3 runs), API cost explosions from the combinatorial evaluation space (perturbations × answers × questions × folds × models), and perturbation quality validity (LLM-generated paraphrases must not read as obviously synthetic). All of these risks have clear mitigation strategies documented in the research and must be addressed in the earliest build phases before any results are generated.

---

## Key Findings

### Recommended Stack

The stack is Python 3.11 (the only version satisfying all library constraints simultaneously), with PyTorch 2.10 as the non-negotiable deep learning backbone per project constraints. HuggingFace's ecosystem (transformers 5.2.0, sentence-transformers 5.2.3, datasets 4.5.0) covers all model loading and fine-tuning needs. litellm 1.81.13 provides a unified API layer for GPT-4o, Claude Sonnet, and Gemini without maintaining three separate SDK integrations, while still requiring the underlying SDKs (openai, anthropic, google-genai). Statistical analysis relies on scipy 1.17.0 + pingouin 0.5.5 for effect sizes and scikit-learn 1.8.0 for QWK. Rule-based perturbation generation uses spaCy 3.8.x + NLTK 3.9. Hydra 1.3.2 (stable) manages experiment configuration. Full version details in `STACK.md`.

**Core technologies:**
- **Python 3.11.x**: Runtime — only version satisfying torch, transformers, scikit-learn 1.8.0, and pandas 3.x simultaneously
- **PyTorch 2.10.0**: Deep learning backbone — project constraint; non-negotiable; native GPU support
- **HuggingFace transformers 5.2.0**: Model loading and fine-tuning — canonical access to DeBERTa, ModernBERT; full Trainer API
- **sentence-transformers 5.2.3**: Semantic similarity — required for SBERT cosine similarity in hybrid grader and perturbation validity checks
- **litellm 1.81.13**: Multi-LLM routing — unified interface for GPT-4o/Claude/Gemini; avoids 3 separate integrations; built-in cost tracking
- **DeBERTa-v3-base**: Primary supervised grader — best accuracy/compute tradeoff for ASAG classification per Timoneda et al. 2025
- **ModernBERT-base**: Alternative supervised grader — Dec 2024 release, 4x faster on mixed lengths, 8192 context; strong second candidate
- **scipy 1.17.0 + pingouin 0.5.5**: Statistical testing — Wilcoxon signed-rank, effect sizes, confidence intervals for metric comparisons
- **spaCy 3.8.x + NLTK 3.9**: Rule-based perturbation — POS tagging for adjective/adverb insertion; WordNet for synonym substitution
- **hydra-core 1.3.2**: Config management — per-experiment YAML overrides; seed/model/perturbation family configs without touching code

**What NOT to use:** google-generativeai (EOL Nov 2025), nlpaug (dependency conflicts with transformers 5.x), langchain (heavyweight overhead), hydra-core 1.4.0.dev1 (pre-release), TensorFlow (project constraint specifies PyTorch).

### Expected Features

Research confirms IVR and SSR are genuinely novel metric formalizations. No prior paper combines all three perturbation families + all three model families + LOQO + statistical testing. The paper's contribution is real and defensible. Full feature analysis in `FEATURES.md`.

**Must have for IFKAD 2026 submission (P1):**
- Perturbation engine: all three families (invariance, sensitivity, gaming) — prerequisite for IVR, SSR, ASR computation
- Semantic preservation check via SBERT cosine similarity (threshold >= 0.85) — gates invariance perturbations
- IVR, SSR, ASR metric computation — the paper's core novel contribution
- Supervised transformer grader (DeBERTa/ModernBERT fine-tuned) with LOQO cross-validation
- LLM rubric-driven grader (GPT-4o zero-shot + one open-source LLM)
- SRA / SemEval 2013 dataset support — standard benchmark required for comparison to prior work
- Within-question and cross-question metric breakdowns (Q and D splits per SemEval protocol)
- Seed-based reproducibility and experiment configuration logging
- Statistical significance testing (Wilcoxon signed-rank; Bonferroni correction for multi-model comparisons)
- Result tables with LaTeX export

**Should have before final submission (P2):**
- Hybrid grading model (SBERT features + XGBoost/LR head) — third model family strengthens multi-grader comparison
- Per-perturbation-type metric decomposition — reveals which linguistic phenomena each model struggles with
- Ranking stability analysis (Kendall's tau) — powerful evidence that traditional metrics mislead
- Radar/spider chart visualization — multi-dimensional model comparison figures
- Stored perturbation outputs as reusable artifact
- Custom dataset ingestion interface (for professor's LUISS dataset when available)

**Defer to post-IFKAD (P3):**
- Trust curve / uncertainty analysis for LLM graders
- Perturbation quality human validation study
- Additional LLMs (Llama 3, Gemini)
- Multi-language support (future work in paper)

**Explicit anti-features:** No real-time system, no web interface, no SOTA accuracy pursuit, no LLM fine-tuning, no per-student longitudinal tracking.

### Architecture Approach

The framework is a five-subsystem pipeline where data flows unidirectionally through: Orchestration (Hydra config + seed manager) → Data Pipeline (loader, preprocessor, LOQO splitter) → Perturbation Engine (registry + three families, outputs cached to JSONL) → Grading Models (three types behind a common GraderInterface) → Evaluation Engine (IVR/SSR/ASR calculators + LOQO coordinator) → Reporting Layer (tables, figures, statistics). Each stage materializes its outputs to disk — the pipeline is NOT a single in-memory script. This design choice is fundamental: it enables independent re-runs, crash recovery, and cost control for LLM API calls. Full architecture with code examples in `ARCHITECTURE.md`.

**Major components:**
1. **DatasetLoader + Preprocessor + DataSplitter** — loads SRA/SemEval XML to canonical AnswerRecord schema; generates LOQO fold definitions; everything downstream depends on this being correct
2. **PerturbationRegistry + three perturbation families** — central registry maps names to perturbation functions tagged by family; rule-based first (deterministic, no cost), LLM-assisted second (cached after first run)
3. **GraderInterface + TransformerGrader / HybridGrader / LLMGrader** — abstract base class enforces `grade(question, reference, answer) -> float`; evaluation engine is model-agnostic
4. **EvaluationEngine (PerturbationRunner + IVR/SSR/ASR calculators + LOQOValidator)** — pure computation; no I/O except reading cache and writing results parquet; LOQO is the outer loop
5. **ReportingLayer (TableGenerator + FigureGenerator + StatisticsRunner)** — reads only from result store; independently re-runnable without re-grading

**Key patterns:** Registry pattern for perturbations (config-driven ablations), GraderInterface ABC (evaluation is model-agnostic), cache-first perturbation generation (reproducibility + cost control), LOQO as the outermost experiment loop (not bolted on afterward).

**Suggested build order:** Schema + DatasetLoader → Preprocessor + LOQO splitter → GraderInterface + HybridGrader (fastest to implement, validates the pipeline) → Metrics (IVR/SSR/ASR) → Rule-based perturbations → End-to-end integration → TransformerGrader (GPU) → LLMGrader + LLM perturbations → Reporting → Custom dataset adapter.

### Critical Pitfalls

Seven critical pitfalls that cause fundamental methodological invalidity if not addressed. Full details in `PITFALLS.md`.

1. **LOQO data leakage via shared preprocessing** — sklearn pipelines fitted on the full dataset before the LOQO loop are a silent invalidator; mitigation: build the LOQO loop first, fit all preprocessing inside each fold; write a leakage diagnostic test that asserts the held-out question's text never appears in training-phase fitted objects
2. **LLM non-determinism invalidating single-run metric reports** — temperature=0 does not guarantee reproducibility; GPU floating-point reduction order is non-deterministic; mitigation: run LLM evaluation 3 times, report mean ± std for IVR/SSR/ASR; log all prompts and completions per run
3. **Unrealistic perturbations testing artifacts rather than behavior** — LLM-generated paraphrases default to polished, fluent text that no student writes; mitigation: analyze SRA corpus for real student error patterns before generating perturbations; human spot-check n >= 30 per perturbation type; base gaming attacks on documented strategies from Filighera 2024 and GradingAttack 2025
4. **API cost overruns halting mid-experiment** — the call count formula (answers × perturbations × questions × folds × LLMs × runs) easily exceeds 100K calls for full SemEval; mitigation: implement dry-run cost estimation before any full execution; use OpenAI Batch API (50% discount); cache by (prompt_hash, model_id)
5. **Invalid statistical comparisons between models** — eyeballing metric table differences without significance testing; mitigation: use paired bootstrap resampling (1000 iterations) for IVR/SSR; Bonferroni correction for 9 comparisons (3 models × 3 metrics); report effect sizes alongside p-values via pingouin
6. **LLM prompt sensitivity contaminating comparative claims** — informally tuned prompts bake in prompt-LLM interaction effects; mitigation: lock the prompt template structure before any comparative evaluation begins; validate with 3 prompt variants on a held-out question
7. **Grade imbalance masking metric quality** — SemEval is majority "correct"; a grader that never flips "correct" answers achieves high IVR trivially; mitigation: compute IVR/SSR/ASR per grade tier (correct/partial/incorrect) and report stratified breakdown alongside aggregate

---

## Implications for Roadmap

Research strongly implies a bottom-up, dependency-driven build order with six phases. Phases 1-3 establish the methodological skeleton before any GPU training or LLM API spending occurs.

### Phase 1: Foundation — Schema, Data, and LOQO

**Rationale:** Everything depends on having correct data in the canonical schema and a correct LOQO implementation. Building this first prevents the most expensive failure mode (discovering LOQO leakage after all experiments are run). The canonical AnswerRecord schema is the contract that makes all downstream components dataset-agnostic.

**Delivers:** DatasetLoader (SRA + SemEval 2013), Preprocessor, canonical AnswerRecord/PerturbedAnswerRecord/GradingResult dataclasses, DataSplitter with LOQO fold generator, leakage diagnostic test, Hydra config skeleton, seed manager.

**Addresses features:** SRA/SemEval dataset support, LOQO cross-validation, seed-based reproducibility, experiment config logging.

**Avoids pitfalls:** LOQO data leakage (Pitfall 2), custom dataset schema brittleness (Pitfall 13).

**Research flag:** Standard patterns — no additional research needed for this phase.

---

### Phase 2: Metrics and Hybrid Grader Baseline

**Rationale:** Build and unit-test the IVR/SSR/ASR metric calculators on dummy grading results with hand-computed expected values before any real grader exists. The HybridGrader is the fastest grader to implement (no GPU, no API) and validates the full evaluation machinery end-to-end at low cost. The evaluation runner and ResultAggregator also belong here.

**Delivers:** IVR/SSR/ASR calculators with unit tests pinning expected values, LOQOValidator coordinator, ResultAggregator (parquet result store), GraderInterface ABC, HybridGrader (SBERT cosine similarity + spaCy features + sklearn head), PerturbationRunner stub (using dummy perturbations), baselines (random grader + majority-class grader).

**Addresses features:** IVR/SSR/ASR metric computation, within/cross-question breakdown, hybrid grading model (P2 brought forward to validate pipeline), baseline graders.

**Avoids pitfalls:** Insufficient baselines (Pitfall 8), grade imbalance in metrics (Pitfall 10), LOQO metrics per-fold not full-dataset (Pitfall 4/anti-pattern).

**Research flag:** Standard patterns — metric math is well-specified; no additional research needed.

---

### Phase 3: Perturbation Engine

**Rationale:** Rule-based perturbations are deterministic, have zero API cost, and must be built and quality-checked before LLM-assisted perturbations are added. The PerturbationRegistry must be established here so later LLM perturbations simply register new functions. The semantic preservation check (SBERT filter) must be wired in before any invariance perturbations are used in evaluation.

**Delivers:** PerturbationRegistry, BasePerturbation ABC, all rule-based invariance perturbations (synonym swap, casing, contraction, whitespace), all sensitivity perturbations (word deletion, negation insertion, concept swap, partial answer), all gaming perturbations (keyword stuffing, trigger injection, answer elongation), semantic preservation check (SBERT cosine >= 0.85 filter), perturbation cache (JSONL), generate_perturbations.py script, human spot-check sample of n >= 30 per perturbation type.

**Addresses features:** Perturbation engine (all three families), semantic preservation check, stored perturbation outputs artifact, per-perturbation-type metric decomposition.

**Avoids pitfalls:** Unrealistic perturbations (Pitfall 1), non-deterministic perturbation on every run (Architecture anti-pattern 3).

**Research flag:** Needs research-phase attention — the exact operationalization of gaming perturbations should reference Filighera 2024 and GradingAttack 2025 attack taxonomies specifically. LLM-assisted paraphrase quality criteria need validation before production use.

---

### Phase 4: Supervised Transformer Grader + End-to-End Integration

**Rationale:** The TransformerGrader is the most computationally expensive component (N LOQO fine-tuning runs). It must be built after the pipeline is validated (Phase 2-3) so GPU compute is not wasted on a broken pipeline. This phase also connects all components into the first complete end-to-end run.

**Delivers:** TransformerGrader (DeBERTa-v3-base + ModernBERT-base fine-tuning with transformers.Trainer), LOQO fine-tuning loop (train on all-but-one question, evaluate on held-out), end-to-end integration test on SRA Beetle subset (~200 answers), multi-seed runs (3 seeds) for variance reporting.

**Addresses features:** Supervised transformer grading model, LOQO cross-validation (fully exercised), seed variance reporting.

**Avoids pitfalls:** Grader overfitting to question-specific surface features (Pitfall 5), single seed masking variance (Pitfall 12).

**Research flag:** Standard patterns — HuggingFace Trainer API for classification is well-documented. LOQO as manual fold loop (Trainer does not natively support LOQO) is confirmed in stack research.

---

### Phase 5: LLM Grader + LLM-Assisted Perturbations + Cost Controls

**Rationale:** LLM components are last because they are expensive, rate-limited, and non-deterministic. All infrastructure (caching, cost estimation, logging, batch API support) must be in place before any full LLM evaluation run. Prompt templates must be locked before any comparative evaluation begins.

**Delivers:** LLMGrader (GPT-4o zero-shot + few-shot + one open-source LLM via litellm), prompt template (locked before comparative runs), LLM-assisted paraphrase perturbations and back-translation (cached), JSONL logging for all LLM calls, dry-run cost estimator, OpenAI Batch API support, 3-run LLM stability analysis (mean ± std for IVR/SSR/ASR), prompt sensitivity validation (3 variants on held-out question).

**Addresses features:** LLM rubric-driven grading model, LLM-assisted perturbation generation (hybrid rule + LLM approach), experiment config logging (LLM-specific).

**Avoids pitfalls:** LLM non-determinism (Pitfall 3), LLM prompt sensitivity (Pitfall 6), API cost overruns (Pitfall 7), LLM hallucination in rubric grading (Pitfall 14), position/verbosity bias (Pitfall 11).

**Research flag:** Needs research-phase attention — optimal prompt structure for rubric-conditioned grading, OpenAI Batch API integration details, and litellm seed parameter support per provider all warrant verification before implementation.

---

### Phase 6: Reporting, Statistics, and Paper Outputs

**Rationale:** Reporting is entirely downstream from stable results. Running it last ensures statistical tests operate on final, validated result data and paper tables reflect the complete experiment.

**Delivers:** Statistical significance testing (paired bootstrap + Bonferroni correction for 9 comparisons), per-tier grade breakdown for IVR/SSR/ASR, LaTeX result tables (per model, per perturbation family, per question set), ranking stability analysis (Kendall's tau between clean and perturbed model rankings), radar charts per model, per-question heatmaps, ReportCompiler assembling output directory, "Looks Done But Isn't" checklist verification.

**Addresses features:** Statistical significance testing, result tables (LaTeX), ranking stability analysis (Kendall's tau), radar/spider chart visualization, within-question and cross-question breakdown.

**Avoids pitfalls:** Invalid statistical comparisons (Pitfall 4), selective perturbation family reporting / cherry-picking (Pitfall 9), insufficient baselines (Pitfall 8 — baseline rows appear in all tables).

**Research flag:** Standard patterns — scipy/pingouin APIs are well-documented. Paired bootstrap implementation is straightforward. No additional research needed.

---

### Phase Ordering Rationale

- **Bottom-up dependency order:** Every phase consumes outputs of the previous. Metrics cannot be computed without graders; graders cannot be evaluated without perturbations; perturbations cannot be validated without the schema and dataset.
- **Cheapest-first compute strategy:** Phases 1-3 use no GPU and no LLM API budget, validating the pipeline for free. Phase 4 introduces GPU cost only after the pipeline is proven. Phase 5 introduces LLM API cost only after cost controls are built.
- **LOQO as the organizing principle:** The LOQO loop is established in Phase 1 (fold definitions) and exercised in Phase 2 (metric calculation), meaning it is validated before the expensive Phase 4 transformer training runs inside it.
- **Pitfall front-loading:** The three most expensive pitfalls to recover from — LOQO leakage, unrealistic perturbations, and API cost overruns — are all addressed in Phases 1-3.

### Research Flags

**Phases needing deeper research during planning:**
- **Phase 3 (Perturbation Engine):** Gaming perturbation taxonomy should be validated against Filighera 2024 and GradingAttack 2025 attack catalogs; LLM paraphrase quality criteria need operationalization for the human spot-check protocol
- **Phase 5 (LLM Grader):** Optimal prompt structure for rubric-conditioned grading (position of rubric vs. reference answer, grade scale format) should be researched before locking the template; OpenAI Batch API integration and litellm seed parameter behavior per provider need verification

**Phases with standard, well-documented patterns (skip research-phase):**
- **Phase 1 (Foundation):** HuggingFace datasets library for SemEval/SRA loading is well-documented; Hydra config patterns are stable
- **Phase 2 (Metrics + Hybrid Grader):** IVR/SSR/ASR math is specified in the project; SBERT cosine similarity via sentence-transformers is trivial; sklearn pipeline patterns are standard
- **Phase 4 (Transformer Grader):** HuggingFace Trainer API for sequence classification is canonical; DeBERTa fine-tuning is well-documented
- **Phase 6 (Reporting):** scipy/pingouin statistics APIs are stable and well-documented; matplotlib/seaborn figure generation is standard

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All package versions verified from PyPI as of 2026-02-20; Python 3.11 constraint is hard (scikit-learn 1.8.0 + pandas 3.x both require it); one MEDIUM: DeBERTa vs. ModernBERT choice depends on benchmark still evolving |
| Features | MEDIUM-HIGH | P1 features grounded in published ASAG literature and standard benchmark protocols; IVR/SSR are novel and their operationalization has no external validation; paper contribution defensibility is HIGH based on prior work comparison table |
| Architecture | HIGH | Five-subsystem pipeline pattern is validated by CheckList (Ribeiro 2020), GradingAttack 2025, and hybrid ASAG literature; LOQO outer loop is Heilman & Madnani 2015 gold standard; cache-first perturbation is best practice for reproducible ML |
| Pitfalls | MEDIUM-HIGH | Critical pitfalls are grounded in cited empirical research (LLM non-determinism: arxiv 2408.04667; grade imbalance: ASAG2024; LOQO leakage: arxiv 2311.04179); IVR/SSR-specific pitfalls are inferred from general robustness evaluation literature, not ASAG-specific prior work |

**Overall confidence:** MEDIUM-HIGH

### Gaps to Address

- **IVR/SSR operationalization thresholds:** The score-change threshold for IVR ("grade does not change" — but by how much?) needs explicit definition. Treat grading as binary (correct/incorrect/partial) or continuous? The answer affects metric sensitivity. Define this in Phase 2 before any results are generated.
- **DeBERTa vs. ModernBERT for ASAG:** Research shows DeBERTa-v3 still leads on controlled classification benchmarks (Timoneda et al. 2025) but ModernBERT is newer and faster. Both should be included in Phase 4 as a comparison; do not drop ModernBERT without empirical testing on SRA data.
- **LUISS custom dataset format:** The professor's dataset schema is unknown. The Phase 1 canonical schema must be flexible enough to accommodate it. Do not hard-code assumptions about grade scale or question format.
- **Compute resources for LOQO transformer training:** SemEval 2013 SciEntsBank has ~10K answers across multiple questions. N LOQO fine-tuning runs on a full-size DeBERTa model requires GPU access. Clarify available GPU resources before Phase 4 to determine whether to use distilBERT for development runs.
- **LLM budget envelope:** The dry-run cost estimator in Phase 5 will reveal the actual call count. Until then, the budget for full evaluation is uncertain. Consider starting with the smaller SRA Beetle subset to validate costs before scaling to full SemEval.

---

## Sources

### Primary (HIGH confidence)
- [PyPI package registry](https://pypi.org) — all package versions verified: torch, transformers, sentence-transformers, datasets, litellm, openai, anthropic, google-genai, scipy, pingouin, scikit-learn, pandas, numpy, matplotlib, seaborn, hydra-core
- [HuggingFace Hub: ModernBERT-base](https://huggingface.co/answerdotai/ModernBERT-base) — architecture, download count, release date confirmed
- [GradingAttack 2025, arXiv 2602.00979](https://arxiv.org/html/2602.00979) — adversarial attack taxonomy and ASR metric; full paper fetched
- [Rubric-Conditioned LLM Grading, arXiv 2601.08843](https://arxiv.org/html/2601.08843) — LLM grader design patterns; full paper fetched
- [Same Meaning Different Scores, arXiv 2602.17316](https://arxiv.org/html/2602.17316) — Kendall's tau ranking stability; full paper fetched
- [Ding et al. 2020, PMC7334174](https://pmc.ncbi.nlm.nih.gov/articles/PMC7334174/) — gaming perturbation methodology; full paper fetched
- [SemEval 2013 Task 7, ACL Anthology S13-2045](http://www.aclweb.org/anthology/S13-2045) — canonical ASAG benchmark
- [LLM non-determinism, arXiv 2408.04667](https://arxiv.org/html/2408.04667v5) — temperature=0 instability; verified
- [Dror et al. 2018, ACL P18-1128](https://aclanthology.org/P18-1128/) — statistical significance testing in NLP; standard reference
- [ASAG2024 Benchmark, arXiv 2409.18596](https://arxiv.org/abs/2409.18596) — grade imbalance, weighted RMSE

### Secondary (MEDIUM confidence)
- [Filighera et al. 2024, ERIC EJ1426308](https://eric.ed.gov/?q=automatic&ff1=dtySince_2024&id=EJ1426308) — adversarial adjective/adverb perturbation methodology; abstract only
- [Heilman & Madnani 2015, ACL Anthology W15-0610](https://aclanthology.org/W15-0610/) — LOQO as gold standard for ASAG evaluation; abstract/metadata
- [Timoneda et al. 2025, ACL Anthology ijcnlp-long.164](https://aclanthology.org/2025.ijcnlp-long.164.pdf) — ModernBERT vs. DeBERTaV3 controlled comparison
- [Ribeiro et al. 2020 CheckList, ACL Anthology acl-main.442](https://aclanthology.org/2020.acl-main.442.pdf) — INV/DIR/MFT perturbation taxonomy; precedent for three-family design
- [Hybrid ASAG approach MDPI 2024](https://www.researchgate.net/publication/381911595_A_Hybrid_Approach_for_Automated_Short_Answer_Grading) — SBERT + XGBoost hybrid grader pattern
- [Data leakage in cross-validation, arXiv 2311.04179](https://arxiv.org/pdf/2311.04179) — LOQO leakage patterns

### Tertiary (LOW confidence)
- [LLM-as-Judge biases, arXiv 2410.02736](https://arxiv.org/html/2410.02736v1) — position and verbosity bias; inferred applicability to ASAG rubric grading
- [Tramer et al. 2020, arXiv 2002.04599](https://arxiv.org/abs/2002.04599) — theoretical basis for invariance/sensitivity distinction in adversarial ML; abstract only

---

*Research completed: 2026-02-20*
*Ready for roadmap: yes*
