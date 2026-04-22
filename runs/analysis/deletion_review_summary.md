# Deletion Missed Cases — Qualitative Review Summary

**Sample**: 30 cases (15 L0 + 15 L1), random seeded (seed=42) from 2,639 (L0) and 2,361 (L1) missed key_concept_deletion pairs.

**Annotator**: author.

**Coding scheme**: see header of `deletion_missed_cases_annotated.txt`.

---

## Cross-tabulation: CATEGORY × SEVERITY (combined L0 + L1)

| Category | preserved | degraded | inverted | Total |
|---|---:|---:|---:|---:|
| domain_concept | 1 | 12 | 4 | **17 (57%)** |
| other (pronouns, quantifiers, generic nouns) | 5 | 1 | 2 | 8 (27%) |
| connective | 3 | 0 | 0 | 3 (10%) |
| verb | 1 | 0 | 1 | 2 (7%) |
| article | 0 | 0 | 0 | 0 (0%) |
| **Total** | **10 (33%)** | **13 (43%)** | **7 (23%)** | 30 |

## Per-grader breakdown

### L0 (n=15)
- Categories: domain_concept 7, other 4, verb 2, connective 2, article 0
- Severity: preserved 6, degraded 7, inverted 2

### L1 (n=15)
- Categories: domain_concept 10, other 4, connective 1, verb 0, article 0
- Severity: preserved 4, degraded 7, inverted 4

---

## Headline findings

### F1 — Deletion blindness is overwhelmingly directed at domain concepts
**17 of 30 missed cases (57%) involved deletion of a domain-specific term** (terminal, battery, circuit, voltage, bulb, closed, open, positive, negative, path). The remaining 43% spans pronouns, quantifiers, generic nouns, connectives and verbs.

The grader's tolerance is **not** a benign forgiveness of function-word omissions — it is concentrated on technical vocabulary that carries the answer's diagnostic content.

### F2 — Domain-concept deletions are almost never benign
Of the 17 missed domain-concept deletions, **16 (94%) were judged degraded or inverted in meaning**. Only one case (L1 [10]: "Circuit 2" → "2") was meaning-preserved, and only because the referent was fully transparent from the question text.

### F3 — Function-word deletions ARE benign
The 3 connective deletions (L0 [8] "Because", L0 [9] "between", L1 [4] "because") and most pronouns / existential expletives (L0 [1] "both", L0 [12] "There", L0 [14] "each", L1 [6] "where", L1 [7] "always") were correctly judged meaning-preserved by both author and grader. **In these cases the grader is right not to penalise.**

### F4 — A recurring critical-failure pattern: open/closed marker deletion
Two of the most striking inverted-meaning cases involve deletion of the modifier that distinguishes a working circuit from a broken one:
- L1 [5]: "in a closed path" → "in a path" (gold=correct, score 1.0 → 1.0)
- L1 [8]: "in a open path" → "in a path" (gold=correct, score 0.5 → 0.5)

The opposition closed/open is the central conceptual axis of the Beetle physics task. The grader treats the modified and unmodified versions as equivalent, even though they describe physically opposite situations.

### F5 — Subject deletion of definitional terms also goes undetected
Three "what is voltage?" answers had their definitional head noun deleted with no score change:
- L1 [11] "strength of electricity" → "of electricity" (head noun gone)
- L1 [13] "the difference of the electrical state..." → "the of the electrical state..." (head noun gone)
- L0 [11] "When the voltage changes to 0" → "When the changes to 0" (subject of change gone)

These are sentence-level semantic collapses that a human reader would immediately mark as broken.

---

## Implication for the paper

The qualitative finding **upgrades** the quantitative one. The §5.4 claim moves from:

> *The grader misses 69-75% of key-concept deletions.*

to:

> *The grader's deletion blindness is concentrated on domain-specific vocabulary that materially alters answer meaning. Of 30 manually-reviewed missed cases, 16/17 (94%) involving domain-concept deletion were judged to degrade or invert the answer's meaning, while function-word deletions (connectives, expletives, redundant quantifiers) were correctly tolerated. The grader is not exhibiting benign forgiveness of grammatical noise; it is failing precisely on the content-bearing words that distinguish a correct technical explanation from an incomplete or ill-formed one.*

This converts a statistical pattern into an interpretable mechanism — exactly the move the supervisor's feedback requested.

---

## Limitations to declare in paper

1. **Single-rater coding**. Per-case Cohen's kappa with a second rater is not available.
2. **N = 30** is illustrative, not inferential. Findings characterise a mechanism; quantitative claims rest on the n=5,000+ statistical analysis (sensitivity_deep.json, mcnemar_tests.json).
3. **Beetle-only**: domain (electrical circuits) shapes which concepts are "domain-specific". Generalisation to other ASAG corpora is future work.
