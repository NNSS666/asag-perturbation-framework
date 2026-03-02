"""
Invariance perturbation generators — synonym substitution and typo insertion.

Invariance perturbations should NOT change the gold grade of a student answer.
They test whether a grader is robust to surface-level paraphrases (synonyms) or
minor character-level noise (typos).

Gate 1 (SBERT cosine >= 0.85) applies to synonym_substitution outputs to catch
cases where the chosen synonym drifts the meaning. Gate 2 (negation heuristic)
applies to both types to catch meaning inversions introduced by the perturbation.

Design notes:
  - SynonymSubstitutionGenerator uses NLTK WordNet and POS tagging.
    Alphabetical sort of synonyms ensures determinism (RESEARCH.md Pitfall 4).
    Uses word_tokenize for punctuation-aware tokenization (RESEARCH.md Anti-Pattern 5).
  - TypoInsertionGenerator is pure Python (no NLTK). Uses random.Random(seed)
    for a deterministic typo operation.
"""

import random
import re
from typing import List, Optional

from asag.perturbations.generators import PerturbationGenerator
from asag.schema.records import AnswerRecord, QuestionRecord

# ---------------------------------------------------------------------------
# NLTK auto-download (Pattern 5 from RESEARCH.md)
# ---------------------------------------------------------------------------

try:
    from nltk import word_tokenize, pos_tag
    from nltk.corpus import wordnet
except LookupError:
    import nltk
    nltk.download("punkt_tab", quiet=True)
    nltk.download("averaged_perceptron_tagger_eng", quiet=True)
    nltk.download("wordnet", quiet=True)
    nltk.download("omw-1.4", quiet=True)
    from nltk import word_tokenize, pos_tag
    from nltk.corpus import wordnet

# ---------------------------------------------------------------------------
# POS tag → WordNet POS constant mapping
# ---------------------------------------------------------------------------

_POS_MAP = {
    "NN": wordnet.NOUN,
    "NNS": wordnet.NOUN,
    "NNP": wordnet.NOUN,
    "NNPS": wordnet.NOUN,
    "VB": wordnet.VERB,
    "VBD": wordnet.VERB,
    "VBG": wordnet.VERB,
    "VBN": wordnet.VERB,
    "VBP": wordnet.VERB,
    "VBZ": wordnet.VERB,
    "JJ": wordnet.ADJ,
    "JJR": wordnet.ADJ,
    "JJS": wordnet.ADJ,
}


def _get_synonyms_sorted(word: str, wn_pos: str) -> List[str]:
    """Return synonyms for word with given WordNet POS, alphabetically sorted.

    Alphabetical sorting ensures determinism across Python versions and
    platforms (avoids synset ordering variation — RESEARCH.md Pitfall 4).

    Excludes the original word itself and multi-word synonyms (contain '_').

    Args:
        word:   The word to find synonyms for (lowercase).
        wn_pos: WordNet POS constant (wordnet.NOUN, wordnet.VERB, wordnet.ADJ).

    Returns:
        Sorted list of single-word synonyms excluding the original word.
    """
    synonyms = set()
    for synset in wordnet.synsets(word, pos=wn_pos):
        for lemma in synset.lemmas():
            name = lemma.name().lower()
            if name != word and "_" not in name:
                synonyms.add(name)
    return sorted(synonyms)


class SynonymSubstitutionGenerator(PerturbationGenerator):
    """Replace content words (nouns, verbs, adjectives) with WordNet synonyms.

    Produces up to 2 variants: variant 0 substitutes at the first eligible word
    position, variant 1 at the second. If only 1 eligible position exists,
    returns 1 variant.

    Determinism: synonyms are alphabetically sorted; substitution positions are
    derived from token iteration order (first/second eligible word), not random
    sampling — so no seed is needed for the substitution itself. The seed
    parameter is accepted for interface consistency but unused.

    Eligibility criteria for a word to be substituted:
      - len(word) >= 4
      - word.isalpha() — no punctuation or numbers
      - POS tag maps to noun, verb, or adjective
      - At least one single-word WordNet synonym exists (excluding original word)
    """

    family = "invariance"
    type_name = "synonym_substitution"
    n_variants = 2

    def generate(
        self,
        answer: AnswerRecord,
        question: QuestionRecord,
        seed: int,
    ) -> List[str]:
        """Return up to 2 synonym-substituted variants of the student answer.

        Args:
            answer:   Source AnswerRecord.
            question: QuestionRecord (unused by this generator).
            seed:     Unused (substitution is fully deterministic from text).

        Returns:
            List of 0, 1, or 2 perturbed strings.
        """
        text = answer.student_answer
        tokens = word_tokenize(text)
        tagged = pos_tag(tokens)

        # Find eligible (position, word, synonym) triples
        substitutions: List[tuple] = []
        for i, (token, tag) in enumerate(tagged):
            if len(token) < 4 or not token.isalpha():
                continue
            wn_pos = _POS_MAP.get(tag)
            if wn_pos is None:
                continue
            synonyms = _get_synonyms_sorted(token.lower(), wn_pos)
            if synonyms:
                substitutions.append((i, token, synonyms[0]))

        variants: List[str] = []
        for i, (pos, original_token, synonym) in enumerate(substitutions[:2]):
            new_tokens = list(tokens)
            # Preserve capitalisation of the original token
            if original_token[0].isupper():
                replacement = synonym.capitalize()
            else:
                replacement = synonym
            new_tokens[pos] = replacement
            variants.append(" ".join(new_tokens))

        return variants


class TypoInsertionGenerator(PerturbationGenerator):
    """Introduce a single character-level typo into one content word.

    Selects a content word using random.Random(seed) and applies one of three
    operations chosen by the same RNG:
      0 — swap two adjacent characters
      1 — delete one character
      2 — duplicate one character

    Pure Python, no NLTK needed. Uses simple whitespace split since punctuation
    sensitivity is not required for typo insertion.
    """

    family = "invariance"
    type_name = "typo_insertion"
    n_variants = 1

    def generate(
        self,
        answer: AnswerRecord,
        question: QuestionRecord,
        seed: int,
    ) -> List[str]:
        """Return 1 typo-modified variant of the student answer.

        Args:
            answer:   Source AnswerRecord.
            question: QuestionRecord (unused by this generator).
            seed:     Controls word selection and operation choice.

        Returns:
            List with exactly 1 string, or empty list if no eligible word exists.
        """
        rng = random.Random(seed)
        text = answer.student_answer
        tokens = text.split()

        eligible_indices = [
            i for i, w in enumerate(tokens)
            if w.isalpha() and len(w) >= 4
        ]
        if not eligible_indices:
            return []

        idx = rng.choice(eligible_indices)
        word = tokens[idx]
        operation = rng.randint(0, 2)

        if operation == 0:
            # Swap adjacent characters at a random position
            if len(word) >= 2:
                pos = rng.randint(0, len(word) - 2)
                typo = word[:pos] + word[pos + 1] + word[pos] + word[pos + 2:]
            else:
                typo = word  # fallback: word too short to swap
        elif operation == 1:
            # Delete one character at a random position
            pos = rng.randint(0, len(word) - 1)
            typo = word[:pos] + word[pos + 1:]
        else:
            # Duplicate one character at a random position
            pos = rng.randint(0, len(word) - 1)
            typo = word[:pos] + word[pos] + word[pos:]

        new_tokens = list(tokens)
        new_tokens[idx] = typo
        return [" ".join(new_tokens)]
