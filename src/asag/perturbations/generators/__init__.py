"""
Perturbation generators — ABC and re-exports of all 7 generator classes.

Usage:
    from asag.perturbations.generators import (
        PerturbationGenerator,
        SynonymSubstitutionGenerator,
        TypoInsertionGenerator,
        NegationInsertionGenerator,
        KeyConceptDeletionGenerator,
        SemanticContradictionGenerator,
        RubricKeywordEchoingGenerator,
        FluentWrongExtensionGenerator,
    )
"""

from abc import ABC, abstractmethod
from typing import List

from asag.schema.records import AnswerRecord, QuestionRecord


class PerturbationGenerator(ABC):
    """Abstract base class for all perturbation generators.

    Subclasses must declare three class-level attributes and implement generate().

    Class attributes (must be defined in subclass):
        family (str):     High-level perturbation family.
                          One of: "invariance" | "sensitivity" | "gaming"
        type_name (str):  Canonical type string from PERTURBATION_TYPES dict.
                          e.g. "synonym_substitution", "negation_insertion"
        n_variants (int): Maximum number of candidate perturbed texts to produce
                          per answer. Actual output may be fewer if the answer
                          lacks sufficient content to generate all variants.

    Usage:
        class MyGenerator(PerturbationGenerator):
            family = "invariance"
            type_name = "my_type"
            n_variants = 2

            def generate(self, answer, question, seed):
                return [answer.student_answer + " (modified)"]
    """

    family: str
    type_name: str
    n_variants: int

    @abstractmethod
    def generate(
        self,
        answer: AnswerRecord,
        question: QuestionRecord,
        seed: int,
    ) -> List[str]:
        """Return up to n_variants candidate perturbed texts.

        Args:
            answer:   The source AnswerRecord to perturb.
            question: The QuestionRecord providing context (prompt, rubric,
                      reference answers). Used by gaming generators and
                      context-aware sensitivity generators.
            seed:     Random seed for all stochastic operations within this
                      call. Must produce identical output when called twice
                      with the same (answer, question, seed) triple.

        Returns:
            List of perturbed text strings. Length is at most n_variants.
            May return fewer variants (or empty list) if the answer is too
            short or lacks suitable content to perturb.
        """
        ...


# ---------------------------------------------------------------------------
# Re-exports — all 7 generator classes
# ---------------------------------------------------------------------------

from asag.perturbations.generators.invariance import (  # noqa: E402
    SynonymSubstitutionGenerator,
    TypoInsertionGenerator,
)
from asag.perturbations.generators.sensitivity import (  # noqa: E402
    NegationInsertionGenerator,
    KeyConceptDeletionGenerator,
    SemanticContradictionGenerator,
)
from asag.perturbations.generators.gaming import (  # noqa: E402
    RubricKeywordEchoingGenerator,
    FluentWrongExtensionGenerator,
)

__all__ = [
    "PerturbationGenerator",
    "SynonymSubstitutionGenerator",
    "TypoInsertionGenerator",
    "NegationInsertionGenerator",
    "KeyConceptDeletionGenerator",
    "SemanticContradictionGenerator",
    "RubricKeywordEchoingGenerator",
    "FluentWrongExtensionGenerator",
]
