"""
asag.evaluation — EvaluationEngine and result models for ASAG robustness evaluation.

Re-exports the public EvaluationEngine and EvaluationResult so callers can use:
    from asag.evaluation import EvaluationEngine, EvaluationResult
"""

from asag.evaluation.engine import EvaluationEngine, EvaluationResult

__all__ = [
    "EvaluationEngine",
    "EvaluationResult",
]
