"""
MetricCalculator — all four dual-form metric variants.

Implements the four metrics at the core of the ASAG robustness evaluation:

  IVR_flip      — Invariance Violation Rate (binary): proportion of invariance
                  pairs where ANY score change occurred.
  IVR_absdelta  — Invariance Violation Rate (continuous): mean absolute score
                  delta across all invariance pairs.
  SSR_directional — Sensitivity Success Rate (directional): proportion of
                  sensitivity pairs where the perturbed score DECREASED.
  ASR_thresholded — Adversarial Success Rate (threshold-crossing): proportion
                  of gaming pairs where the score crossed from below the passing
                  threshold (orig < 0.5) to at or above it (pert >= 0.5).

Design decisions (from RESEARCH.md):
  - Pitfall 1: Scores are rounded to SCORE_PRECISION decimals before float
    comparison. This prevents false positives from IEEE 754 representation
    errors (e.g. 0.1 + 0.2 != 0.3).
  - Pitfall 6: SSR_directional uses strict less-than (pert < orig). No-change
    counts as FAILURE — semantically correct because a sensitivity perturbation
    that doesn't change the score means the grader missed the perturbation.
  - ASR_thresholded: "crossing the threshold" definition — orig must be BELOW
    the passing threshold and pert must be AT OR ABOVE. Already-passing answers
    that increase further are NOT counted (that's just a score increase, not
    gaming). PASSING_THRESHOLD = 0.5 (normalized scale).

All metric methods return float('nan') on empty input, not 0.0, to distinguish
"no pairs evaluated" from "all pairs passed the criterion".

Python 3.9 compatible: uses typing.Dict, List, Tuple.
"""

import math
from typing import Dict, List, Tuple

# Type alias: (original_score, perturbed_score)
ScorePair = Tuple[float, float]


class MetricCalculator:
    """Computes all four dual-form robustness metrics.

    All metric methods accept a list of ScorePair = (orig_score, pert_score)
    and return a float in [0.0, 1.0] (proportion) or float('nan') on empty.

    Usage:
        calc = MetricCalculator()
        pairs = [(1.0, 1.0), (1.0, 0.5), (0.5, 0.5)]
        ivr = calc.ivr_flip(pairs)   # 0.333...
    """

    PASSING_THRESHOLD: float = 0.5
    SCORE_PRECISION: int = 6

    def _round(self, score: float) -> float:
        """Round score to SCORE_PRECISION decimals to prevent IEEE 754 pitfalls.

        This is the fix for RESEARCH.md Pitfall 1: floating-point equality
        comparisons on raw scores can produce false positives (e.g. 0.1 + 0.2
        technically differs from 0.3 in IEEE 754). Rounding to 6 decimal places
        is fine-grained enough to distinguish all practically meaningful score
        differences (scores are normalized to [0.0, 1.0]).

        Args:
            score: Raw float score to round.

        Returns:
            Score rounded to SCORE_PRECISION decimal places.
        """
        return round(score, self.SCORE_PRECISION)

    def ivr_flip(self, pairs: List[ScorePair]) -> float:
        """Invariance Violation Rate — binary (flip) variant.

        Computes the proportion of invariance perturbation pairs where ANY
        score change occurred. A "flip" is defined as:
            round(orig, 6) != round(pert, 6)

        Locked decision: ANY change counts as a violation, regardless of
        direction or magnitude. This is the strictest invariance criterion.

        Args:
            pairs: List of (original_score, perturbed_score) tuples.

        Returns:
            Proportion in [0.0, 1.0] of pairs where a flip occurred.
            Returns float('nan') if pairs is empty.

        Example:
            calc.ivr_flip([(1.0, 1.0), (1.0, 0.5)]) == 0.5
        """
        if not pairs:
            return float("nan")
        flips = sum(
            1 for orig, pert in pairs if self._round(orig) != self._round(pert)
        )
        return flips / len(pairs)

    def ivr_absdelta(self, pairs: List[ScorePair]) -> float:
        """Invariance Violation Rate — continuous (mean absolute delta) variant.

        Computes the mean absolute difference between original and perturbed
        scores across all invariance perturbation pairs. Unlike IVR_flip, this
        captures the magnitude of violations, not just their presence.

        Args:
            pairs: List of (original_score, perturbed_score) tuples.

        Returns:
            Mean absolute delta in [0.0, 1.0].
            Returns float('nan') if pairs is empty.

        Example:
            calc.ivr_absdelta([(1.0, 0.5), (1.0, 1.0)]) == 0.25
        """
        if not pairs:
            return float("nan")
        total_delta = sum(abs(orig - pert) for orig, pert in pairs)
        return total_delta / len(pairs)

    def ssr_directional(self, pairs: List[ScorePair]) -> float:
        """Sensitivity Success Rate — directional variant.

        Computes the proportion of sensitivity perturbation pairs where the
        perturbed score STRICTLY DECREASED compared to the original:
            pert < orig

        Design decision (RESEARCH.md Pitfall 6):
            No-change counts as FAILURE. A sensitivity perturbation should
            cause the grade to decrease. If the grade stays the same, the
            grader failed to detect the perturbation — a negative result.

        Args:
            pairs: List of (original_score, perturbed_score) tuples.

        Returns:
            Proportion in [0.0, 1.0] of pairs where pert < orig.
            Returns float('nan') if pairs is empty.

        Example:
            calc.ssr_directional([(1.0, 0.0), (1.0, 1.0)]) == 0.5
        """
        if not pairs:
            return float("nan")
        successes = sum(1 for orig, pert in pairs if pert < orig)
        return successes / len(pairs)

    def asr_thresholded(self, pairs: List[ScorePair]) -> float:
        """Adversarial Success Rate — threshold-crossing variant.

        Computes the proportion of gaming perturbation pairs where the score
        CROSSED the passing threshold: orig was below threshold AND pert is
        at or above threshold.

        Passing threshold: PASSING_THRESHOLD = 0.5 (normalized scale).

        Criterion:
            orig < PASSING_THRESHOLD AND pert >= PASSING_THRESHOLD

        This is the "gaming" definition: the student answer originally failed
        (below threshold) and the adversarial perturbation caused it to pass
        (at or above threshold). Already-passing answers that increase further
        are NOT counted — that's a score increase, not adversarial gaming.

        Args:
            pairs: List of (original_score, perturbed_score) tuples.

        Returns:
            Proportion in [0.0, 1.0] of pairs that crossed the threshold.
            Returns float('nan') if pairs is empty.

        Example:
            # Crosses threshold: 0.0 -> 0.5 = success
            # Already passing: 0.5 -> 1.0 = not counted
            # Stays failing: 0.0 -> 0.0 = not counted
            calc.asr_thresholded([(0.0, 0.5), (0.5, 1.0), (0.0, 0.0)]) == 1/3
        """
        if not pairs:
            return float("nan")
        crossings = sum(
            1
            for orig, pert in pairs
            if orig < self.PASSING_THRESHOLD and pert >= self.PASSING_THRESHOLD
        )
        return crossings / len(pairs)

    def compute_by_type(
        self,
        grade_pairs: List[Tuple[str, str, float, float]],
        family: str,
    ) -> Dict[str, Dict[str, float]]:
        """Compute per-perturbation-type metric breakdown.

        Groups score pairs by perturbation type and computes the appropriate
        metric(s) for the given perturbation family.

        Metrics computed per family:
          - "invariance": ivr_flip + ivr_absdelta
          - "sensitivity": ssr_directional
          - "gaming":     asr_thresholded

        Args:
            grade_pairs: List of (answer_id, perturb_type, orig_score, pert_score)
                         tuples. answer_id is included for debugging but not used
                         in the computation.
            family:      Perturbation family: "invariance", "sensitivity", or "gaming".

        Returns:
            Dict[perturb_type, Dict[metric_name, value]].
            For example, for "invariance":
                {
                    "synonym_substitution": {"ivr_flip": 0.2, "ivr_absdelta": 0.1},
                    "surface_rewrite":      {"ivr_flip": 0.5, "ivr_absdelta": 0.3},
                }

        Raises:
            ValueError: If family is not one of the three recognized values.
        """
        if family not in ("invariance", "sensitivity", "gaming"):
            raise ValueError(
                f"Unknown family {family!r}. "
                "Expected 'invariance', 'sensitivity', or 'gaming'."
            )

        # Group pairs by perturbation type
        by_type: Dict[str, List[ScorePair]] = {}
        for _answer_id, perturb_type, orig_score, pert_score in grade_pairs:
            if perturb_type not in by_type:
                by_type[perturb_type] = []
            by_type[perturb_type].append((orig_score, pert_score))

        result: Dict[str, Dict[str, float]] = {}

        for perturb_type, pairs in by_type.items():
            if family == "invariance":
                result[perturb_type] = {
                    "ivr_flip": self.ivr_flip(pairs),
                    "ivr_absdelta": self.ivr_absdelta(pairs),
                }
            elif family == "sensitivity":
                result[perturb_type] = {
                    "ssr_directional": self.ssr_directional(pairs),
                }
            elif family == "gaming":
                result[perturb_type] = {
                    "asr_thresholded": self.asr_thresholded(pairs),
                }

        return result
