"""
asag.graders — Grader implementations and shared interface.

Re-exports the public GraderInterface and GradeResult so callers can use:
    from asag.graders import GraderInterface, GradeResult

Also re-exports concrete grader implementations:
    from asag.graders import HybridGrader
"""

from asag.graders.base import GradeResult, GraderInterface
from asag.graders.hybrid import HybridGrader
from asag.graders.llm import LLMGrader

__all__ = [
    "GraderInterface",
    "GradeResult",
    "HybridGrader",
    "LLMGrader",
]
