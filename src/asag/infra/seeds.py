"""
Per-component seed management for reproducible multi-seed experiments.

Seed isolation philosophy:
  Each pipeline component (splitter, perturbation generator, model trainer)
  receives its own seed through a dedicated parameter (e.g., random_state=seed).
  This means changing the training seed does NOT affect how the data was split
  or how perturbations were sampled — enabling controlled ablations.

  Global seed setters (set_global_seeds, set_split_seeds) are provided as a
  fallback for libraries that do not expose a random_state parameter. They
  should be called immediately before the relevant operation, not at program
  start — this preserves independence between components.

  SeedConfig holds all per-component seeds in one place so the full
  randomization configuration can be logged to config.json alongside the
  rest of the experiment setup.
"""

import random

import numpy

from pydantic import BaseModel


class SeedConfig(BaseModel):
    """Per-component seed configuration for reproducible experiments.

    All fields default to 42 but are independently variable. In a multi-seed
    experiment you would vary one field while keeping the others fixed:

        SeedConfig(split_seed=42, perturb_seed=123, train_seed=456)

    This ensures that varying the training seed does not affect splitting or
    perturbation, making results directly comparable across seeds.

    Fields:
        split_seed:   Controls Protocol A/B train/test splitting.
        perturb_seed: Controls perturbation generation (sampling, LLM temperature
                      is fixed at 0 but order-dependent operations use this seed).
        train_seed:   Controls model weight initialization and mini-batch ordering.
    """

    split_seed: int = 42
    perturb_seed: int = 42
    train_seed: int = 42


def set_global_seeds(seed: int) -> None:
    """Set random seeds for all available libraries.

    Sets random, numpy, and (if installed) torch seeds. Use this before
    any operation that should be fully deterministic across all libraries.

    For component-isolated randomness, prefer set_split_seeds() or passing
    the seed as a random_state argument directly to the component.

    Args:
        seed: Integer seed value to set across all libraries.
    """
    random.seed(seed)
    numpy.random.seed(seed)
    try:
        import torch  # type: ignore[import]

        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
    except ImportError:
        pass  # torch not installed in Phase 1 — skip silently


def set_split_seeds(seed: int) -> None:
    """Set random seeds for split-related libraries only.

    Sets random and numpy seeds without touching torch — use this immediately
    before calling a splitter to ensure reproducible train/test splits while
    leaving the training seed unaffected.

    Args:
        seed: Integer seed value for random and numpy.
    """
    random.seed(seed)
    numpy.random.seed(seed)
