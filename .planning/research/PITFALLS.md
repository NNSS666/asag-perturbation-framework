# Pitfalls Research

**Domain:** Perturbation-based ASAG evaluation framework (academic research)
**Researched:** 2026-02-20
**Confidence:** MEDIUM-HIGH (core pitfalls verified across multiple sources; specific metrics IVR/SSR/ASR are novel to this project and lack external verification)

---

## Critical Pitfalls

These mistakes cause fundamental methodological invalidity — the paper's claims fall apart.

---

### Pitfall 1: Unrealistic Perturbations That Don't Match Real Student Behavior

**What goes wrong:**
Perturbations are generated that no actual student would produce — e.g., grammatically correct but stylistically alien paraphrases, perfectly clean paraphrases with no disfluency, or semantically null additions that are obviously artificial to any reader. The perturbation set ends up testing the grader against synthetic noise rather than real behavioral patterns: keyword stuffing, copying question phrasing, partial answers, typical spelling errors, natural hedging language. The evaluation then measures resistance to an artifact of the generator, not robustness against student behavior.

**Why it happens:**
LLM-assisted perturbation generation defaults to fluent, polished text because that is what LLMs are trained to produce. Rule-based perturbations are easy to implement at the character or word level but ignore the pragmatics of how students actually write. Researchers sample from their intuition of "what an adversarial student does" rather than from corpus evidence of what students actually do.

**How to avoid:**
- Before generating perturbations, analyze the actual SRA / SemEval 2013 corpus for recurring student error patterns: common misconceptions, hedging phrases, question-rephrase tendencies, partial-answer structures.
- For LLM-assisted semantic perturbations, include a validity filter: human spot-check a sample (n ≥ 30 per perturbation type) to confirm the perturbation reads as plausible student output, not GPT output.
- For gaming perturbations specifically, base the attack taxonomy on documented adversarial strategies from Filighera et al. 2024 (adjective/adverb injection) and GradingAttack 2025 (token suffix, role-play prompt injection), not invented strategies.
- Distinguish clearly in the paper between perturbations inspired by real student behavior vs. synthetic stress tests — these measure different things and should be reported separately.

**Warning signs:**
- LLM-generated paraphrases score higher than the original on readability/fluency metrics
- Human reviewers can reliably distinguish LLM perturbations from genuine student answers above 80% accuracy
- All perturbation types cluster in the same region of an embedding space, far from the original student answer distribution

**Phase to address:** Perturbation engine design phase (earliest). Perturbation quality validation must happen before any grading model is run against them.

---

### Pitfall 2: Data Leakage in LOQO Cross-Validation via Shared Preprocessing

**What goes wrong:**
The Leave-One-Question-Out (LOQO) scheme is implemented correctly at the split level, but preprocessing steps — TF-IDF vocabulary construction, embedding normalization, label encoding, or tokenizer vocabulary — are fitted on the full dataset before the LOQO loop begins. This leaks distributional information from the held-out question into the training fold, inflating cross-question generalization metrics.

A subtler variant: the LLM perturbation generator is prompted with reference answers from all questions, including the held-out one, before the LOQO loop is established. The generated perturbations then carry statistical fingerprints of the held-out question's vocabulary.

**Why it happens:**
sklearn's `fit_transform` on the full dataset is the default pattern for preprocessing. Researchers add the LOQO loop after the pipeline is already built rather than integrating it from the start. The perturbation generation step is typically treated as a one-time preprocessing artifact, not as something scoped to training folds.

**How to avoid:**
- Wrap the entire pipeline inside the LOQO loop: split first, then fit all preprocessing (tokenizer vocab, TF-IDF, scaler) only on the training folds of each iteration.
- Treat perturbation generation as fold-aware: if perturbations use any reference answer or answer statistics from the dataset, scope that generation to training-fold answers only, or generate them once but verify no held-out information contaminates the generation prompt.
- Write a data-leakage test: for each LOQO fold, assert that the test question's answer text never appears in any object fitted during training setup for that fold.

**Warning signs:**
- LOQO performance is suspiciously close to within-question performance (gap < 5%)
- Performance on SemEval vs. custom dataset shows different patterns than expected given domain shift
- Removing the LOQO loop and replacing with random split produces near-identical numbers

**Phase to address:** Experiment runner and LOQO implementation phase. Build the loop first, add preprocessing inside it as a discipline.

---

### Pitfall 3: LLM Non-Determinism Invalidates Metric Reproducibility

**What goes wrong:**
LLM-based grading model outputs vary across runs even with temperature=0 and identical prompts, because inference non-determinism comes from GPU floating-point parallelism, not just sampling. The IVR (Invariance Violation Rate), SSR (Sensitivity Success Rate), and ASR (Adversarial Success Rate) metrics computed on one run differ from a second run, making it impossible to claim the reported numbers are the true value. Published results become unreproducible.

The research finding: even with temperature=0, LLMs are "rarely 100% stable across 5 re-runs with same data input" at the raw output level (arxiv 2408.04667). Gemini showed standard deviation of 0.15 grade points across 10 re-runs on identical ASAG inputs (PMC11429088).

**Why it happens:**
The assumption that temperature=0 gives deterministic outputs is technically incorrect for transformer models running on GPU hardware with non-deterministic floating-point reduction order. Researchers set temperature=0 and assume they are done. No replication budget is allocated.

**How to avoid:**
- Run each LLM grading model N=3 times with the same inputs, report mean and standard deviation for IVR/SSR/ASR.
- Log every prompt sent to every LLM and every raw response received (jsonl file per run) — this is already listed as a project requirement.
- For the paper, report LLM stability explicitly as a separate analysis: if σ(IVR) across runs > 0.02, acknowledge this bounds the precision of claims.
- Use `seed` parameters where the API exposes them (OpenAI supports `seed` in the request body since Nov 2023).
- Budget compute for at least 3 full runs of the LLM grading component.

**Warning signs:**
- Two runs of the same evaluation script produce different IVR/SSR values without changing any code or data
- Model comparison conclusions flip between runs (Model A > Model B in run 1, B > A in run 2)
- Any claim of the form "Model X achieves 87.3% SSR" reported to three significant figures

**Phase to address:** LLM grading model implementation phase. Stability analysis should be built into the runner before results are reported.

---

### Pitfall 4: Invalid Statistical Comparisons Between Grading Models

**What goes wrong:**
The paper reports IVR/SSR/ASR values for three grading models (supervised transformer, hybrid linguistic, LLM-based) and draws comparative conclusions (e.g., "the LLM grader shows 12% better SSR than the transformer") without any significance testing. Given that the metrics are computed on the same perturbation set and the same LOQO folds, samples across models are correlated — standard t-tests assuming independence are invalid. Without correcting for multiple comparisons across three model pairs and multiple metrics, at least one spuriously significant result is expected by chance.

**Why it happens:**
Significance testing in NLP is underused. Authors present metric tables and eyeball the differences. The ASAG literature itself rarely uses significance tests in comparative evaluations, normalizing this absence.

**How to avoid:**
- Use McNemar's test or permutation/bootstrap tests for comparing binary outcomes (grading decision correct/incorrect) across paired samples (same perturbation, different grader).
- For continuous metrics (IVR, SSR), use paired bootstrap resampling (1000 iterations) to compute confidence intervals and p-values — this correctly accounts for within-question correlation.
- Apply Bonferroni or Holm correction when comparing 3 models × 3 metrics (9 comparisons total).
- Reference: Dror et al. "The Hitchhiker's Guide to Testing Statistical Significance in Natural Language Processing" (ACL 2018) — the standard reference for this.
- Report effect sizes, not just significance flags.

**Warning signs:**
- Paper reads "Model A outperforms Model B" with no p-value or confidence interval
- All reported metric differences are between 0.5% and 5% — the range where chance variation is plausible
- Three-way comparison table with no statistical annotation

**Phase to address:** Metric computation and reporting phase. Design the statistical analysis plan before writing results — pre-specify which comparisons will be made and which tests will be used.

---

### Pitfall 5: Grading Model Overfitting to Question-Specific Surface Features

**What goes wrong:**
The supervised transformer-based grader and the hybrid linguistic model learn question-specific vocabulary (keywords from the reference answer, question-specific n-grams) as their primary grading signal. Under LOQO, when the held-out question has a different vocabulary distribution, performance collapses. The model is learning "does this answer contain words from the reference?" not "does this answer demonstrate understanding?". The perturbation evaluation then measures surface-feature matching, not semantic grading quality.

Research confirms: "Training a separate grading model for each question can result in models that only identify typical patterns in student responses to individual questions but cannot understand how to differentiate good responses from bad ones."

**Why it happens:**
Short answer grading datasets are small. With 30-50 student answers per question, transformers and even logistic regression will memorize question-specific patterns. The within-question train/test split looks good (high accuracy) while cross-question generalization fails silently until LOQO is applied.

**How to avoid:**
- Always evaluate on LOQO from the start — never report only within-question performance.
- For the hybrid linguistic model, explicitly exclude features that are question-specific: no direct reference answer word overlap features. Focus on structural features (answer length, hedging language, negation patterns).
- For the supervised transformer, use multi-question fine-tuning jointly, not per-question fine-tuning.
- Report LOQO performance as the primary metric in the paper; within-question performance goes in an appendix if at all.

**Warning signs:**
- Within-question accuracy >> LOQO accuracy (gap > 15 percentage points)
- The transformer's attention weights concentrate on content words from the reference answer
- Performance degrades dramatically when tested on SemEval vs. the training dataset domain (science vs. custom domain)

**Phase to address:** Supervised grading model training phase. LOQO baseline should be established before any feature engineering work begins.

---

### Pitfall 6: LLM Prompt Sensitivity Contaminates Comparative Claims

**What goes wrong:**
The rubric-driven LLM grader's IVR/SSR/ASR metrics shift substantially with minor prompt changes: reordering rubric criteria, changing from numeric to letter grade labels, adjusting instruction phrasing, or changing where the student answer appears relative to the reference answer. If Model A is compared to Model B using prompts that were informally tuned, the comparison reflects prompt quality differences as much as model quality differences.

Research evidence: "score sensitivity arises when changing prompt components such as rubric order, ID type (numeric vs. Roman), or reference answer quality, with even state-of-the-art judges like GPT-4o exhibiting fluctuations in correlation with human judgments."

**Why it happens:**
Prompt engineering for LLM graders is done iteratively and informally. The "best" prompt for GPT-4 is found by trial and error. The same prompt is then reused for Gemini and another LLM without validation. The resulting comparison bakes in prompt-LLM interaction effects.

**How to avoid:**
- Fix the prompt template structure before beginning comparative evaluation. Document it in the paper.
- Validate prompt stability separately: run the same LLM with 3 prompt variants on a held-out question; if IVR/SSR/ASR varies by more than 5%, the prompt is unstable and must be stabilized before comparative claims are made.
- Use the same structural prompt template across all LLMs — only change model-specific elements (API call parameters). Do not tune the prompt separately per LLM.
- Include a prompt sensitivity analysis as a supplementary experiment: report how much IVR/SSR/ASR vary under prompt perturbations vs. under answer perturbations.

**Warning signs:**
- Switching from "Score from 0 to 2" to "Score: correct/partially correct/incorrect" changes results by more than 3%
- One LLM consistently underperforms despite qualitative impressions that it is capable — prompt mismatch likely
- The prompt was revised after seeing some results

**Phase to address:** LLM grading model design phase. Lock the prompt template structure before running the full evaluation.

---

### Pitfall 7: LLM API Cost Overruns Halt the Experiment

**What goes wrong:**
The full evaluation requires: N student answers × 10-15 perturbations × 3 perturbation families × Q questions × 3+ LLMs × K LOQO folds × N_runs for stability analysis. A naive implementation sends each (answer, perturbation) pair as a separate API call, paying per-call overhead and getting no batching discount. Costs escalate to hundreds of dollars before the researcher notices, halting the experiment mid-run.

Specific risk: OpenAI's batch API offers 50% cost reduction for async calls. Missing this for a 1000+ call run doubles the cost unnecessarily.

**Why it happens:**
Cost estimation is skipped at design time. Each API call is a few cents, so the individual call feels trivial. The combinatorial explosion (answers × perturbations × questions × folds × runs) is only obvious when written as a product.

**How to avoid:**
- Before any full run, compute the call count formula explicitly: `n_answers × n_perturbations × n_questions × n_folds × n_llms × n_runs`. For SemEval 2013 SRA (~1500 answers), this easily exceeds 100K calls.
- Use OpenAI's Batch API (50% discount) for all non-interactive evaluation runs. Add explicit support for this in the experiment runner.
- Cache all LLM responses keyed by (prompt_hash, model_id) — identical prompts across folds need not be re-called.
- Implement a dry-run mode: compute and log call count and estimated cost before executing any API calls.
- Set hard cost limits in the API dashboard. Use a separate project/key for the experiment with a capped budget.

**Warning signs:**
- No dry-run cost estimation step in the experiment runner
- API calls are made inside the innermost loop without batching
- No response caching between LOQO folds
- The experiment takes more than 4 hours and costs accumulate while running unmonitored

**Phase to address:** Experiment runner implementation phase. Build cost estimation and caching before connecting to any paid API.

---

## Moderate Pitfalls

These cause degraded results or weak paper claims, but not fundamental invalidity.

---

### Pitfall 8: Insufficient Baselines Make Contribution Claims Unfalsifiable

**What goes wrong:**
The paper compares grading models against each other using the new IVR/SSR/ASR metrics, but includes no baseline that establishes what "bad" looks like on these metrics. Without a known-weak baseline (e.g., a random grader, a majority-class grader, or a bag-of-words exact-match grader), reviewers cannot calibrate whether the IVR/SSR values reported are actually meaningful. A model that achieves 70% SSR sounds impressive — unless random chance also achieves 70% given the perturbation distribution.

**How to avoid:**
- Include at minimum two baselines: (1) a random grader that assigns grades uniformly, (2) a majority-class grader that always assigns the most common grade in training. These establish the floor.
- Include one well-known weak model as an upper bound on "we already knew this was bad" — e.g., cosine similarity to reference answer (TF-IDF).
- Verify that the new metrics discriminate between these known-weak baselines and the models being evaluated. If they don't, the metric definition needs revision.

**Warning signs:**
- The results table contains only the three main models with no baseline row
- Reviewers ask "how does this compare to a simple keyword matcher?" and you don't have the answer
- IVR/SSR values for the random baseline have never been computed

**Phase to address:** Metric validation phase, before writing results. Run baselines before running the main models.

---

### Pitfall 9: Selective Perturbation Family Reporting (Cherry-Picking)

**What goes wrong:**
Preliminary results show that one perturbation family (e.g., invariance tests) produces cleaner results than another (e.g., gaming tests produce noisy, inconsistent results). The author reports only the clean family prominently, relegating the messy results to a footnote or omitting them. The paper's contribution claim implicitly rests on the cherry-picked family.

**How to avoid:**
- Pre-register the analysis plan: commit in writing (e.g., in the thesis chapter introduction) which perturbation families will be reported and that all three will appear in the main results table.
- Report all three families in the main table even if results are disappointing for one. Negative results for gaming perturbations are scientifically interesting — they indicate graders are not as vulnerable as feared.
- If one family is excluded from main results, provide an explicit, principled reason in the paper (e.g., "we found the gaming perturbations were not grounded in real student behavior and have excluded them pending better operationalization").

**Warning signs:**
- One perturbation family is absent from draft tables without explanation
- The results section discusses only the most favorable perturbation type
- Conclusion claims generalize across all three families but data only covers two

**Phase to address:** Results writing phase. Enforce complete reporting as a discipline from the first draft.

---

### Pitfall 10: Ignoring Grade Imbalance in Metric Computation

**What goes wrong:**
SemEval 2013 SRA and similar datasets are grade-imbalanced: "correct" answers are more common than "incorrect" and "partially correct" answers are rare. IVR/SSR/ASR computed on raw counts will be dominated by the majority class. A grader that always marks perturbations of "correct" answers as "correct" (never flipping) achieves high IVR by doing nothing. The metric appears good but the grader is not doing what the framework intends.

ASAG2024 benchmark introduced weighted RMSE specifically to address this problem (arxiv 2409.18596), confirming it is a known issue in the field.

**How to avoid:**
- Define IVR, SSR, ASR as stratified metrics: compute per grade tier (correct/partial/incorrect) and report the per-tier breakdown alongside the aggregate.
- Use class-weighted computation where each grade tier contributes equally to the aggregate regardless of frequency.
- Report the grade distribution of the dataset alongside every metric table so readers can assess imbalance.

**Warning signs:**
- The dataset's grade distribution is not reported anywhere in the paper
- IVR for "correct" answers >> IVR for "partially correct" answers
- The aggregate metric value is very close to the "correct" class baseline

**Phase to address:** Metric implementation phase. Build stratified reporting into the metric computation code from day one.

---

### Pitfall 11: Position Bias and Verbosity Bias in LLM Grader Prompts

**What goes wrong:**
When the LLM grader evaluates perturbed answers, the position of the student answer, reference answer, and rubric within the prompt affects the grade given. Perturbations that increase answer length get systematically higher grades (verbosity bias). Perturbations placed at the beginning of the answer get more attention than those embedded in the middle (position bias). These biases confound the SSR/IVR measurements.

Research finding: "Response length influences model judgment in complex ways, with increasing response length without corresponding quality improvement leading to a decline in model robustness." LLM judges show position bias that "increases with more answer candidates."

**How to avoid:**
- Standardize prompt structure: student answer always appears in the same position relative to the rubric and reference answer.
- For gaming perturbations that add content (adjective injection, keyword stuffing), measure the grade change while controlling for answer length. If the grader changes its score for length-matched perturbations that don't add semantically relevant content, report this as a verbosity bias finding.
- Run a controlled verbosity experiment: pad answers to different lengths while keeping content constant. If grades change, quantify verbosity bias as a separate analysis.

**Warning signs:**
- Longer perturbations consistently score higher than shorter ones regardless of content quality
- Moving the student answer from first to last position in the prompt changes grading outcomes
- Gaming perturbations that inject text at the beginning of answers succeed more than those that inject at the end

**Phase to address:** LLM grading model design and experiment runner phases.

---

## Minor Pitfalls

---

### Pitfall 12: Seed Sensitivity Masking Genuine Variance

**What goes wrong:**
The experiment runner uses a single fixed seed for all randomness (train/test splits, model initialization, perturbation sampling order). Results look stable but are actually specific to that one seed. The paper's claims may not hold for other seeds, which is only discovered during peer review or replication attempts.

**How to avoid:**
- Run experiments with 3 different seeds. Report mean ± std for all metrics.
- Use a seed table in the paper or appendix: list the 3 seeds and per-seed results.
- For the supervised transformer model specifically, initialize with at least 3 different seeds and report variance.

**Warning signs:**
- All results reported to 3 decimal places with no variance reported
- Changing the random seed by 1 shifts accuracy by more than 2 percentage points
- The experiment runner hard-codes `seed=42` with no seed variation mechanism

**Phase to address:** Experiment runner implementation. Build multi-seed support before running any evaluation.

---

### Pitfall 13: Custom Dataset Dependency Blocking Early Development

**What goes wrong:**
Implementation waits for the custom professor dataset before building any component. When the dataset arrives late (or with different structure than expected), the timeline collapses. Alternatively, the framework is built to assume the custom dataset's specific schema, making it brittle when integrated with SemEval or SRA.

**How to avoid:**
- Build everything against SRA/SemEval first. Treat the custom dataset as a plug-in.
- Define a canonical internal schema (question_id, student_answer, reference_answer, grade, grade_max) that both the public datasets and custom dataset map to. Build adapters for each source format.
- Do not gate any implementation milestone on the custom dataset's arrival.

**Warning signs:**
- A planning document says "wait for dataset" before implementing any component
- The data loading code has hard-coded paths or column names specific to the custom dataset
- Public dataset tests are skipped because "we'll test on the real data"

**Phase to address:** Dataset integration phase (first phase). Define the schema before any other component is built.

---

### Pitfall 14: LLM Hallucination in Rubric Evaluation

**What goes wrong:**
The rubric-driven LLM grader fabricates rubric criteria that were not specified, invents sub-criteria implied by the question but not in the rubric, or evaluates against background knowledge rather than the provided reference. This produces grading behavior that appears plausible but is not rubric-aligned. The IVR/SSR/ASR metrics then measure something partially uncontrolled.

Research finding: "LLMs lack symbolic structure and grounding and are unable to capture human language representation and understanding, coupled with other limitations such as hallucinations."

**How to avoid:**
- Include in the grading prompt an explicit instruction: "Grade solely based on the provided rubric and reference answer. Do not introduce criteria not listed."
- Log all graded outputs with their reasoning (chain-of-thought). Spot-check a sample (n=20) for rubric deviation.
- Compare grading reasoning across models: if one model consistently cites criteria not in the rubric, treat its results with a caveat.

**Warning signs:**
- Chain-of-thought reasoning mentions concepts not present in the reference answer
- The LLM consistently grades higher than human annotators on the same rubric
- Grading reasoning is generic and does not reference specific rubric criteria

**Phase to address:** LLM grading model implementation and validation phase.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Hard-code perturbation generation outside LOQO loop | Faster to implement | Data leakage in LOQO results; invalidates cross-question claims | Never |
| Single API call per perturbation (no batching) | Simpler code | 2× API cost; possible rate-limit failures on large runs | Never for full runs; OK for small dev tests |
| Report only aggregate metrics (no per-grade-tier breakdown) | Cleaner tables | Hides imbalance effects; weakens statistical claims | Never in final paper |
| Fix seed=42 only, no multi-seed runs | Faster | Results specific to one seed; not reproducible claims | Only in exploratory dev phase |
| Use one human annotator as ground truth | Avoids annotation cost | Single-annotator bias; claims about "human agreement" are invalid | Never for main evaluation; OK for spot-checks |
| Evaluate perturbation quality subjectively (author's own judgment) | Fast validation | Confirmation bias; reviewers will question it | Never; always use independent spot-check |
| Skip significance testing | Simpler results section | Comparative claims are scientifically unfounded | Never in final paper |

---

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| OpenAI API | Using `temperature=0` and assuming full determinism | Use temperature=0 AND seed parameter AND run 3 times; report variance |
| OpenAI Batch API | Using synchronous calls for large evaluation runs | Queue all non-interactive evaluation calls through Batch API for 50% cost reduction |
| HuggingFace Transformers | Loading models without pinning versions | Pin exact model checkpoint hash in config; transformers model releases change behavior |
| SemEval 2013 SRA dataset | Using raw files without checking for duplicate answer IDs across Beetle/SciEntsBank subsets | Load subsets independently; deduplicate by (question_id, answer_id) pair |
| LOQO cross-validation | Building sklearn pipeline then wrapping LOQO around it | Build LOQO loop first, fit pipeline inside each fold |

---

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Generating all perturbations synchronously before evaluation | Hours of wait before any results | Stream perturbations into evaluation queue as they are generated | At ~500+ answers |
| Loading full transformer model for each LOQO fold | GPU memory thrash, slow fold iterations | Cache model weights; only reload classifier head per fold | At >5 LOQO folds |
| Sending one API call per perturbation | Rate-limit errors, excessive cost | Batch calls; use async client | At >200 calls |
| Storing all perturbations in memory | OOM on large datasets | Write perturbations to disk (jsonl) immediately, load on demand | At >10K perturbations |

---

## "Looks Done But Isn't" Checklist

- [ ] **LOQO implementation:** Verify preprocessing is fitted inside the fold loop, not before it — run a leakage diagnostic test
- [ ] **LLM stability:** Verify multi-run variance has been measured and reported, not just one run
- [ ] **Perturbation validity:** Verify human spot-check of perturbation quality has been done, not just algorithmic generation
- [ ] **Statistical tests:** Verify significance tests exist for every comparative claim in the results section
- [ ] **Baselines:** Verify at least a random grader and majority-class grader have been evaluated and appear in results
- [ ] **Grade imbalance:** Verify per-tier metric breakdown exists, not only aggregate
- [ ] **Cost control:** Verify cost estimation dry-run exists in the experiment runner
- [ ] **Seed variance:** Verify 3-seed runs exist for the supervised model
- [ ] **Prompt locking:** Verify the LLM prompt template was frozen before comparative runs began
- [ ] **All perturbation families reported:** Verify all 3 families appear in the paper's main results table

---

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Discovered data leakage in LOQO | HIGH | Rebuild pipeline with preprocessing inside fold loop; rerun all experiments; all previous numbers are invalid |
| LLM non-determinism invalidating single-run results | MEDIUM | Rerun LLM evaluation N=3 times; report mean/std; update all metric tables |
| Cost overrun halting experiment | MEDIUM | Switch remaining calls to Batch API; implement caching; reduce to subset of LOQO folds for initial publication |
| Perturbations found unrealistic post-hoc | HIGH | Regenerate perturbation set with quality filter; rerun full evaluation; significant timeline impact |
| Significance tests reveal no significant differences | LOW | This is a valid scientific result; reframe as "no reliable difference between models on these metrics" — still publishable |
| Prompt sensitivity discovered mid-evaluation | MEDIUM | Lock prompt, rerun affected LLM models; add prompt sensitivity analysis as supplementary experiment |

---

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Unrealistic perturbations | Perturbation engine design | Human spot-check sample (n=30/type); plausibility rate ≥ 80% |
| LOQO data leakage | Experiment runner / LOQO implementation | Leakage diagnostic test passes; within-vs-LOQO gap is plausible (> 5%) |
| LLM non-determinism | LLM grading model implementation | 3-run stability analysis; σ per metric documented |
| Invalid statistical comparisons | Metric computation and reporting | Paired bootstrap tests for all comparative claims; Bonferroni corrected |
| Grader overfitting to question-specific features | Supervised model training | LOQO established before any feature engineering; gap reported |
| LLM prompt sensitivity | LLM grading model design | Prompt frozen before comparative runs; 3-variant sensitivity test run |
| API cost overruns | Experiment runner implementation | Dry-run cost estimate printed before any full run executes |
| Insufficient baselines | Metric validation | Random and majority-class baselines appear in results table |
| Cherry-picked perturbation families | Results writing | All 3 families present in main results table |
| Grade imbalance in metrics | Metric implementation | Per-tier breakdown in all metric output |
| Position/verbosity bias | LLM grading model design | Prompt structure standardized; verbosity control experiment run |
| Single seed | Experiment runner | 3-seed runs for supervised model; variance reported |
| Dataset schema brittleness | Dataset integration (first) | Canonical internal schema; adapters for both SRA and custom dataset |
| LLM hallucination in rubric grading | LLM model validation | Chain-of-thought spot-check; hallucination rate logged |

---

## Sources

- Filighera et al. 2024, "Cheating Automatic Short Answer Grading: On the Adversarial Usage of Adjectives and Adverbs," *International Journal of AI in Education* — [ERIC EJ1426308](https://eric.ed.gov/?q=automatic&ff1=dtySince_2024&id=EJ1426308)
- GradingAttack 2025, "Attacking Large Language Models Towards Short Answer Grading Ability" — [arxiv 2602.00979](https://arxiv.org/abs/2602.00979)
- LLM non-determinism: "Non-Determinism of Deterministic LLM Settings" — [arxiv 2408.04667](https://arxiv.org/html/2408.04667v5)
- LLM ASAG grading variance: PMC11429088, "LLM-based automatic short answer grading in undergraduate medical education" — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC11429088/)
- ASAG2024 benchmark (grade imbalance): [arxiv 2409.18596](https://arxiv.org/abs/2409.18596)
- Rubric-Conditioned LLM Grading, alignment and robustness: [arxiv 2601.08843](https://www.arxiv.org/pdf/2601.08843)
- LLM-as-Judge biases: "Justice or Prejudice? Quantifying Biases in LLM-as-a-Judge" — [arxiv 2410.02736](https://arxiv.org/html/2410.02736v1)
- Statistical significance in NLP: Dror et al., "The Hitchhiker's Guide to Testing Statistical Significance in NLP" — [ACL Anthology P18-1128](https://aclanthology.org/P18-1128/)
- ASAG cross-question generalization: Heilman & Madnani 2015, "The Impact of Training Data on Automated Short Answer Scoring Performance" — [ACL Anthology W15-0610](https://aclanthology.org/W15-0610/)
- Perturbation CheckLists for NLG metrics: [arxiv 2109.05771](https://arxiv.org/abs/2109.05771)
- Data leakage in cross-validation: [arxiv 2311.04179](https://arxiv.org/pdf/2311.04179)
- Fundamental tradeoffs between invariance and sensitivity: [ICML 2020, arxiv 2002.04599](https://arxiv.org/abs/2002.04599)
- Reproducibility in NLP: [PMC5998676](https://pmc.ncbi.nlm.nih.gov/articles/PMC5998676/)

---

*Pitfalls research for: Perturbation-First ASAG Evaluation Framework (IFKAD 2026)*
*Researched: 2026-02-20*
