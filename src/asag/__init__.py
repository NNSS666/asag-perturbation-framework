"""
asag -- Automatic Short Answer Grading research toolkit.

Provides canonical schema types, dataset loaders, splitting protocols,
perturbation generators, grading interfaces, metric computation,
and evaluation infrastructure for robustness benchmarking of ASAG models.

Public API:
    from asag import (
        EvaluationEngine, PerturbationEngine,
        HybridGrader, LLMGrader,
        SemEval2013Loader, MetricCalculator,
    )
"""

__version__ = "0.1.0"

# -- Evaluation ---------------------------------------------------------------
from asag.evaluation.engine import EvaluationEngine, EvaluationResult

# -- Perturbations -------------------------------------------------------------
from asag.perturbations.engine import PerturbationEngine

# -- Graders -------------------------------------------------------------------
from asag.graders.hybrid import HybridGrader
from asag.graders.llm import LLMGrader
from asag.graders.base import GraderInterface, GradeResult

# -- Loaders -------------------------------------------------------------------
from asag.loaders.semeval2013 import SemEval2013Loader

# -- Metrics -------------------------------------------------------------------
from asag.metrics.calculator import MetricCalculator
from asag.metrics.results import MetricResult

# -- Schema --------------------------------------------------------------------
from asag.schema.records import QuestionRecord, AnswerRecord, PerturbationRecord

__all__ = [
    # Version
    "__version__",
    # Evaluation
    "EvaluationEngine",
    "EvaluationResult",
    # Perturbations
    "PerturbationEngine",
    # Graders
    "GraderInterface",
    "GradeResult",
    "HybridGrader",
    "LLMGrader",
    # Loaders
    "SemEval2013Loader",
    # Metrics
    "MetricCalculator",
    "MetricResult",
    # Schema
    "QuestionRecord",
    "AnswerRecord",
    "PerturbationRecord",
]
