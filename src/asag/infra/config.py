"""
Experiment configuration logging for full run reproducibility.

ExperimentConfig captures all configuration that affects experimental results:
  - Which corpus to use
  - Per-component seeds (split, perturbation, training)
  - Which evaluation protocol(s) to run
  - Phase-specific hyperparameters (model name, learning rate, etc.)

save_run_config writes this together with library versions and a timestamp
to config.json in the run directory. This single file is sufficient to
identify exactly what ran, when, and with what libraries — enabling future
reproduction of any experiment.

Usage:
    config = ExperimentConfig(corpus="beetle", seeds=SeedConfig(split_seed=42))
    run_dir = make_run_dir(Path("runs"), "beetle", config.seeds.split_seed)
    save_run_config(run_dir, config)
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel

from .seeds import SeedConfig
from .storage import load_json, save_json
from .versions import get_library_versions


class ExperimentConfig(BaseModel):
    """Full experiment configuration for one pipeline run.

    All fields except corpus and seeds have sensible defaults so that
    simple experiments can be created with minimal boilerplate.

    Fields:
        corpus:      Dataset name, e.g. "beetle" or "scientsbank".
        seeds:       Per-component seed configuration (split, perturb, train).
        protocol:    Evaluation protocol(s) to run:
                     "A" — LOQO cross-question generalization only.
                     "B" — within-question in-distribution only.
                     "both" — run both protocols side-by-side (default).
        description: Free-text note about this experiment's purpose.
        extra:       Catch-all dict for phase-specific hyperparameters such as
                     model name, learning rate, perturbation budget, etc.
                     These are logged as-is and not validated — use explicit
                     fields if a parameter affects pipeline branching logic.
    """

    corpus: str
    seeds: SeedConfig = SeedConfig()
    protocol: Literal["A", "B", "both"] = "both"
    description: Optional[str] = None
    extra: Dict[str, Any] = {}


def save_run_config(run_dir: Path, config: ExperimentConfig) -> Path:
    """Write experiment config + library versions + timestamp to config.json.

    The resulting file contains three top-level keys:
      - "config":           the experiment configuration (corpus, seeds, etc.)
      - "library_versions": output of get_library_versions()
      - "timestamp":        ISO-format datetime string of when config was saved

    Args:
        run_dir: The run directory created by make_run_dir().
        config:  ExperimentConfig instance to persist.

    Returns:
        Path to the written config.json file.
    """
    run_dir = Path(run_dir)
    record: Dict[str, Any] = {
        "config": config.model_dump(),
        "library_versions": get_library_versions(),
        "timestamp": datetime.now().isoformat(),
    }
    config_path = run_dir / "config.json"
    save_json(record, config_path)
    return config_path


def load_run_config(run_dir: Path) -> Dict[str, Any]:
    """Read config.json from a run directory and return it as a dict.

    Returns the raw dict (not an ExperimentConfig) because config.json also
    contains library_versions and timestamp fields not present in the model.
    Callers can reconstruct ExperimentConfig from loaded["config"] if needed:

        data = load_run_config(run_dir)
        config = ExperimentConfig(**data["config"])

    Args:
        run_dir: The run directory whose config.json should be read.

    Returns:
        Dict with "config", "library_versions", and "timestamp" keys.
    """
    return load_json(Path(run_dir) / "config.json")


if __name__ == "__main__":
    import tempfile

    from .run_dir import make_run_dir

    with tempfile.TemporaryDirectory() as td:
        config = ExperimentConfig(
            corpus="beetle",
            seeds=SeedConfig(split_seed=42, perturb_seed=123, train_seed=456),
            description="Self-test run",
            extra={"model_name": "bert-base-uncased", "learning_rate": 2e-5},
        )
        run_dir = make_run_dir(Path(td), config.corpus, config.seeds.split_seed)
        config_path = save_run_config(run_dir, config)
        loaded = load_run_config(run_dir)

        print(f"Run dir: {run_dir.name}")
        print(f"Config path: {config_path}")
        print(f"Corpus: {loaded['config']['corpus']}")
        print(f"Split seed: {loaded['config']['seeds']['split_seed']}")
        print(f"Library versions tracked: {len(loaded['library_versions'])}")
        print(f"Timestamp: {loaded['timestamp']}")
        print("ExperimentConfig self-test OK")
