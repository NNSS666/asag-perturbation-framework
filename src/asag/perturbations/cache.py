"""
Hash-keyed JSONL cache for perturbation generation results.

Each cache entry stores a list of candidate perturbed texts keyed by a
16-character MD5 hex digest of (answer_text, perturb_type, seed). The cache
is loaded into memory at init time and written incrementally (streaming append)
to avoid full-file rewrites.

If `cache_dir` is None, all operations are no-ops — get() returns None and
put() is a silent skip. This mode is used by unit tests to ensure self-contained,
reproducible test runs without touching disk.

Cache file: `{cache_dir}/perturbation_cache.jsonl`
Format: one JSON object per line: {"key": "...", "candidates": [...]}
"""

import hashlib
import json
from pathlib import Path
from typing import Dict, List, Optional


class PerturbationCache:
    """Hash-keyed JSONL cache for perturbation results.

    Cache key: MD5 hash of JSON-encoded (answer_text, perturb_type, seed).
    Each entry stores a list of candidate perturbed texts.

    Args:
        cache_dir: Directory for cache files. None = caching disabled (for unit tests).
    """

    _CACHE_FILENAME = "perturbation_cache.jsonl"

    def __init__(self, cache_dir: Optional[Path] = None) -> None:
        self._cache_dir = Path(cache_dir) if cache_dir is not None else None
        self._store: Dict[str, List[str]] = {}

        if self._cache_dir is not None:
            self._cache_dir.mkdir(parents=True, exist_ok=True)
            self._cache_path = self._cache_dir / self._CACHE_FILENAME
            self._load()
        else:
            self._cache_path = None

    def _load(self) -> None:
        """Load existing cache entries from disk into in-memory dict."""
        if self._cache_path is None or not self._cache_path.exists():
            return

        with self._cache_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    key = entry["key"]
                    candidates = entry["candidates"]
                    self._store[key] = candidates
                except (json.JSONDecodeError, KeyError):
                    # Skip malformed entries — partial writes during crash
                    continue

    def get(self, answer_text: str, perturb_type: str, seed: int) -> Optional[List[str]]:
        """Return cached candidates or None if not cached.

        Args:
            answer_text:  The original student answer text.
            perturb_type: Canonical perturbation type string.
            seed:         The per-answer seed used during generation.

        Returns:
            List of perturbed text strings, or None if not in cache.
        """
        if self._cache_dir is None:
            return None
        key = self._make_key(answer_text, perturb_type, seed)
        return self._store.get(key)

    def put(self, answer_text: str, perturb_type: str, seed: int, candidates: List[str]) -> None:
        """Store candidates in cache.

        Writes to in-memory dict AND appends to JSONL file (streaming append,
        not full rewrite). If caching is disabled (cache_dir=None), this is a no-op.

        Args:
            answer_text:  The original student answer text.
            perturb_type: Canonical perturbation type string.
            seed:         The per-answer seed used during generation.
            candidates:   List of perturbed text strings to cache.
        """
        if self._cache_dir is None:
            return

        key = self._make_key(answer_text, perturb_type, seed)
        self._store[key] = candidates

        entry = {"key": key, "candidates": candidates}
        with self._cache_path.open("a", encoding="utf-8") as f:  # type: ignore[arg-type]
            f.write(json.dumps(entry))
            f.write("\n")

    @staticmethod
    def _make_key(answer_text: str, perturb_type: str, seed: int) -> str:
        """16-char MD5 hex cache key from (text, type, seed).

        Args:
            answer_text:  The original student answer text.
            perturb_type: Canonical perturbation type string.
            seed:         The per-answer seed.

        Returns:
            16-character lowercase hex string.
        """
        payload = json.dumps(
            {"text": answer_text, "type": perturb_type, "seed": seed},
            sort_keys=True,
        )
        return hashlib.md5(payload.encode("utf-8")).hexdigest()[:16]
