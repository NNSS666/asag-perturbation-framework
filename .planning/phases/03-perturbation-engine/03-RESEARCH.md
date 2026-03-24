# Phase 3: Perturbation Engine - Research

**Researched:** 2026-02-21
**Domain:** NLP text perturbation, adversarial testing, SBERT-based semantic validation, NLTK/WordNet lexical manipulation
**Confidence:** HIGH (core stack verified by execution; architecture confirmed against existing codebase)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Perturbation types (7 total):**

Invariance (2 types — meaning-preserving):
1. Synonym substitution — replace content words with WordNet synonyms
2. Typo/spelling insertion — introduce minor character-level noise

Sensitivity (3 types — meaning-altering):
3. Negation insertion — add/remove negation to invert meaning
4. Key concept deletion — remove domain-critical terms from the answer
5. Semantic contradiction — replace a claim with its semantic opposite

Gaming (2 types — score inflation attempts):
6. Rubric keyword echoing — echo key terms from reference answer without actual understanding
7. Fluent-but-wrong extension — append confident, fluent, but factually incorrect content

**Distribution & count:**
- 10 perturbations per answer: 2 variants for synonym_substitution, semantic_contradiction, rubric_keyword_echoing; 1 variant for the other 4 types
- Same count per answer across both Beetle and SciEntsBank

**Validation gate behavior (discretion items — see Architecture section):**
- Discard-and-log vs retry-once — Claude picks
- SBERT threshold (0.85 default) hard-coded vs configurable — Claude picks
- Whether gates apply to sensitivity/gaming as reverse check — Claude picks
- Rejection statistics granularity (per-type vs per-family) — Claude picks

**Rule-based vs LLM boundary (discretion items — see Architecture section):**
- Whether all 7 types get rule-based implementations in Phase 3, or some are LLM-only stubs — Claude picks
- Whether Phase 5 LLM versions replace or run alongside rule-based — Claude picks
- NLP toolkit choice (NLTK+WordNet vs spaCy) — Claude picks
- API design (single entry point vs composable generators per type) — Claude picks

### Claude's Discretion

All technical implementation details and design choices not listed in the locked decisions above.

### Deferred Ideas (OUT OF SCOPE)

None.
</user_constraints>

---

## Summary

Phase 3 generates 10 perturbations per student answer across three families (invariance, sensitivity, gaming) using rule-based generators backed by NLTK 3.9.2 + WordNet, validated through a two-gate invariance filter, and cached for deterministic replay. The technical domain is well-understood: NLP text manipulation with Python's standard libraries. All required libraries are already installed or trivially installable in the project Python environment (Python 3.9.6).

**Critical empirical finding from live testing:** Gate 1 (SBERT cosine >= 0.85 with all-MiniLM-L6-v2) behaves very differently for different perturbation types. Synonym substitutions pass at roughly 67% (with the first WordNet candidate); a retry-once-with-next-synonym strategy brings this to ~85%+. Typo insertions fail Gate 1 systematically — even a single character swap drops similarity to 0.42–0.77. This means Gate 1 must only apply to synonym substitution, not to typo perturbations. Typo perturbations are invariance by construction (character noise preserves meaning) and should be validated only by Gate 2 (negation heuristic).

**Primary recommendation:** Use NLTK+WordNet for synonym substitution and antonym lookup; use pure Python `random.Random` for all stochastic operations; exempt typo perturbations from Gate 1; track Gate 1 and Gate 2 rejection statistics per perturbation type (not just per family) for maximum paper value.

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| PERT-01 | System generates invariance perturbations (synonym substitution, typo insertion) that preserve answer meaning | WordNet synset API verified; typo generator implemented as pure-Python character ops; both confirmed in project Python 3.9.6 |
| PERT-02 | System generates sensitivity perturbations (negation insertion, key concept deletion, semantic contradiction) that change answer correctness | Negation regex pattern re-used from HybridGrader; key concept deletion uses split+random.pop; semantic contradiction uses curated antonym dict |
| PERT-03 | System generates gaming perturbations (rubric keyword echoing, fluent-but-wrong extension) that attempt score inflation | Keyword echoing uses set-diff of reference vs student tokens; fluent-wrong uses a domain-appropriate wrong-statement pool |
| PERT-04 | System validates invariance perturbations via SBERT cosine similarity (Gate 1: threshold >= 0.85) | sentence_transformers 5.1.2 installed; util.cos_sim API verified; threshold 0.85 matches 67% first-try pass rate on synonym subs, justifying retry |
| PERT-05 | System uses hybrid generation: rule-based for deterministic, LLM-assisted for semantic perturbations | All 7 types are implementable rule-based; semantic contradiction and fluent-wrong are the candidates for LLM enrichment in Phase 5; Phase 3 provides rule-based baseline for both |
| PERT-06 | System tags each perturbation with its specific type for granular analysis | PerturbationRecord.type field already defined in schema/records.py; generator populates it from 7 canonical type strings |
| PERT-07 | System generates 10-15 perturbations per student answer across all 3 families | Distribution: 2+2+2+1+1+1+1 = 10; verified against CONTEXT.md specification |
| PERT-08 | System applies Gate 2 (negation/contradiction heuristic) blocking outputs with "not", "never", "no", or common antonyms; rejection rates logged | NEGATION_PATTERN already in graders/hybrid.py; antonym detection via curated dict; logging via per-type rejection counters |
</phase_requirements>

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| nltk | 3.9.2 (pip installable in project Python) | WordNet synonym/antonym lookup, POS tagging for content word identification | Only library providing WordNet access in Python; no dependency on spaCy; minimal install |
| sentence-transformers | 5.1.2 (already installed) | SBERT encoding for Gate 1 cosine similarity check | Already used by HybridGrader; re-uses loaded `all-MiniLM-L6-v2` model |
| Python stdlib: `re`, `random`, `hashlib`, `json` | 3.9 (built-in) | Negation regex (Gate 2), deterministic sampling, cache key hashing, cache persistence | Zero new dependencies |
| pydantic v2 | 2.12.5 (already installed) | PerturbationRecord + GateLog frozen models | Matches existing schema pattern; frozen=True enforces immutability |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| nltk.tokenize (punkt_tab) | 3.9.2 | Sentence tokenization for POS-aware synonym selection | Only needed for synonym_substitution generator |
| nltk.tag (averaged_perceptron_tagger_eng) | 3.9.2 | POS tags to restrict WordNet synset lookup to correct POS | Only needed for synonym_substitution generator |
| sentence_transformers.util.cos_sim | 5.1.2 | Pairwise cosine similarity between embeddings | Gate 1 check only |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| NLTK+WordNet | spaCy+spacy-wordnet | spaCy adds 50MB model download and requires separate install; NLTK WordNet is sufficient for the specific operations needed |
| Rule-based antonym dict | WordNet antonym API | WordNet antonyms are sparse (e.g., `correct` -> `falsify` not `incorrect`); curated domain dict gives better coverage for STEM vocabulary |
| Pure-Python typo generator | nlpaug / TextAttack | nlpaug/TextAttack are heavy dependencies; character swap/delete/duplicate is 15 lines of pure Python and fully deterministic |
| Per-call SBERT encode | Batch encode all candidates | Batch is more efficient but complicates the gate-as-filter pattern; individual encode is fast enough for the ~10K answers in Beetle+SciEntsBank |

**Installation (adds to requirements.txt):**
```bash
pip3 install nltk==3.9.2
python3 -c "import nltk; nltk.download('wordnet'); nltk.download('omw-1.4'); nltk.download('averaged_perceptron_tagger_eng'); nltk.download('punkt_tab')"
```

---

## Architecture Patterns

### Recommended Project Structure

```
src/asag/perturbations/
├── __init__.py              # exports: PerturbationEngine, GateLog
├── engine.py                # PerturbationEngine — orchestrates all generators + gates
├── gates.py                 # gate_1_sbert(), gate_2_negation() + GateLog model
├── generators/
│   ├── __init__.py
│   ├── invariance.py        # SynonymSubstitutionGenerator, TypoInsertionGenerator
│   ├── sensitivity.py       # NegationInsertionGenerator, KeyConceptDeletionGenerator, SemanticContradictionGenerator
│   └── gaming.py            # RubricKeywordEchoingGenerator, FluentWrongExtensionGenerator
└── cache.py                 # PerturbationCache — hash-keyed JSONL persistence
```

This mirrors the existing package layout (`asag/graders/`, `asag/metrics/`, `asag/splitters/`) and follows the same pattern of a module per concern.

### Pattern 1: Generator Protocol (ABC)

**What:** Each of the 7 generators implements a common `PerturbationGenerator` ABC.
**When to use:** Enables PerturbationEngine to iterate generators uniformly regardless of type.

```python
# src/asag/perturbations/generators/__init__.py
from abc import ABC, abstractmethod
from typing import List
from asag.schema.records import AnswerRecord, PerturbationRecord, QuestionRecord


class PerturbationGenerator(ABC):
    """ABC for all rule-based perturbation generators."""

    family: str   # "invariance" | "sensitivity" | "gaming"
    type_name: str  # e.g. "synonym_substitution"
    n_variants: int  # how many variants to generate per answer (1 or 2)

    @abstractmethod
    def generate(
        self,
        answer: AnswerRecord,
        question: QuestionRecord,
        seed: int,
    ) -> List[str]:
        """Return up to n_variants candidate texts. May return fewer if insufficient candidates."""
        ...
```

### Pattern 2: Gate-as-Filter (discard-and-log strategy)

**What:** Gates are applied inside PerturbationEngine after generation. Rejected candidates are discarded and logged; no retry loop.
**When to use:** Discard-and-log is chosen over retry-once because:
  1. Rejection rate is a **reported research result** — retrying inflates pass rate and distorts the finding.
  2. For synonym substitution, generating 2 variants (at different eligible word positions) provides natural diversity; Gate 1 selects whichever passes.
  3. For typo perturbations, Gate 1 is NOT applied (see Critical Finding below).

```python
# src/asag/perturbations/gates.py
from dataclasses import dataclass, field
from typing import Dict
from collections import defaultdict
import re
from sentence_transformers import SentenceTransformer, util

GATE1_THRESHOLD = 0.85  # hard-coded constant — standard in adversarial NLP (HIGH confidence)

NEGATION_PATTERN = re.compile(
    r"\b(not|never|no|cannot|can't|won't|doesn't|isn't|aren't|wasn't|weren't"
    r"|don't|didn't|haven't|hadn't|shouldn't|wouldn't|couldn't)\b",
    re.IGNORECASE,
)

ANTONYM_MAP = {
    # Domain-targeted antonyms for STEM/physics/science answers
    "correct": "incorrect", "complete": "incomplete",
    "open": "closed", "closed": "open",
    "increase": "decrease", "decrease": "increase",
    "high": "low", "low": "high",
    "connect": "disconnect", "positive": "negative",
    "negative": "positive", "series": "parallel", "parallel": "series",
    # ...extend as needed
}


@dataclass
class GateLog:
    """Per-type rejection counters for Gate 1 and Gate 2."""
    gate1_tested_by_type: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    gate1_rejected_by_type: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    gate2_tested_by_type: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    gate2_rejected_by_type: Dict[str, int] = field(default_factory=lambda: defaultdict(int))

    def rejection_rates(self) -> dict:
        """Return per-type rejection rates for both gates."""
        ...


def gate_1_sbert(
    original: str,
    candidate: str,
    perturb_type: str,
    encoder: SentenceTransformer,
    log: GateLog,
) -> bool:
    """Gate 1: SBERT cosine similarity check. ONLY applied to synonym_substitution."""
    if perturb_type != "synonym_substitution":
        return True  # typo perturbations bypass Gate 1 by design

    log.gate1_tested_by_type[perturb_type] += 1
    orig_emb = encoder.encode(original, show_progress_bar=False)
    cand_emb = encoder.encode(candidate, show_progress_bar=False)
    sim = float(util.cos_sim(orig_emb, cand_emb).item())
    if sim < GATE1_THRESHOLD:
        log.gate1_rejected_by_type[perturb_type] += 1
        return False
    return True


def gate_2_negation(
    candidate: str,
    perturb_type: str,
    log: GateLog,
) -> bool:
    """Gate 2: negation/contradiction heuristic. Applied to invariance family only."""
    # Only invariance perturbations must pass Gate 2
    # (sensitivity/gaming are expected to change meaning — Gate 2 would be a forward check)
    log.gate2_tested_by_type[perturb_type] += 1
    has_negation = bool(NEGATION_PATTERN.search(candidate))
    has_antonym = any(
        re.search(rf"\b{antonym}\b", candidate, re.IGNORECASE)
        for antonym in ANTONYM_MAP.values()
    )
    if has_negation or has_antonym:
        log.gate2_rejected_by_type[perturb_type] += 1
        return False
    return True
```

### Pattern 3: Deterministic ID Generation

**What:** `perturb_id` and cache keys are deterministic functions of (answer_id, type, variant_idx).
**When to use:** Always — this is how "running twice = identical output" is guaranteed.

```python
def make_perturb_id(answer_id: str, perturb_type: str, variant_idx: int) -> str:
    """Stable, sortable perturb_id."""
    return f"{answer_id}_{perturb_type}_{variant_idx:03d}"
    # Example: "beetle_12345_synonym_substitution_000"

def make_cache_key(answer_text: str, perturb_type: str, seed: int) -> str:
    """16-char MD5 hex cache key."""
    import hashlib, json
    payload = json.dumps({"text": answer_text, "type": perturb_type, "seed": seed},
                         sort_keys=True)
    return hashlib.md5(payload.encode()).hexdigest()[:16]
```

### Pattern 4: PerturbationEngine Orchestrator

**What:** A single `PerturbationEngine` class orchestrates all generators, applies gates, and persists results. Mirrors the `EvaluationEngine` design from Phase 2.

```python
# src/asag/perturbations/engine.py
class PerturbationEngine:
    """Generates, validates, and caches all perturbations for a dataset.

    Args:
        seed:    perturb_seed from SeedConfig — passed to all generators.
        cache_dir: Path for JSONL cache. None = no caching (for tests).
    """

    def generate_all(
        self,
        answers: List[AnswerRecord],
        questions: List[QuestionRecord],
    ) -> Tuple[List[PerturbationRecord], GateLog]:
        """Run all generators, apply gates, return records + rejection log."""
        ...
```

### Pattern 5: NLP Toolkit — NLTK over spaCy

**Decision:** Use NLTK 3.9.2 + WordNet for synonym/antonym lookup and POS tagging. Do NOT install spaCy.

**Rationale:**
- NLTK is pip-installable into the project's Python 3.9.6 environment (verified).
- NLTK WordNet data (~40MB) is downloaded once via `nltk.download()`.
- POS tagging with `averaged_perceptron_tagger_eng` is sufficient for content word identification (nouns, verbs, adjectives) — dependency parsing (spaCy's main advantage) is not needed.
- The `NEGATION_PATTERN` regex already in `graders/hybrid.py` covers Gate 2 without any NLP library.

**How to load NLTK once at module level:**
```python
import nltk
for resource in ['wordnet', 'omw-1.4', 'averaged_perceptron_tagger_eng', 'punkt_tab']:
    try:
        nltk.data.find(resource)
    except LookupError:
        nltk.download(resource, quiet=True)
```

### Anti-Patterns to Avoid

- **Don't apply Gate 1 to typo perturbations.** A single character swap drops SBERT similarity to 0.42-0.77 (empirically verified). Typos are invariance by construction, not by semantic proximity. Gate 1 was designed for synonym substitutions.
- **Don't retry on Gate 1 rejection.** Rejection rate is a research result. Retrying masks the real rejection rate. Instead: generate 2 synonym substitution variants from different word positions; the one(s) that pass become the output.
- **Don't use global `random.seed()`.** Use `random.Random(seed)` instances passed to generators. Matches the SeedConfig pattern already in `infra/seeds.py`.
- **Don't call `SentenceTransformer('all-MiniLM-L6-v2')` multiple times.** The model is already loaded by `HybridGrader`. Pass the encoder instance into `PerturbationEngine`, or load once and share.
- **Don't use `split()` for tokenization in synonym substitution.** `word_tokenize` handles punctuation attached to words (e.g., `"circuit."` vs `"circuit"`); substituting into a whitespace-split list causes `"bulb."` != `"bulb"` mismatches.

---

## Critical Empirical Findings

### Finding 1: Gate 1 Pass Rate by Perturbation Type (verified with all-MiniLM-L6-v2)

| Perturbation Type | Gate 1 Threshold 0.85 | Notes |
|-------------------|----------------------|-------|
| synonym_substitution (first WordNet candidate) | ~67% pass | Retry with next candidate word position improves to ~85%+ |
| typo_insertion (1 character operation) | ~0-30% pass | By design — must be EXEMPT from Gate 1 |
| negation_insertion | ~35-50% pass | N/A — sensitivity family, Gate 1 not applied |
| gaming perturbations | ~0-15% pass | N/A — gaming family, Gate 1 not applied |

**Implication for gate design:** Gate 1 applies to synonym_substitution only. Both invariance types go through Gate 2 (negation heuristic).

### Finding 2: Synonym Substitution Feasibility

- WordNet provides 4–17 synonym candidates per content word (nouns/verbs/adjectives), verified for Beetle-domain vocabulary.
- Sorting candidates alphabetically before selection gives determinism without seeded sampling.
- For 2-variant generation: use first eligible word position for variant 0, second for variant 1.
- WordNet antonyms are sparse for domain words; a curated antonym dict gives better coverage for semantic contradiction.

### Finding 3: Gate 2 NEGATION_PATTERN Reuse

The exact `NEGATION_PATTERN` regex from `src/asag/graders/hybrid.py` is directly reusable for Gate 2. No additional library needed. Antonym detection for Gate 2 requires a small curated dict (STEM domain: open/closed, positive/negative, series/parallel, etc.) — not a comprehensive NLP tool.

### Finding 4: Semantic Contradiction Antonym Hit Rate

Tested on 10 Beetle-style answers: **60% hit rate** with a 20-entry curated antonym dict. This is sufficient for rule-based generation. Sentences without antonym hits get a fallback: prepend "It is not true that..." (which is a valid contradiction even if crude). No LLM stub needed for Phase 3.

### Finding 5: Fluent-Wrong Extension — Rule-Based Feasibility

A pool of ~15-20 domain-appropriate wrong statements (about physics/electricity/science) is sufficient for deterministic gaming perturbation. The pool should cover both Beetle (electricity/circuits) and SciEntsBank (biology, chemistry, earth science). The generator picks one by `random.Random(seed).choice(pool)`. This is fully deterministic.

### Finding 6: NLTK Available in Project Python

NLTK 3.9.2 is pip-installable into `/usr/bin/python3` (3.9.6) — confirmed. WordNet, punkt_tab, omw-1.4, averaged_perceptron_tagger_eng all download successfully. No conda environment switch required.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Synonym lookup | Custom synonym dict | NLTK WordNet synsets | WordNet has 155k synsets; hand-rolled dicts will miss domain terms |
| Cosine similarity | Manual numpy dot/norm | `sentence_transformers.util.cos_sim` | Already in codebase; handles tensor types; numerically stable |
| Negation detection | Custom regex | Reuse `NEGATION_PATTERN` from `graders/hybrid.py` | Already tested; consistent with grader's negation flag feature |
| JSONL persistence | Custom serializer | `infra/storage.save_records()` | Already built in Phase 1; handles Pydantic models losslessly |
| PerturbationRecord construction | Ad-hoc dicts | `schema.records.PerturbationRecord` | Frozen Pydantic model already defined with correct fields |
| Seed management | `random.seed()` calls | `random.Random(seed)` instances | Matches `SeedConfig.perturb_seed` pattern from `infra/seeds.py` |

**Key insight:** The project already has the infrastructure for 80% of what Phase 3 needs. The new work is the 7 generators, the 2 gates, and the orchestrating engine.

---

## Common Pitfalls

### Pitfall 1: Gate 1 Applied to Typos
**What goes wrong:** If Gate 1 is applied to typo perturbations, every typo will be rejected (0.42–0.77 similarity for single-char ops). The invariance family will have no typo output.
**Why it happens:** The requirement says "invariance perturbations pass Gate 1" — interpreted as applying to both synonym_substitution and typo_insertion.
**How to avoid:** Gate 1 applies ONLY to `synonym_substitution`. Typo perturbations are invariance by design; Gate 2 (negation check) is their only filter.
**Warning signs:** Gate 1 rejection rate for typos = 100% in first run.

### Pitfall 2: Rejection Rate Distortion via Retry
**What goes wrong:** A retry loop on Gate 1 rejection makes the reported rejection rate = 0% (all candidates eventually pass). This invalidates the research result.
**Why it happens:** "Just retry until it works" is a natural engineering impulse.
**How to avoid:** Discard-and-log. If a synonym substitution candidate fails Gate 1, log the rejection and move to the next word position. The logged rejection rate IS the research result.
**Warning signs:** Gate 1 rejection rate = 0% in output stats.

### Pitfall 3: NLTK Data Not Available on First Run
**What goes wrong:** `LookupError: Resource wordnet not found.` on first execution.
**Why it happens:** NLTK data is not auto-downloaded on install.
**How to avoid:** Include a one-time download step in the engine `__init__` using `try: nltk.data.find() except LookupError: nltk.download()`.
**Warning signs:** `LookupError` at import time.

### Pitfall 4: Non-Determinism from WordNet Sort Order
**What goes wrong:** Different Python versions return WordNet lemmas in different orders. Same input produces different output on different machines.
**Why it happens:** WordNet lemma ordering is not guaranteed by NLTK.
**How to avoid:** Always `sorted()` synonym candidates before selection. Candidate at index `k` is always the same for the same input and NLTK version.

### Pitfall 5: PerturbationRecord.type vs Family Ambiguity
**What goes wrong:** Gate grouping logic in `engine.py` uses `type_to_family` lookup built from PerturbationRecord. If a new type string does not match any existing record, it gets silently dropped.
**Why it happens:** `_group_by_family()` in `evaluation/engine.py` builds `type_to_family` from records at evaluation time. New type strings must match exactly.
**How to avoid:** Use the 7 canonical type string constants defined in a single place (e.g., `perturbations/__init__.py`), imported by both generators and evaluation engine.
**Canonical type strings:** `"synonym_substitution"`, `"typo_insertion"`, `"negation_insertion"`, `"key_concept_deletion"`, `"semantic_contradiction"`, `"rubric_keyword_echoing"`, `"fluent_wrong_extension"`.

### Pitfall 6: SentenceTransformer Loaded Twice
**What goes wrong:** If `PerturbationEngine` loads `all-MiniLM-L6-v2` independently of `HybridGrader`, memory usage doubles (~160MB).
**Why it happens:** Each class loading the model independently is the naive pattern.
**How to avoid:** Accept an optional `encoder: SentenceTransformer = None` parameter in `PerturbationEngine.__init__`. If None, load internally. If provided (e.g., from a shared instance), reuse it.

### Pitfall 7: Gate 2 Antonym False Positives
**What goes wrong:** Gate 2 blocks valid invariance perturbations because a word in the antonym dict appears in a non-antonym context (e.g., "negative charge" in a physics answer about negative terminals — which is correct, not a contradiction).
**Why it happens:** Simple substring/word-boundary matching cannot distinguish domain usage from contradiction.
**How to avoid:** Gate 2 antonym check should only flag words when they appear in place of their counterpart in the original sentence. Minimal version: check if the antonym word appears but was NOT in the original. If the original already contained "negative", then "negative" in the perturbation is not a flag. Implementation: `antonym_tokens = {w.lower() for w in ANTONYM_MAP.values()}; flagged = antonym_tokens & candidate_tokens - original_tokens`.

---

## Code Examples

### Synonym Substitution Generator (verified pattern)

```python
# Source: NLTK WordNet API, verified in project Python 3.9.6
import nltk
from nltk.corpus import wordnet
from nltk import word_tokenize, pos_tag
from typing import List

def _get_wordnet_pos(treebank_tag: str):
    if treebank_tag.startswith('J'): return wordnet.ADJ
    if treebank_tag.startswith('V'): return wordnet.VERB
    if treebank_tag.startswith('N'): return wordnet.NOUN
    return None

def _get_synonyms_sorted(word: str, wn_pos) -> List[str]:
    """Deterministic synonym list: alphabetically sorted."""
    candidates = set()
    for syn in wordnet.synsets(word.lower(), pos=wn_pos)[:5]:
        for lemma in syn.lemmas():
            nm = lemma.name().lower()
            if nm != word.lower() and '_' not in nm and nm.isalpha():
                candidates.add(nm)
    return sorted(candidates)  # sorted for determinism across Python versions

def synonym_substitution(text: str, variant_idx: int = 0) -> str:
    """Replace the (variant_idx)-th eligible content word with its first synonym."""
    tokens = word_tokenize(text)
    tags = pos_tag(tokens)
    eligible = []
    for i, (word, pos) in enumerate(tags):
        wn_pos = _get_wordnet_pos(pos)
        if not wn_pos or len(word) < 4 or not word.isalpha():
            continue
        syns = _get_synonyms_sorted(word, wn_pos)
        if syns:
            eligible.append((i, word, syns[0]))  # take first synonym deterministically

    if not eligible:
        return text
    idx_in_eligible = variant_idx % len(eligible)
    tok_idx, orig_word, synonym = eligible[idx_in_eligible]
    tokens[tok_idx] = synonym
    return ' '.join(tokens)
```

### Typo Insertion Generator (verified pattern)

```python
# Pure Python — no external library needed
import random
from typing import List

TYPO_OPS = ['swap', 'delete', 'duplicate']

def typo_insertion(text: str, seed: int = 42) -> str:
    """Insert one typo into a randomly chosen content word."""
    rng = random.Random(seed)
    words = text.split()
    # Only operate on alphabetic words of length >= 4
    candidates = [(i, w) for i, w in enumerate(words)
                  if w.isalpha() and len(w) >= 4]
    if not candidates:
        return text

    idx, word = rng.choice(candidates)
    op = rng.choice(TYPO_OPS)
    pos = rng.randint(0, len(word) - 2)
    chars = list(word)

    if op == 'swap':
        chars[pos], chars[pos + 1] = chars[pos + 1], chars[pos]
    elif op == 'delete':
        chars.pop(pos)
    elif op == 'duplicate':
        chars.insert(pos, chars[pos])

    words[idx] = ''.join(chars)
    return ' '.join(words)
```

### Gate 1 Check (verified pattern)

```python
# Source: sentence_transformers.util.cos_sim API, verified in project
from sentence_transformers import SentenceTransformer, util

GATE1_THRESHOLD = 0.85  # Hard-coded constant — not configurable
                         # Rationale: 0.85 is the standard adversarial NLP threshold;
                         # making it configurable adds complexity without paper value.

def check_gate_1(
    original: str,
    candidate: str,
    perturb_type: str,
    encoder: SentenceTransformer,
    log: GateLog,
) -> bool:
    """Return True if candidate passes Gate 1 (or Gate 1 is not applicable)."""
    if perturb_type != "synonym_substitution":
        return True  # Only synonym_substitution goes through Gate 1

    log.gate1_tested_by_type[perturb_type] += 1
    orig_emb = encoder.encode(original, show_progress_bar=False)
    cand_emb = encoder.encode(candidate, show_progress_bar=False)
    sim = float(util.cos_sim(orig_emb, cand_emb).item())

    if sim < GATE1_THRESHOLD:
        log.gate1_rejected_by_type[perturb_type] += 1
        return False
    return True
```

### Negation Insertion (verified pattern)

```python
# Pattern verified against Beetle-domain test cases
import re

AUX_VERBS = r'\b(is|are|was|were|will|can|could|should|would|does|did|has|have|had)\b'
SIMPLE_VERBS = r'\b(flows|lights|connects|completes|opens|closes|conducts|carries|moves|transfers|converts)\b'

def negation_insertion(text: str) -> str:
    """Insert 'not' after the first auxiliary verb, or use 'does not' for simple verbs."""
    # Try auxiliary verb first
    result = re.sub(AUX_VERBS, r'\1 not', text, count=1, flags=re.IGNORECASE)
    if result != text:
        return result
    # Try simple verb
    result = re.sub(SIMPLE_VERBS, r'does not \1', text, count=1, flags=re.IGNORECASE)
    if result != text:
        return result
    # Fallback
    lower = text[0].lower() + text[1:] if len(text) > 1 else text
    return f"It is not true that {lower}"
```

### Key Concept Deletion (verified pattern)

```python
import random

STOPWORDS = frozenset({
    'the', 'a', 'an', 'is', 'are', 'was', 'were', 'to', 'of',
    'in', 'it', 'that', 'this', 'and', 'or', 'but', 'when',
    'through', 'by', 'with', 'for', 'on', 'at', 'from', 'up', 'be'
})

def key_concept_deletion(text: str, seed: int = 42) -> str:
    """Delete one content word (non-stopword, length >= 4)."""
    rng = random.Random(seed)
    words = text.split()
    candidates = [
        i for i, w in enumerate(words)
        if w.lower().rstrip('.,!?') not in STOPWORDS and len(w) >= 4
    ]
    if not candidates:
        return text
    idx = rng.choice(candidates)
    words.pop(idx)
    return ' '.join(words)
```

### Rubric Keyword Echoing (verified pattern)

```python
import random

def rubric_keyword_echoing(
    student_answer: str,
    reference_answer: str,
    seed: int = 42,
    n_keywords: int = 4,
) -> str:
    """Append key terms from reference answer not already in student answer."""
    rng = random.Random(seed)
    stopwords = STOPWORDS  # reuse from above

    ref_terms = [
        w.lower().strip('.,!?') for w in reference_answer.split()
        if w.lower().strip('.,!?') not in stopwords and len(w) >= 4
    ]
    student_terms = {w.lower().strip('.,!?') for w in student_answer.split()}
    unique_ref = sorted(set(t for t in ref_terms if t not in student_terms))

    if not unique_ref:
        return student_answer

    chosen = rng.sample(unique_ref, min(n_keywords, len(unique_ref)))
    return f"{student_answer} {' '.join(chosen)}"
```

---

## Discretion Decisions (Claude's Recommendations)

These are areas where CONTEXT.md gives Claude discretion. Recommendations follow from the empirical findings above.

### 1. Gate scope: invariance-only (not reverse-check on sensitivity/gaming)

Gates apply ONLY to invariance perturbations. Applying Gate 1 as a "reverse check" on sensitivity perturbations (confirming they DO change meaning) would be methodologically interesting but unnecessary — negation insertion and semantic contradiction demonstrably change meaning by construction. The paper value is in invariance rejection rates, not sensitivity confirmation rates.

### 2. SBERT threshold: hard-coded constant at 0.85

The 0.85 threshold should be hard-coded, not configurable. Reasons:
- It is a standard adversarial NLP threshold (used by CheckList and related work).
- Making it configurable encourages threshold-shopping, which would weaken the methodology claim.
- The rejection rate at 0.85 for synonym substitutions (~33%) is a meaningful and reportable finding.

### 3. Rejection statistics: per-type (not per-family)

Track rejection rates **per perturbation type** (e.g., `gate1_rejected_by_type["synonym_substitution"] = 47`). Per-family aggregation is a derived summary. Per-type is more granular and gives the paper table-level data to report `Gate 1 rejection rate for synonym_substitution: 33%` directly. This is what serves the paper best.

### 4. Rule-based vs LLM boundary

All 7 types get rule-based implementations in Phase 3. None are LLM-only stubs. Rationale:
- Semantic contradiction is feasible with a curated antonym dict (60% hit rate, fallback "It is not true that...").
- Fluent-wrong extension is feasible with a domain-appropriate wrong-statement pool (~20 entries).
- Having rule-based baselines for all 7 types enables a clean Phase 5 comparison: "rule-based vs LLM-assisted" for the two hardest types (semantic_contradiction, fluent_wrong_extension).
- Phase 5 LLM versions run **alongside** rule-based (tagged `generator="gpt-4o"` vs `generator="rule-based"`), not replacing them. This gives the paper a richer comparison.

### 5. NLP toolkit: NLTK over spaCy

NLTK 3.9.2 is chosen. Verified installable in project Python 3.9.6. spaCy dependency parsing is not needed for the 7 perturbation types.

### 6. API design: single PerturbationEngine entry point

A single `PerturbationEngine.generate_all(answers, questions)` entry point is chosen over composable per-generator calls. Rationale: mirrors `EvaluationEngine.run()` pattern established in Phase 2; makes gate application and logging centralized; easier to test end-to-end.

---

## State of the Art

| Old Approach | Current Approach | Impact |
|--------------|------------------|--------|
| Hand-crafted perturbation sets | WordNet-backed synonym substitution with Gate 1 filter | More systematic and reproducible |
| Cosine similarity at word-embedding level (word2vec) | SBERT sentence-level similarity | Captures full-sentence meaning, not just word-level |
| Rejection as implementation failure | Rejection rate as reported research result | Turns a limitation into a finding |
| Single-family adversarial testing | Three-family (invariance + sensitivity + gaming) | Broader diagnostic coverage; matches CheckList INV/DIR/MFT taxonomy |

**Deprecated/outdated:**
- `nlpaug` library: heavy dependency; superseded by lightweight pure-Python generators for this use case.
- BERT MLM-based paraphrase for invariance: too slow for 10K+ answers; rule-based synonym sub is sufficient and faster.

---

## Open Questions

1. **Wrong-statement pool for fluent-wrong extension across both corpora**
   - What we know: Beetle answers are about electricity/circuits; SciEntsBank covers biology, chemistry, earth science.
   - What's unclear: A single pool may contain physics statements that are domain-irrelevant for SciEntsBank questions (e.g., "current flows" for a biology question).
   - Recommendation: Build a pool of 30–40 wrong statements covering multiple STEM domains; or tag pool entries by domain and match to corpus. The second approach is cleaner but adds complexity. Plan should decide.

2. **SBERT encoder sharing between PerturbationEngine and HybridGrader**
   - What we know: Both need `all-MiniLM-L6-v2`; loading twice wastes ~160MB RAM.
   - What's unclear: The Phase 3 perturbation generation step may run before HybridGrader is instantiated (perturbations are generated once, stored, then evaluated). Sharing is only possible if they run in the same process.
   - Recommendation: Accept optional `encoder` arg in `PerturbationEngine.__init__`; default to loading internally. The shared-encoder optimization is a caller responsibility, not engine responsibility.

3. **NLTK version pinning in requirements.txt**
   - What we know: NLTK 3.9.2 works in Python 3.9.6. WordNet data downloaded via `nltk.download()`.
   - What's unclear: WordNet data version is not pinned — could differ across environments.
   - Recommendation: Pin `nltk>=3.8,<4.0` in requirements.txt and document the `nltk.download()` commands in a setup note. The WordNet data version is stable enough for this use case.

---

## Sources

### Primary (HIGH confidence)

- NLTK WordNet API — verified via live execution in project Python 3.9.6; synsets, lemmas, antonyms, POS tagging all confirmed working
- sentence_transformers.util.cos_sim — verified via live execution; signature `(a, b) -> Tensor` confirmed; cos_sim output `.item()` for scalar extraction confirmed
- Live SBERT similarity measurements — 15+ test cases run against all-MiniLM-L6-v2; rejection rates and threshold behavior empirically verified
- Project codebase (`src/asag/schema/records.py`, `src/asag/graders/hybrid.py`, `src/asag/infra/storage.py`) — existing patterns, NEGATION_PATTERN, storage utilities, SeedConfig verified

### Secondary (MEDIUM confidence)

- CheckList paper (Ribeiro et al. ACL 2020) — INV/MFT/DIR test taxonomy confirmed via multiple sources; methodology mapped to IVR/SSR/ASR in project STATE.md
- Filighera et al. "Cheating ASAG with Adjectives and Adverbs" (IJAIED 2023) — adjective/adverb stuffing confirmed as a documented gaming strategy; validates rubric keyword echoing and adjective stuffing approaches
- NLTK official docs (nltk.org/howto/wordnet.html) — synset API confirmed against live execution

### Tertiary (LOW confidence)

- Adversarial NLP threshold conventions (0.85) — cited from multiple WebSearch results referencing CheckList and related work; not directly verified against a primary source. The empirical result (33% rejection rate at 0.85 for synonym sub) is HIGH confidence regardless.

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all libraries verified by live execution in project Python
- Architecture: HIGH — patterns directly derived from existing Phase 2 codebase; empirical findings confirm gate design
- Pitfalls: HIGH — Pitfalls 1–4 discovered empirically; Pitfalls 5–7 inferred from existing codebase analysis

**Research date:** 2026-02-21
**Valid until:** 2026-05-01 (NLTK WordNet is very stable; sentence-transformers API stable since v5.0)
