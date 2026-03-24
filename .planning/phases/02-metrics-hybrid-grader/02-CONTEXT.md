# Phase 2: Metrics and Hybrid Grader - Context

**Gathered:** 2026-02-20
**Status:** Ready for planning

<domain>
## Phase Boundary

Dual-form IVR/SSR/ASR metric calculators validated against hand-computed expected values, within-question diagnostic protocol producing a "robustness drop in shift" comparison, and hybrid grader demonstrating the full evaluation loop end-to-end. No perturbation engine (Phase 3), no transformer fine-tuning (Phase 4), no LLM grading (Phase 5).

</domain>

<decisions>
## Implementation Decisions

### Metric Formulations
- IVR_flip: ANY score change on an invariance perturbation counts as a violation (strictest definition). Since the grading scale is discrete (correct/partially_correct_complete/partially_correct_incomplete/contradictory/irrelevant), every change is already a full category shift
- IVR_absdelta: Mean absolute score delta across all invariance perturbation pairs (continuous measure of instability magnitude)
- SSR_directional: Claude's discretion on whether direction-only or reaching-expected-grade counts as success — choose the most defensible definition from ASAG literature
- ASR_thresholded: Claude's discretion — choose between "increase >= 1 level OR crossing passing threshold" vs "crossing threshold only" based on literature
- Edge cases (zero denominators): Claude's discretion — choose the standard approach in evaluation literature (likely exclude from calculation)

### Hybrid Grader Design
- Feature set: Claude's discretion — choose the most defensible set from ASAG literature, starting from the requirement baseline (lexical overlap, length ratio, negation flags) and extending as appropriate
- Sentence-transformer model: all-MiniLM-L6-v2 (80MB, standard in literature, sufficient for a baseline grader)
- Classifier to combine features + embeddings: Claude's discretion — choose the most defensible option for a paper (likely logistic regression for interpretability or gradient boosting for performance)

### GraderInterface Contract
- Returns both grade label AND confidence score (float 0-1)
- Input: (question, rubric, student_answer)
- All grading models in later phases must implement this same interface

### Gold Test Dataset
- Size and structure: Claude's discretion — dimension it to cover all necessary cases while remaining hand-calculable
- Grade scale: Claude's discretion — choose between full SemEval 5-level scale or simplified 3-level for tests based on what validates the metrics most robustly
- Edge case coverage: Claude's discretion — decide whether edge cases are in the synthetic dataset or in separate unit tests
- Expected values MUST be documented with step-by-step derivation formulas (not just final values) — useful for thesis and debugging

### Protocol Comparison
- Robustness drop in shift format: Claude's discretion — choose the clearest table/visualization format for an academic paper
- Granularity: breakdown goes down to specific perturbation type level (e.g., synonym_substitution, negation_insertion) for maximum detail and downstream heatmap compatibility
- End-to-end validation: run on BOTH Beetle AND SciEntsBank corpora (not just Beetle subset)
- Mock perturbations for E2E: Claude's discretion — choose between hardcoded mocks vs minimal rule-based generator, whichever best validates the loop without anticipating Phase 3

### Claude's Discretion
- SSR_directional exact success criterion (direction-only vs reaching expected grade)
- ASR_thresholded exact threshold definition
- Zero-denominator handling for metrics
- Hybrid grader feature set selection
- Hybrid grader classifier choice
- Gold test dataset sizing and edge case strategy
- Protocol comparison visualization format
- Mock perturbation approach for E2E testing

</decisions>

<specifics>
## Specific Ideas

- The paper focus is on evaluation methodology, not grader quality — the hybrid grader is a baseline to demonstrate the framework works, not a SOTA pursuit
- Gold test derivations should be thesis-ready: step-by-step formulas showing how each expected value is computed
- Per-type granularity (not just per-family) ensures Phase 6 heatmaps have the data they need

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 02-metrics-hybrid-grader*
*Context gathered: 2026-02-20*
