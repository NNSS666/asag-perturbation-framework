"""
Auto-named run directory creation for experiment traceability.

Every experiment run gets a uniquely-named directory that encodes when it
ran, which corpus it used, and what seed controlled the split. This makes
it trivial to identify runs from directory listings alone.

Naming convention (per CONTEXT.md):
    runs/2026-02-20_14-30_beetle_seed42/

The directory is created with exist_ok=False to prevent silent overwrites
of previous results. If two runs start within the same minute they will
produce different names only if the corpus or seed differ — this is
intentional: same-minute reruns should be distinguished by changing the
seed, not by timestamp alone.
"""

from datetime import datetime
from pathlib import Path


def make_run_dir(base: Path, corpus: str, seed: int) -> Path:
    """Create and return a uniquely-named run directory.

    The directory name follows the pattern:
        {YYYY-MM-DD_HH-MM}_{corpus}_seed{seed}

    Example:
        make_run_dir(Path("runs"), "beetle", 42)
        # Creates: runs/2026-02-20_14-30_beetle_seed42/

    Args:
        base:   Parent directory under which the run directory is created.
                Typically Path("runs") relative to the project root.
        corpus: Dataset name (e.g. "beetle", "scientsbank").
        seed:   Split seed used for this run (from SeedConfig.split_seed).

    Returns:
        Path to the newly created run directory.

    Raises:
        FileExistsError: If the run directory already exists (prevents
                         overwriting previous results).
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    run_name = f"{timestamp}_{corpus}_seed{seed}"
    run_dir = Path(base) / run_name
    run_dir.mkdir(parents=True, exist_ok=False)
    return run_dir
