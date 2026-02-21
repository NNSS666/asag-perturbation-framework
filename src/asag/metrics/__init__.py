"""
asag.metrics — Metric computation for ASAG robustness evaluation.

Re-exports the public MetricCalculator and result models so callers can use:
    from asag.metrics import MetricCalculator, MetricResult, MetricSuite, ScorePair
"""

from asag.metrics.calculator import MetricCalculator, ScorePair
from asag.metrics.results import MetricResult, MetricSuite

__all__ = [
    "MetricCalculator",
    "ScorePair",
    "MetricResult",
    "MetricSuite",
]
