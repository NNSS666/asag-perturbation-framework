"""
Convert OpenAI Batch API output to our grade cache JSONL format.

The batch output contains responses keyed by content hash (custom_id).
This script matches them back to the original requests and writes the
grade cache in the same format used by run_llm_experiments.py.

Usage:
    PYTHONPATH=src python3 -m scripts.convert_batch_results runs/batch_output/llm_openai_gpt-5.4-mini_level1.jsonl
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

from asag.loaders import SemEval2013Loader
from asag.perturbations import PerturbationEngine
from asag.schema import AnswerRecord, QuestionRecord
from asag.schema.grade import LABEL_TO_SCORE

# Fuzzy aliases — must match llm.py
_LABEL_ALIASES: Dict[str, str] = {
    "correct": "correct",
    "partially correct": "partially_correct_incomplete",
    "partially_correct": "partially_correct_incomplete",
    "partially_correct_incomplete": "partially_correct_incomplete",
    "partial": "partially_correct_incomplete",
    "contradictory": "contradictory",
    "incorrect": "contradictory",
    "wrong": "contradictory",
    "irrelevant": "irrelevant",
    "off-topic": "irrelevant",
    "off topic": "irrelevant",
    "non_domain": "non_domain",
    "non domain": "non_domain",
    "out of domain": "non_domain",
}

CACHE_DIR = Path("runs") / "llm_grade_caches"


def _parse_llm_response(raw_text: str) -> Tuple[str, float, float]:
    """Parse LLM JSON response into (label, score, confidence).

    Returns:
        Tuple of (canonical_label, score_0_to_1, confidence).

    Raises:
        ValueError: If the response cannot be parsed.
    """
    raw_text = raw_text.strip()

    # Try direct JSON parse
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError:
        # Try extracting JSON from markdown code block
        if "```" in raw_text:
            for block in raw_text.split("```"):
                block = block.strip()
                if block.startswith("json"):
                    block = block[4:].strip()
                try:
                    data = json.loads(block)
                    break
                except json.JSONDecodeError:
                    continue
            else:
                raise ValueError(f"Cannot parse response: {raw_text[:200]}")
        else:
            raise ValueError(f"Cannot parse response: {raw_text[:200]}")

    label_raw = data.get("label", "").strip().lower()
    confidence = float(data.get("confidence", 0.5))

    label = _LABEL_ALIASES.get(label_raw)
    if label is None:
        raise ValueError(f"Unknown label: {label_raw}")

    score = LABEL_TO_SCORE[label]
    return label, score, confidence


def convert(batch_output_path: str) -> None:
    """Convert batch output JSONL to grade cache JSONL."""
    batch_path = Path(batch_output_path)
    if not batch_path.exists():
        print(f"ERROR: File not found: {batch_path}")
        sys.exit(1)

    # Infer grader name from filename (e.g. llm_openai_gpt-5.4-mini_level1)
    grader_name = batch_path.stem
    cache_path = CACHE_DIR / f"{grader_name}.jsonl"

    print(f"Converting {batch_path.name} -> {cache_path.name}")

    # Load data to build hash -> (question, student_answer, ref) mapping
    print("Loading Beetle corpus...")
    questions, answers = SemEval2013Loader("beetle").load()
    engine = PerturbationEngine(seed=42)
    perturbations, _ = engine.generate_all(answers, questions)

    answer_lookup: Dict[str, AnswerRecord] = {a.answer_id: a for a in answers}
    question_lookup: Dict[str, QuestionRecord] = {
        q.question_id: q for q in questions
    }

    # Build hash -> (question, student_answer, ref) mapping
    hash_to_key: Dict[str, Tuple[str, str, str]] = {}

    for pert in perturbations:
        answer = answer_lookup.get(pert.answer_id)
        if answer is None:
            continue
        q = question_lookup.get(answer.question_id)
        if q is None:
            continue
        ref = q.reference_answers[0] if q.reference_answers else ""
        raw = f"{q.prompt}|||{pert.text}|||{ref}"
        h = hashlib.md5(raw.encode()).hexdigest()
        hash_to_key[h] = (q.prompt, pert.text, ref)

    for answer in answers:
        q = question_lookup.get(answer.question_id)
        if q is None:
            continue
        ref = q.reference_answers[0] if q.reference_answers else ""
        raw = f"{q.prompt}|||{answer.student_answer}|||{ref}"
        h = hashlib.md5(raw.encode()).hexdigest()
        hash_to_key[h] = (q.prompt, answer.student_answer, ref)

    print(f"  Hash map: {len(hash_to_key):,} entries")

    # Load existing cache to avoid duplicates
    existing_hashes = set()
    if cache_path.exists():
        with open(cache_path, "r") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                    raw = f"{row['question']}|||{row['student_answer']}|||{row['ref']}"
                    existing_hashes.add(hashlib.md5(raw.encode()).hexdigest())
                except (json.JSONDecodeError, KeyError):
                    pass
        print(f"  Existing cache: {len(existing_hashes):,} entries")

    # Parse batch results
    converted = 0
    errors = 0
    skipped = 0

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_path, "a", encoding="utf-8") as cache_file:
        with open(batch_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                result = json.loads(line)
                custom_id = result["custom_id"]

                # Skip if already in cache
                if custom_id in existing_hashes:
                    skipped += 1
                    continue

                # Find the original key
                key_tuple = hash_to_key.get(custom_id)
                if key_tuple is None:
                    errors += 1
                    continue

                question, student_answer, ref = key_tuple

                # Extract LLM response
                response = result.get("response", {})
                if response.get("status_code") != 200:
                    errors += 1
                    continue

                raw_content = response["body"]["choices"][0]["message"]["content"]

                try:
                    label, score, confidence = _parse_llm_response(raw_content)
                except ValueError:
                    errors += 1
                    continue

                # Write to cache
                row = {
                    "question": question,
                    "student_answer": student_answer,
                    "ref": ref,
                    "label": label,
                    "score": score,
                    "confidence": confidence,
                }
                cache_file.write(json.dumps(row, ensure_ascii=False) + "\n")
                converted += 1

    print(f"\n  Converted: {converted:,}")
    print(f"  Skipped (already cached): {skipped:,}")
    print(f"  Errors: {errors:,}")
    print(f"  Cache: {cache_path}")

    print(f"\nNext: run evaluation with cached grades:")
    print(f"  PYTHONPATH=src python3 -m scripts.run_llm_experiments --models {grader_name.split('_')[2]} --levels {grader_name[-1]} --resume")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert batch output to grade cache.")
    parser.add_argument("batch_output", help="Path to batch output JSONL file")
    args = parser.parse_args()
    convert(args.batch_output)
