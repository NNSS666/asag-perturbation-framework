"""
JSON-based storage for Pydantic records and arbitrary config dicts.

Provides two storage patterns:
  - JSONL (one JSON object per line) for lists of Pydantic BaseModel records
    via save_records / load_records — enables streaming large datasets
  - Pretty-printed JSON for config files and metadata dicts
    via save_json / load_json

Design:
  - save_records uses model_dump_json() for lossless Pydantic roundtrip
  - load_records uses model_validate_json() for type-safe reconstruction
  - save_json uses default=str to handle datetime, Path, and other
    non-serializable types gracefully in config files
  - Parent directories are created automatically on write
"""

import json
from pathlib import Path
from typing import List, Type, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def save_records(records: List[BaseModel], path: Path) -> None:
    """Save a list of Pydantic model instances to a JSONL file.

    One JSON object per line. Uses model_dump_json() for lossless roundtrip.
    Parent directories are created if they do not exist.

    Args:
        records:    List of Pydantic BaseModel instances to persist.
        path:       Destination file path (will be created or overwritten).
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(record.model_dump_json())
            f.write("\n")


def load_records(path: Path, model_class: Type[T]) -> List[T]:
    """Load a list of Pydantic model instances from a JSONL file.

    Each non-empty line is parsed via model_class.model_validate_json().
    Returns a typed list of model instances.

    Args:
        path:        JSONL file path to read from.
        model_class: The Pydantic model class to deserialize into.

    Returns:
        List of model instances, one per non-empty line in the file.
    """
    path = Path(path)
    records: List[T] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(model_class.model_validate_json(line))
    return records


def save_json(data: dict, path: Path) -> None:
    """Write an arbitrary dict to a pretty-printed JSON file.

    Uses default=str to convert non-serializable types (datetime, Path, etc.)
    to their string representation — suitable for config and metadata files.

    Args:
        data:   Dict to serialize.
        path:   Destination file path (will be created or overwritten).
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


def load_json(path: Path) -> dict:
    """Read a JSON file and return its contents as a dict.

    Args:
        path:   JSON file path to read from.

    Returns:
        Parsed dict from the JSON file.
    """
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    # Self-test: roundtrip for QuestionRecord
    import tempfile
    import os
    import sys

    # Add src to path for standalone execution
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

    from asag.schema.records import QuestionRecord

    qs = [
        QuestionRecord(
            question_id="q1",
            prompt="What is X?",
            reference_answers=["X is Y"],
        ),
        QuestionRecord(
            question_id="q2",
            prompt="What is Z?",
            reference_answers=["Z is W", "Z is also V"],
        ),
        QuestionRecord(
            question_id="q3",
            prompt="What is A?",
            reference_answers=["A is B"],
            rubric_text="Focus on the definition.",
            corpus="test_corpus",
        ),
    ]

    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "test.jsonl"
        save_records(qs, p)
        loaded = load_records(p, QuestionRecord)
        assert len(loaded) == 3, f"Expected 3 records, got {len(loaded)}"
        assert loaded[0] == qs[0], "Record 0 mismatch"
        assert loaded[1].reference_answers == ["Z is W", "Z is also V"], "Record 1 mismatch"
        assert loaded[2].rubric_text == "Focus on the definition.", "Record 2 mismatch"
        print("JSONL roundtrip OK — 3 QuestionRecords saved and loaded losslessly")

        cfg_path = Path(td) / "config.json"
        save_json({"key": "value", "number": 42}, cfg_path)
        loaded_cfg = load_json(cfg_path)
        assert loaded_cfg["key"] == "value"
        assert loaded_cfg["number"] == 42
        print("JSON config roundtrip OK")
