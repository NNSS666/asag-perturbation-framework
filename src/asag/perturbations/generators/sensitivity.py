"""
Sensitivity perturbation generators — negation insertion, key concept deletion,
and semantic contradiction.

Sensitivity perturbations SHOULD change the gold grade of a student answer.
They test whether a grader correctly detects meaning-altering modifications.

Generators:
  NegationInsertionGenerator     — inserts "not" to invert the sentence meaning
  KeyConceptDeletionGenerator    — removes a domain-critical content word
  SemanticContradictionGenerator — replaces a claim with its opposite via
                                   a curated antonym dictionary

All three generators operate on text only (no external model calls at generation
time). NegationInsertionGenerator and SemanticContradictionGenerator are fully
deterministic from input text. KeyConceptDeletionGenerator uses random.Random(seed)
for word selection to maintain determinism for a given seed.
"""

import random
import re
from typing import List

from asag.perturbations.generators import PerturbationGenerator
from asag.schema.records import AnswerRecord, QuestionRecord

# ---------------------------------------------------------------------------
# NegationInsertionGenerator constants
# ---------------------------------------------------------------------------

# Auxiliary verbs: insert "not" directly after these
_AUX_PATTERN = re.compile(
    r"\b(is|are|was|were|will|can|could|should|would|does|did|has|have|had)\b",
    re.IGNORECASE,
)

# Simple domain verbs: replace with "does not <verb>"
_SIMPLE_VERB_PATTERN = re.compile(
    r"\b(flows|lights|connects|completes|opens|closes|conducts|carries|moves|"
    r"transfers|converts|increases|decreases|changes|causes|produces|requires|"
    r"contains|allows|prevents|stores|absorbs|reflects|emits|dissolves|"
    r"evaporates|melts|freezes)\b",
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# KeyConceptDeletionGenerator constants
# ---------------------------------------------------------------------------

STOPWORDS = frozenset({
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "this", "that", "these", "those", "is",
    "are", "was", "were", "be", "been", "being", "have", "has", "had",
    "it", "its",
})

# ---------------------------------------------------------------------------
# SemanticContradictionGenerator — curated antonym map
# ---------------------------------------------------------------------------

CONTRADICTION_MAP = {
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


def _lowercase_first_char(text: str) -> str:
    """Return text with the first character lowercased."""
    if not text:
        return text
    return text[0].lower() + text[1:]


class NegationInsertionGenerator(PerturbationGenerator):
    """Insert negation into a sentence to invert its meaning.

    Strategy (tried in order):
      1. Insert "not" after the first auxiliary verb (is, are, was, were, ...).
      2. Replace the first simple domain verb with "does not <verb>".
      3. Fallback: prepend "It is not true that " with first char lowercased.

    Fully deterministic from input text — no seed is used.
    """

    family = "sensitivity"
    type_name = "negation_insertion"
    n_variants = 1

    def generate(
        self,
        answer: AnswerRecord,
        question: QuestionRecord,
        seed: int,
    ) -> List[str]:
        """Return 1 negation-inserted variant.

        Args:
            answer:   Source AnswerRecord.
            question: QuestionRecord (unused).
            seed:     Unused (fully deterministic from text).

        Returns:
            List with exactly 1 string.
        """
        text = answer.student_answer

        # Strategy 1: "is" → "is not"
        match = _AUX_PATTERN.search(text)
        if match:
            end = match.end()
            return [text[:end] + " not" + text[end:]]

        # Strategy 2: "flows" → "does not flow"
        match = _SIMPLE_VERB_PATTERN.search(text)
        if match:
            verb = match.group(0)
            start = match.start()
            end = match.end()
            return [text[:start] + "does not " + verb + text[end:]]

        # Strategy 3: Fallback
        return [f"It is not true that {_lowercase_first_char(text)}"]


class KeyConceptDeletionGenerator(PerturbationGenerator):
    """Remove one domain-critical content word from the student answer.

    Selects a non-stopword content word (len >= 4) using random.Random(seed)
    and removes it from the token sequence. Uses simple whitespace split.
    """

    family = "sensitivity"
    type_name = "key_concept_deletion"
    n_variants = 1

    def generate(
        self,
        answer: AnswerRecord,
        question: QuestionRecord,
        seed: int,
    ) -> List[str]:
        """Return 1 word-deleted variant.

        Args:
            answer:   Source AnswerRecord.
            question: QuestionRecord (unused).
            seed:     Controls which content word is deleted.

        Returns:
            List with exactly 1 string, or empty list if no eligible word exists.
        """
        rng = random.Random(seed)
        tokens = answer.student_answer.split()

        eligible_indices = [
            i for i, w in enumerate(tokens)
            if w.lower() not in STOPWORDS and w.isalpha() and len(w) >= 4
        ]
        if not eligible_indices:
            return []

        idx = rng.choice(eligible_indices)
        new_tokens = tokens[:idx] + tokens[idx + 1:]
        return [" ".join(new_tokens)]


class SemanticContradictionGenerator(PerturbationGenerator):
    """Replace a domain concept with its semantic opposite.

    Uses a curated CONTRADICTION_MAP covering physics/electricity/circuits
    (Beetle dataset) and biology/chemistry/earth science (SciEntsBank dataset).

    Strategy:
      - Scan words for CONTRADICTION_MAP keys (case-insensitive, word-boundary).
      - Variant 0: replace the first match.
      - Variant 1: replace the second match (if it exists).
      - Fallback (no match found): return "It is not true that {text}".

    Fully deterministic from input text and map insertion order — no seed used.
    """

    family = "sensitivity"
    type_name = "semantic_contradiction"
    n_variants = 2

    def generate(
        self,
        answer: AnswerRecord,
        question: QuestionRecord,
        seed: int,
    ) -> List[str]:
        """Return up to 2 contradiction-substituted variants.

        Args:
            answer:   Source AnswerRecord.
            question: QuestionRecord (unused).
            seed:     Unused (fully deterministic from text).

        Returns:
            List of 1 or 2 strings. If no contradiction found, returns the
            fallback "It is not true that..." variant.
        """
        text = answer.student_answer

        # Collect all (match_start, match_end, replacement) triples
        matches: List[tuple] = []
        for key, value in CONTRADICTION_MAP.items():
            pattern = re.compile(r"\b" + re.escape(key) + r"\b", re.IGNORECASE)
            for m in pattern.finditer(text):
                # Preserve original case style
                original_word = m.group(0)
                if original_word.isupper():
                    replacement = value.upper()
                elif original_word[0].isupper():
                    replacement = value.capitalize()
                else:
                    replacement = value
                matches.append((m.start(), m.end(), replacement))
            # Only need first 2 distinct matches
            if len(matches) >= 2:
                break

        if not matches:
            return [f"It is not true that {_lowercase_first_char(text)}"]

        variants: List[str] = []
        # Sort by position to ensure deterministic order
        matches_sorted = sorted(matches[:2], key=lambda x: x[0])

        for start, end, replacement in matches_sorted[:2]:
            variant = text[:start] + replacement + text[end:]
            variants.append(variant)
            if len(variants) == 1 and len(matches_sorted) == 1:
                # Only one match found; break after first variant
                break

        return variants
