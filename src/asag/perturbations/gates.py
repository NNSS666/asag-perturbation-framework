"""
Two-gate invariance validation system for perturbation quality control.

Gate 1 — SBERT cosine similarity threshold:
  Applies ONLY to synonym_substitution perturbations. Rejects candidates where
  cosine similarity to the original falls below GATE1_THRESHOLD (0.85).
  Typo insertions bypass Gate 1 entirely — typos are expected to slightly shift
  embeddings but are still surface-level changes (RESEARCH.md Critical Finding 1).

Gate 2 — Negation and antonym heuristic:
  Applies ONLY to invariance family types (synonym_substitution, typo_insertion).
  Rejects candidates that introduce NEW negation markers or NEW antonyms not
  present in the original text. This catches meaning inversions that SBERT
  may miss (RESEARCH.md Pitfall 7).

GateLog — per-type rejection statistics:
  Tracks tested/rejected counts for both gates across all perturbation types.
  Rejection rates are a reported research result showing how many invariance
  candidates are discarded by each validation stage.

Relationship to hybrid.py:
  NEGATION_PATTERN is the same regex used in graders/hybrid.py. It is duplicated
  here to maintain module independence (gates.py should not import from graders/).
  ANTONYM_MAP values are a subset/extension of CONTRADICTION_MAP from sensitivity.py,
  used for a different purpose: detecting meaning-change in invariance candidates.
"""

import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict

from sentence_transformers import util

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Hard-coded at 0.85 — no configurability to prevent threshold-shopping
# (RESEARCH.md Discretion Decision 2)
GATE1_THRESHOLD: float = 0.85

# Negation markers — same pattern as graders/hybrid.py NEGATION_PATTERN.
# Duplicated for independence; see module docstring.
NEGATION_PATTERN = re.compile(
    r"\b(not|never|no|cannot|can't|won't|doesn't|isn't|aren't|wasn't|weren't"
    r"|don't|didn't|haven't|hadn't|shouldn't|wouldn't|couldn't)\b",
    re.IGNORECASE,
)

# Antonym map for Gate 2 — used to detect new meaning-inverting words introduced
# by a perturbation. Mirrors CONTRADICTION_MAP in sensitivity.py but used
# differently: we check if an antonym VALUE appears in the candidate but was NOT
# in the original text (per-token set comparison avoids false positives from
# words that legitimately appear in both — RESEARCH.md Pitfall 7).
ANTONYM_MAP: Dict[str, str] = {
    "open": "closed",
    "closed": "open",
    "increase": "decrease",
    "decrease": "increase",
    "high": "low",
    "low": "high",
    "positive": "negative",
    "negative": "positive",
    "series": "parallel",
    "parallel": "series",
    "connect": "disconnect",
    "disconnect": "connect",
    "complete": "incomplete",
    "incomplete": "complete",
    "correct": "incorrect",
    "incorrect": "correct",
    "conduct": "insulate",
    "insulate": "conduct",
    "absorb": "reflect",
    "reflect": "absorb",
    "dissolve": "precipitate",
    "precipitate": "dissolve",
    "expand": "contract",
    "contract": "expand",
    "solid": "liquid",
    "liquid": "gas",
    "gas": "solid",
    "producer": "consumer",
    "consumer": "producer",
    "predator": "prey",
    "prey": "predator",
    "oxidize": "reduce",
    "reduce": "oxidize",
    "endothermic": "exothermic",
    "exothermic": "endothermic",
    "acidic": "basic",
    "basic": "acidic",
    "anode": "cathode",
    "cathode": "anode",
    "evaporate": "condense",
    "condense": "evaporate",
    "bright": "dim",
    "dim": "bright",
    "more": "less",
    "less": "more",
    "faster": "slower",
    "slower": "faster",
    "larger": "smaller",
    "smaller": "larger",
}

# Invariance family type names (Gate 2 applies only to these)
_INVARIANCE_TYPES = frozenset({"synonym_substitution", "typo_insertion"})


# ---------------------------------------------------------------------------
# GateLog
# ---------------------------------------------------------------------------

@dataclass
class GateLog:
    """Per-type rejection statistics for Gate 1 and Gate 2.

    Tracks how many candidates were tested and rejected by each gate for each
    perturbation type. Rejection rates are a reported research result.

    Fields:
        gate1_tested_by_type:   {type_name: count} — candidates tested by Gate 1
        gate1_rejected_by_type: {type_name: count} — candidates rejected by Gate 1
        gate2_tested_by_type:   {type_name: count} — candidates tested by Gate 2
        gate2_rejected_by_type: {type_name: count} — candidates rejected by Gate 2

    Usage:
        log = GateLog()
        passed = gate_1_sbert(original, candidate, "synonym_substitution", encoder, log)
        rates = log.rejection_rates()
        # rates["gate1"]["synonym_substitution"] == 0.0 or 1.0 depending on result
    """

    gate1_tested_by_type: Dict[str, int] = field(
        default_factory=lambda: defaultdict(int)
    )
    gate1_rejected_by_type: Dict[str, int] = field(
        default_factory=lambda: defaultdict(int)
    )
    gate2_tested_by_type: Dict[str, int] = field(
        default_factory=lambda: defaultdict(int)
    )
    gate2_rejected_by_type: Dict[str, int] = field(
        default_factory=lambda: defaultdict(int)
    )

    def rejection_rates(self) -> Dict[str, Dict[str, float]]:
        """Return per-type rejection rates for Gate 1 and Gate 2.

        Returns:
            Dict with keys "gate1" and "gate2", each mapping type_name → float
            rejection rate in [0.0, 1.0]. Types with zero tested candidates
            are excluded from the output to avoid division-by-zero.

        Example:
            {
                "gate1": {"synonym_substitution": 0.33},
                "gate2": {"synonym_substitution": 0.10, "typo_insertion": 0.05},
            }
        """
        result: Dict[str, Dict[str, float]] = {"gate1": {}, "gate2": {}}

        for type_name, tested in self.gate1_tested_by_type.items():
            if tested > 0:
                rejected = self.gate1_rejected_by_type.get(type_name, 0)
                result["gate1"][type_name] = rejected / tested

        for type_name, tested in self.gate2_tested_by_type.items():
            if tested > 0:
                rejected = self.gate2_rejected_by_type.get(type_name, 0)
                result["gate2"][type_name] = rejected / tested

        return result


# ---------------------------------------------------------------------------
# Gate 1 — SBERT cosine similarity
# ---------------------------------------------------------------------------

def gate_1_sbert(
    original: str,
    candidate: str,
    perturb_type: str,
    encoder: "SentenceTransformer",
    log: GateLog,
) -> bool:
    """Gate 1: SBERT cosine similarity threshold for synonym_substitution only.

    Only synonym_substitution candidates are evaluated by this gate. All other
    perturbation types return True immediately (bypass). This is the correct
    behaviour per RESEARCH.md Critical Finding 1: typo insertions are expected
    to slightly shift embeddings but remain surface-level changes.

    Args:
        original:     The original student answer text.
        candidate:    The perturbed candidate text to evaluate.
        perturb_type: Canonical perturbation type string.
        encoder:      A loaded SentenceTransformer model for encoding.
        log:          GateLog instance for recording tested/rejected counts.

    Returns:
        True if the candidate passes (should be kept).
        False if the candidate is rejected (too semantically different).
    """
    if perturb_type != "synonym_substitution":
        # All non-synonym-substitution types bypass Gate 1
        return True

    log.gate1_tested_by_type[perturb_type] += 1

    orig_emb = encoder.encode(original, show_progress_bar=False)
    cand_emb = encoder.encode(candidate, show_progress_bar=False)
    sim = float(util.cos_sim(orig_emb, cand_emb).item())

    if sim < GATE1_THRESHOLD:
        log.gate1_rejected_by_type[perturb_type] += 1
        return False

    return True


# ---------------------------------------------------------------------------
# Gate 2 — Negation and antonym heuristic
# ---------------------------------------------------------------------------

def _extract_negation_tokens(text: str) -> frozenset:
    """Return the set of matched negation token spans (lowercased) in text."""
    return frozenset(m.group(0).lower() for m in NEGATION_PATTERN.finditer(text))


def gate_2_negation(
    original: str,
    candidate: str,
    perturb_type: str,
    log: GateLog,
) -> bool:
    """Gate 2: Negation and antonym heuristic for invariance family types only.

    Applies only to synonym_substitution and typo_insertion. All other types
    return True immediately.

    Rejection criteria (either condition triggers rejection):
      1. New negation markers: candidate contains negation words NOT present in
         the original text (token-set comparison avoids false positives from
         pre-existing negation).
      2. New antonyms: any ANTONYM_MAP value appears in candidate tokens but was
         NOT in original tokens (per RESEARCH.md Pitfall 7 — "negative charge"
         in original should not be flagged).

    Args:
        original:     The original student answer text.
        candidate:    The perturbed candidate text to evaluate.
        perturb_type: Canonical perturbation type string.
        log:          GateLog instance for recording tested/rejected counts.

    Returns:
        True if the candidate passes (should be kept).
        False if the candidate is rejected (introduces meaning inversion).
    """
    if perturb_type not in _INVARIANCE_TYPES:
        # Gate 2 only applies to invariance family
        return True

    log.gate2_tested_by_type[perturb_type] += 1

    # --- Check 1: New negation markers ---
    original_negations = _extract_negation_tokens(original)
    candidate_negations = _extract_negation_tokens(candidate)
    new_negations = candidate_negations - original_negations
    negation_flag = bool(new_negations)

    # --- Check 2: New antonym words ---
    original_tokens = frozenset(w.lower() for w in original.split())
    candidate_tokens = frozenset(w.lower() for w in candidate.split())

    flagged_antonyms = {
        antonym_value
        for antonym_value in ANTONYM_MAP.values()
        if antonym_value.lower() in candidate_tokens
        and antonym_value.lower() not in original_tokens
    }
    antonym_flag = bool(flagged_antonyms)

    if negation_flag or antonym_flag:
        log.gate2_rejected_by_type[perturb_type] += 1
        return False

    return True
