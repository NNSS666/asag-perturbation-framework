"""
Shared pytest configuration for the ASAG test suite.

Tests are run with PYTHONPATH=src so that `from asag.xxx import ...` works
without installing the package. Fixtures shared across all test modules are
collected here; module-specific fixtures live in the test modules themselves.
"""

# All shared fixtures are imported from their respective modules via conftest
# plugin discovery. Module-level fixtures in tests/metrics/synthetic_mini_dataset.py
# are automatically discovered by pytest when conftest.py imports them.

from tests.metrics.synthetic_mini_dataset import (
    invariance_pairs,
    sensitivity_pairs,
    gaming_pairs,
    grade_pairs_for_by_type,
    synthetic_questions,
    synthetic_answers,
    synthetic_perturbations,
)

__all__ = [
    "invariance_pairs",
    "sensitivity_pairs",
    "gaming_pairs",
    "grade_pairs_for_by_type",
    "synthetic_questions",
    "synthetic_answers",
    "synthetic_perturbations",
]
