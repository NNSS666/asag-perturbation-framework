"""
PerturbationEngine — orchestrates all 7 generators, applies two-gate validation,
caches results deterministically, and returns tagged PerturbationRecords.

Architecture:
  1. Engine instantiates all 7 generators once at init.
  2. generate_all() iterates (answer, generator) pairs:
     a. Computes a per-answer seed to ensure cross-answer independence.
     b. Checks PerturbationCache — returns cached candidates if available.
     c. Calls generator.generate() and caches the result.
     d. For invariance-family generators: applies Gate 1 then Gate 2 to each
        candidate; rejects candidates that fail (NO retry — rejection rate is
        a research result per RESEARCH.md Pitfall 2).
     e. Wraps each accepted candidate in a PerturbationRecord.
  3. Returns (records, gate_log) for downstream analysis.

Distribution (before gate rejections):
  synonym_substitution    2 variants (invariance)
  typo_insertion          1 variant  (invariance)
  negation_insertion      1 variant  (sensitivity)
  key_concept_deletion    1 variant  (sensitivity)
  semantic_contradiction  2 variants (sensitivity)
  rubric_keyword_echoing  2 variants (gaming)
  fluent_wrong_extension  1 variant  (gaming)
  ─────────────────────────────────────────────
  Total                  10 variants (before gate rejections)

Gate rejections may reduce the count below 10 for some answers. The gap is
the reported research result — do not compensate by retrying.
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple

from asag.perturbations.cache import PerturbationCache
from asag.perturbations.gates import GateLog, gate_1_sbert, gate_2_negation
from asag.perturbations.generators import (
    FluentWrongExtensionGenerator,
    KeyConceptDeletionGenerator,
    NegationInsertionGenerator,
    PerturbationGenerator,
    RubricKeywordEchoingGenerator,
    SemanticContradictionGenerator,
    SynonymSubstitutionGenerator,
    TypoInsertionGenerator,
)
from asag.schema.records import AnswerRecord, PerturbationRecord, QuestionRecord

# ---------------------------------------------------------------------------
# Invariance family type names (gates applied only to these)
# ---------------------------------------------------------------------------

_INVARIANCE_FAMILY = frozenset({"invariance"})


class PerturbationEngine:
    """Generates, validates, and caches all perturbations for a dataset.

    Args:
        seed:      perturb_seed from SeedConfig — passed to all generators
                   as a base seed. Each answer derives its own seed from this
                   to ensure cross-answer independence.
        cache_dir: Path for JSONL cache directory. None = no caching (for tests).
        encoder:   Optional pre-loaded SentenceTransformer instance for Gate 1.
                   If None, loads all-MiniLM-L6-v2 internally on first use.
    """

    def __init__(
        self,
        seed: int = 42,
        cache_dir: Optional[Path] = None,
        encoder=None,
    ) -> None:
        self._seed = seed
        self._cache = PerturbationCache(cache_dir)
        self._encoder = encoder  # lazy-loaded on first Gate 1 call if None
        self._gate_log = GateLog()

        # All 7 generators — order determines variant_idx within each type
        self._generators: List[PerturbationGenerator] = [
            SynonymSubstitutionGenerator(),   # invariance, up to 2 variants
            TypoInsertionGenerator(),          # invariance, 1 variant
            NegationInsertionGenerator(),      # sensitivity, 1 variant
            KeyConceptDeletionGenerator(),     # sensitivity, 1 variant
            SemanticContradictionGenerator(),  # sensitivity, up to 2 variants
            RubricKeywordEchoingGenerator(),   # gaming, up to 2 variants
            FluentWrongExtensionGenerator(),   # gaming, 1 variant
        ]

    def _get_encoder(self):
        """Lazy-load SentenceTransformer on first Gate 1 call."""
        if self._encoder is None:
            from sentence_transformers import SentenceTransformer  # type: ignore
            self._encoder = SentenceTransformer("all-MiniLM-L6-v2")
        return self._encoder

    def _answer_seed(self, answer_id: str) -> int:
        """Compute a per-answer seed deterministically from the base seed.

        Uses hash(answer_id) modulo 2^31 to stay within safe integer range.
        The base seed ensures cross-run reproducibility while the answer_id
        hash ensures cross-answer independence.

        Args:
            answer_id: The answer's unique identifier string.

        Returns:
            A non-negative integer in [seed, seed + 2^31).
        """
        return self._seed + hash(answer_id) % (2 ** 31)

    def generate_all(
        self,
        answers: List[AnswerRecord],
        questions: List[QuestionRecord],
    ) -> Tuple[List[PerturbationRecord], GateLog]:
        """Run all generators, apply gates, return records and rejection log.

        Processes every (answer, generator) pair. For invariance generators,
        applies Gate 1 (SBERT cosine) and Gate 2 (negation/antonym heuristic)
        to each candidate. Rejected candidates are discarded — no retry.

        Caching: candidates are cached before gate application (raw generator
        output). This ensures cache hits produce the same gate results on
        re-run.

        Args:
            answers:   List of AnswerRecord instances to perturb.
            questions: List of QuestionRecord instances providing question context.

        Returns:
            Tuple of:
              - List[PerturbationRecord]: all accepted perturbations across all
                answers and generators (up to 10 per answer before gate rejections)
              - GateLog: per-type rejection statistics for both gates
        """
        # Reset gate log for this run (allows re-use of engine instance)
        self._gate_log = GateLog()

        # Build lookup dict for O(1) question access
        question_lookup: Dict[str, QuestionRecord] = {
            q.question_id: q for q in questions
        }

        all_records: List[PerturbationRecord] = []

        for answer in answers:
            question = question_lookup.get(answer.question_id)
            if question is None:
                # Skip answers whose question is not in the questions list
                continue

            answer_seed = self._answer_seed(answer.answer_id)

            for generator in self._generators:
                # Check cache first
                cached = self._cache.get(
                    answer.student_answer, generator.type_name, answer_seed
                )
                if cached is not None:
                    candidates = cached
                else:
                    # Generate and cache (raw output, before gate filtering)
                    candidates = generator.generate(answer, question, answer_seed)
                    self._cache.put(
                        answer.student_answer,
                        generator.type_name,
                        answer_seed,
                        candidates,
                    )

                # Apply gates and build PerturbationRecords
                variant_idx = 0
                for candidate in candidates:
                    is_invariance = generator.family in _INVARIANCE_FAMILY

                    if is_invariance:
                        # Gate 1: SBERT cosine similarity (synonym_substitution only)
                        if not gate_1_sbert(
                            answer.student_answer,
                            candidate,
                            generator.type_name,
                            self._get_encoder(),
                            self._gate_log,
                        ):
                            continue  # discard — no retry

                        # Gate 2: Negation/antonym heuristic (all invariance types)
                        if not gate_2_negation(
                            answer.student_answer,
                            candidate,
                            generator.type_name,
                            self._gate_log,
                        ):
                            continue  # discard — no retry

                    perturb_id = (
                        f"{answer.answer_id}_{generator.type_name}_{variant_idx:03d}"
                    )

                    record = PerturbationRecord(
                        perturb_id=perturb_id,
                        answer_id=answer.answer_id,
                        family=generator.family,  # type: ignore[arg-type]
                        type=generator.type_name,
                        generator="rule-based",
                        seed=answer_seed,
                        text=candidate,
                    )
                    all_records.append(record)
                    variant_idx += 1

        return all_records, self._gate_log
