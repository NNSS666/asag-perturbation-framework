"""
Perturbation Engine package — canonical type constants and top-level exports.

Seven perturbation types across three families:
  invariance  — should NOT change the grade (paraphrase, typo)
  sensitivity — SHOULD change the grade (deletion, negation, contradiction)
  gaming      — adversarial gaming attempt (keyword echoing, wrong extension)

Usage:
    from asag.perturbations import PERTURBATION_TYPES
    from asag.perturbations.generators import PerturbationGenerator
    from asag.perturbations import gate_1_sbert, gate_2_negation, GateLog
"""

# ---------------------------------------------------------------------------
# Canonical type string constants
# ---------------------------------------------------------------------------

PERTURBATION_TYPES = {
    "synonym_substitution": "invariance",
    "typo_insertion": "invariance",
    "negation_insertion": "sensitivity",
    "key_concept_deletion": "sensitivity",
    "semantic_contradiction": "sensitivity",
    "rubric_keyword_echoing": "gaming",
    "fluent_wrong_extension": "gaming",
}

# ---------------------------------------------------------------------------
# Re-exports from submodules (imported lazily to avoid circular imports at
# package init time when submodules reference PERTURBATION_TYPES)
# ---------------------------------------------------------------------------

from asag.perturbations.generators import (  # noqa: E402
    PerturbationGenerator,
    SynonymSubstitutionGenerator,
    TypoInsertionGenerator,
    NegationInsertionGenerator,
    KeyConceptDeletionGenerator,
    SemanticContradictionGenerator,
    RubricKeywordEchoingGenerator,
    FluentWrongExtensionGenerator,
)

from asag.perturbations.gates import (  # noqa: E402
    gate_1_sbert,
    gate_2_negation,
    GateLog,
    GATE1_THRESHOLD,
)

from asag.perturbations.engine import PerturbationEngine  # noqa: E402
from asag.perturbations.cache import PerturbationCache  # noqa: E402

__all__ = [
    # Constants
    "PERTURBATION_TYPES",
    # ABC
    "PerturbationGenerator",
    # Invariance generators
    "SynonymSubstitutionGenerator",
    "TypoInsertionGenerator",
    # Sensitivity generators
    "NegationInsertionGenerator",
    "KeyConceptDeletionGenerator",
    "SemanticContradictionGenerator",
    # Gaming generators
    "RubricKeywordEchoingGenerator",
    "FluentWrongExtensionGenerator",
    # Gates
    "gate_1_sbert",
    "gate_2_negation",
    "GateLog",
    "GATE1_THRESHOLD",
    # Engine and Cache (Plan 03-02)
    "PerturbationEngine",
    "PerturbationCache",
]
