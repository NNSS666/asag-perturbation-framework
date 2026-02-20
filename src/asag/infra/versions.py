"""
Library version capture for experiment reproducibility.

Records the exact version of every dependency used in a run, so that
results can be attributed to specific library versions and experiments
can be reproduced in the future.

Uses importlib.metadata (stdlib since Python 3.8) — no additional
dependencies required.
"""

import importlib.metadata
import platform
import sys
from typing import Dict, List

TRACKED_PACKAGES: List[str] = [
    "pydantic",
    "datasets",
    "scikit-learn",
    "numpy",
    "torch",
    "transformers",
    "sentence-transformers",
    "openai",
]
"""All packages whose versions are captured at run start.

Covers all phase dependencies: Phase 1 (pydantic, datasets, scikit-learn,
numpy), Phase 3 (transformers, sentence-transformers), Phase 4 (torch),
Phase 5 (openai). Packages not installed are recorded as 'not_installed'
rather than raising an error.
"""


def get_library_versions() -> Dict[str, str]:
    """Capture Python version, platform, and all tracked package versions.

    Returns a dict ready for JSON serialization. Uninstalled packages are
    recorded as "not_installed" so the output always has the same keys
    regardless of which phases' dependencies are installed.

    Returns:
        Dict mapping name -> version string (or "not_installed").
        Always includes "python" and "platform" keys.

    Example:
        {
            "python": "3.9.6 (default, ...)",
            "platform": "macOS-14.0-arm64-...",
            "pydantic": "2.5.3",
            "torch": "not_installed",
            ...
        }
    """
    versions: Dict[str, str] = {
        "python": sys.version,
        "platform": platform.platform(),
    }
    for pkg in TRACKED_PACKAGES:
        try:
            versions[pkg] = importlib.metadata.version(pkg)
        except importlib.metadata.PackageNotFoundError:
            versions[pkg] = "not_installed"
    return versions


if __name__ == "__main__":
    versions = get_library_versions()
    print(f"Captured {len(versions)} version entries:")
    for name, version in versions.items():
        print(f"  {name}: {version}")
