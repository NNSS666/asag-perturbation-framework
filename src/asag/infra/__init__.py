"""
Reproducibility infrastructure for ASAG experiments.

Provides:
  - JSON-based storage for Pydantic records (JSONL) and config dicts
  - Auto-named run directory creation (timestamp + corpus + seed)
  - Library version capture using importlib.metadata
  - Per-component seed management with SeedConfig
  - Experiment configuration logging with ExperimentConfig

All public symbols are re-exported here for convenient access:

    from asag.infra import save_records, load_records, ExperimentConfig, ...
"""

from .storage import load_json, load_records, save_json, save_records
from .seeds import SeedConfig, set_global_seeds, set_split_seeds
from .run_dir import make_run_dir
from .versions import get_library_versions
from .config import ExperimentConfig, load_run_config, save_run_config

__all__ = [
    # storage
    "save_records",
    "load_records",
    "save_json",
    "load_json",
    # seeds
    "SeedConfig",
    "set_global_seeds",
    "set_split_seeds",
    # run directory
    "make_run_dir",
    # versions
    "get_library_versions",
    # experiment config
    "ExperimentConfig",
    "save_run_config",
    "load_run_config",
]
