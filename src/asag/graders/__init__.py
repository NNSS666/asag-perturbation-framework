"""
asag.graders — Grader implementations and shared interface.

Re-exports the public GraderInterface and GradeResult so callers can use:
    from asag.graders import GraderInterface, GradeResult
"""

from asag.graders.base import GradeResult, GraderInterface

__all__ = [
    "GraderInterface",
    "GradeResult",
]
