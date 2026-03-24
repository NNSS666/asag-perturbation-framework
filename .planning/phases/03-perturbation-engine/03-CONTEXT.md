# Phase 3: Perturbation Engine - Context

**Gathered:** 2026-02-21
**Status:** Ready for planning

<domain>
## Phase Boundary

Generate all three perturbation families (invariance, sensitivity, gaming) with two-gate invariance validation (SBERT cosine + negation heuristic), deterministic caching, and per-type tagging. Rule-based generation only — LLM-assisted perturbations arrive in Phase 5.

</domain>

<decisions>
## Implementation Decisions

### Perturbation types (7 total)

**Invariance (2 types — meaning-preserving):**
1. Synonym substitution — replace content words with WordNet synonyms
2. Typo/spelling insertion — introduce minor character-level noise

**Sensitivity (3 types — meaning-altering):**
3. Negation insertion — add/remove negation to invert meaning
4. Key concept deletion — remove domain-critical terms from the answer
5. Semantic contradiction — replace a claim with its semantic opposite

**Gaming (2 types — score inflation attempts):**
6. Rubric keyword echoing — echo key terms from reference answer without actual understanding
7. Fluent-but-wrong extension — append confident, fluent, but factually incorrect content

### Distribution & count
- 10 perturbations per answer: 2 variants for the 3 most variable types (synonym substitution, semantic contradiction, rubric keyword echoing), 1 variant for the remaining 4 types
- Same count per answer across both Beetle and SciEntsBank — consistent methodology

### Validation gate behavior
- **Claude's Discretion:** Discard-and-log vs retry-once strategy — Claude picks what best serves rejection-rate-as-research-result
- **Claude's Discretion:** SBERT threshold (0.85 default) as hard-coded constant vs configurable parameter — Claude picks based on adversarial NLP standards
- **Claude's Discretion:** Whether gates apply as reverse check on sensitivity/gaming perturbations (confirming they DO change meaning) or invariance-only — Claude picks what strengthens methodology
- **Claude's Discretion:** Rejection statistics granularity (per-type vs per-family) — Claude picks what serves the paper best

### Rule-based vs LLM boundary
- **Claude's Discretion:** Whether all 7 types get rule-based implementations in Phase 3, or some (semantic contradiction, fluent-but-wrong) are LLM-only stubs for Phase 5 — Claude picks based on feasibility with rules
- **Claude's Discretion:** Whether Phase 5 LLM versions replace or run alongside rule-based versions — Claude picks what's more valuable for the paper
- **Claude's Discretion:** NLP toolkit choice (NLTK+WordNet vs spaCy) — Claude picks the best fit for the chosen perturbation types
- **Claude's Discretion:** API design (single entry point vs composable generators per type) — Claude picks what fits existing codebase patterns

</decisions>

<specifics>
## Specific Ideas

- User explicitly chose 7 perturbation types from an initial set of 14 — prioritized signal-to-noise over exhaustive coverage
- The 7 types were selected to maximize discrimination power for the paper's core question: surface cues vs. true understanding
- Rubric keyword echoing directly tests the paper's central thesis (keyword overlap gaming)
- User trusts Claude's judgment on all technical implementation details — focus on methodological soundness

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 03-perturbation-engine*
*Context gathered: 2026-02-21*
