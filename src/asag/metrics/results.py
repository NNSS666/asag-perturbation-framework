"""
Pydantic models for metric computation results.

MetricResult captures the output of computing one family of metrics
(invariance / sensitivity / gaming) for one (grader, protocol) combination.

MetricSuite bundles all family results for a single (grader, protocol) run,
making it easy to serialize the complete evaluation output to JSONL.

Design principles:
  - All models are frozen (immutable after construction)
  - Optional float fields are None when the metric is not applicable for the family
  - by_type holds per-perturbation-type breakdowns keyed by type string
  - Python 3.9 compatible: uses typing.Dict, List, Optional
"""

from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict


class MetricResult(BaseModel):
    """Metric values for one perturbation family from one (grader, protocol) run.

    Fields:
        grader_name:      Identifier of the grader that produced the scores.
        protocol:         Evaluation protocol: "A" (LOQO) or "B" (within-question).
        family:           Perturbation family: "invariance", "sensitivity", or "gaming".
        n_pairs:          Number of (original_score, perturbed_score) pairs evaluated.
        ivr_flip:         Invariance Violation Rate (binary flip). None if not applicable.
        ivr_absdelta:     Invariance Violation Rate (mean absolute delta). None if not applicable.
        ssr_directional:  Sensitivity Success Rate (directional). None if not applicable.
        asr_thresholded:  Adversarial Success Rate (threshold crossing). None if not applicable.
        by_type:          Per-perturbation-type breakdown. Keys are type strings (e.g.
                          "synonym_substitution"), values are dicts of metric_name -> value.
    """

    model_config = ConfigDict(frozen=True)

    grader_name: str
    protocol: str
    family: str
    n_pairs: int
    ivr_flip: Optional[float] = None
    ivr_absdelta: Optional[float] = None
    ssr_directional: Optional[float] = None
    asr_thresholded: Optional[float] = None
    by_type: Dict[str, Dict[str, float]] = {}


class MetricSuite(BaseModel):
    """Container for all family MetricResults from one (grader, protocol) combination.

    Fields:
        grader_name: Identifier of the grader.
        protocol:    Evaluation protocol: "A" or "B".
        results:     List of MetricResult, one per perturbation family evaluated.
    """

    model_config = ConfigDict(frozen=True)

    grader_name: str
    protocol: str
    results: List[MetricResult]
