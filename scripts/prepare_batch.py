"""
Prepare OpenAI Batch API JSONL files for remaining LLM configurations.

Generates one JSONL file per config, ready to upload to OpenAI Batch API.
Each line is a request with custom_id that encodes the cache key for later
reconstruction.

Usage:
    PYTHONPATH=src python3 -m scripts.prepare_batch
    PYTHONPATH=src python3 -m scripts.prepare_batch --models gpt-5.4-mini --levels 1
    PYTHONPATH=src python3 -m scripts.prepare_batch --skip-existing

After running, upload each file to OpenAI:
    PYTHONPATH=src python3 -m scripts.submit_batch runs/batch_input/llm_openai_gpt-5.4-mini_level1.jsonl
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

from asag.loaders import SemEval2013Loader
from asag.perturbations import PerturbationEngine
from asag.schema import AnswerRecord, PerturbationRecord, QuestionRecord

# ---------------------------------------------------------------------------
# Prompts — must match llm.py exactly
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = (
    "You are an expert educational assessor grading student answers to science questions. "
    "You must classify each student answer into exactly one of these categories:\n"
    "- correct: The answer fully addresses the question with accurate information.\n"
    "- partially_correct_incomplete: The answer is partially correct but missing key concepts.\n"
    "- contradictory: The answer contradicts the expected correct answer.\n"
    "- irrelevant: The answer is off-topic and does not address the question.\n"
    "- non_domain: The answer is outside the subject domain entirely.\n\n"
    "Respond with ONLY a JSON object in this exact format:\n"
    '{"label": "<one of the five labels above>", "confidence": <float between 0.0 and 1.0>}\n'
    "Do not include any other text."
)

_USER_PROMPT_LEVEL0 = (
    "Question: {question}\n\n"
    "Student answer: {student_answer}\n\n"
    "Classify the student answer."
)

_USER_PROMPT_LEVEL1 = (
    "Question: {question}\n\n"
    "Reference answer (correct): {reference_answer}\n\n"
    "Student answer: {student_answer}\n\n"
    "Classify the student answer by comparing it to the reference answer."
)

# ---------------------------------------------------------------------------
# Configurations
# ---------------------------------------------------------------------------

OPENAI_CONFIGS: List[Tuple[str, int]] = [
    ("gpt-5.4-mini", 1),
    ("gpt-5.4", 0),
    ("gpt-5.4", 1),
]

BATCH_INPUT_DIR = Path("runs") / "batch_input"
CACHE_DIR = Path("runs") / "llm_grade_caches"


def _grader_name(model: str, level: int) -> str:
    return f"llm_openai_{model}_level{level}"


def _load_existing_cache_keys(grader_name: str) -> Set[str]:
    """Load custom_ids already graded (from previous sync runs)."""
    cache_path = CACHE_DIR / f"{grader_name}.jsonl"
    if not cache_path.exists():
        return set()

    keys = set()
    with open(cache_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
                # Reconstruct the same hash we use for custom_id
                raw = f"{row['question']}|||{row['student_answer']}|||{row['ref']}"
                keys.add(hashlib.md5(raw.encode()).hexdigest())
            except (json.JSONDecodeError, KeyError):
                pass
    return keys


def prepare_requests(
    model: str,
    level: int,
    questions: List[QuestionRecord],
    answers: List[AnswerRecord],
    perturbations: List[PerturbationRecord],
    skip_existing: bool = False,
) -> Tuple[Path, int]:
    """Generate a JSONL batch input file for one (model, level) config.

    Returns:
        Tuple of (output_path, request_count).
    """
    grader_name = _grader_name(model, level)
    output_path = BATCH_INPUT_DIR / f"{grader_name}.jsonl"

    answer_lookup: Dict[str, AnswerRecord] = {a.answer_id: a for a in answers}
    question_lookup: Dict[str, QuestionRecord] = {
        q.question_id: q for q in questions
    }

    # Collect all unique (question, student_answer, ref) triples
    seen: Set[str] = set()
    requests: List[Dict] = []

    # Load existing cache to skip already-graded
    existing_keys: Set[str] = set()
    if skip_existing:
        existing_keys = _load_existing_cache_keys(grader_name)
        if existing_keys:
            print(f"  Skipping {len(existing_keys)} already-graded entries")

    def _add_request(question_text: str, student_answer: str, ref_answer: str) -> None:
        # Deterministic ID from content
        raw = f"{question_text}|||{student_answer}|||{ref_answer}"
        content_hash = hashlib.md5(raw.encode()).hexdigest()

        if content_hash in seen:
            return
        seen.add(content_hash)

        if content_hash in existing_keys:
            return

        # Build prompt
        if level == 0:
            user_prompt = _USER_PROMPT_LEVEL0.format(
                question=question_text,
                student_answer=student_answer,
            )
        else:
            user_prompt = _USER_PROMPT_LEVEL1.format(
                question=question_text,
                reference_answer=ref_answer,
                student_answer=student_answer,
            )

        request = {
            "custom_id": content_hash,
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": model,
                "messages": [
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.0,
                "max_completion_tokens": 100,
                "seed": 42,
            },
        }
        requests.append(request)

    # Add all perturbations
    for pert in perturbations:
        answer = answer_lookup.get(pert.answer_id)
        if answer is None:
            continue
        q = question_lookup.get(answer.question_id)
        if q is None:
            continue
        ref = q.reference_answers[0] if q.reference_answers else ""
        _add_request(q.prompt, pert.text, ref)

    # Add all original answers
    for answer in answers:
        q = question_lookup.get(answer.question_id)
        if q is None:
            continue
        ref = q.reference_answers[0] if q.reference_answers else ""
        _add_request(q.prompt, answer.student_answer, ref)

    # Write JSONL
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for req in requests:
            f.write(json.dumps(req, ensure_ascii=False) + "\n")

    return output_path, len(requests)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Prepare OpenAI Batch API JSONL files."
    )
    parser.add_argument(
        "--models", nargs="+", default=None,
        help="Filter by model ID (e.g. gpt-5.4-mini gpt-5.4)"
    )
    parser.add_argument(
        "--levels", nargs="+", type=int, default=None,
        help="Filter by level (0, 1)"
    )
    parser.add_argument(
        "--skip-existing", action="store_true",
        help="Skip entries already in the grade cache"
    )
    args = parser.parse_args()

    # Filter configs
    configs = OPENAI_CONFIGS
    if args.models:
        configs = [(m, l) for m, l in configs if m in args.models]
    if args.levels:
        configs = [(m, l) for m, l in configs if l in args.levels]

    if not configs:
        print("No configurations match filters.")
        sys.exit(1)

    print("Loading Beetle corpus...")
    questions, answers = SemEval2013Loader("beetle").load()
    engine = PerturbationEngine(seed=42)
    perturbations, _ = engine.generate_all(answers, questions)
    print(f"  {len(questions)} questions, {len(answers)} answers, {len(perturbations)} perturbations\n")

    total_requests = 0
    for model, level in configs:
        grader_name = _grader_name(model, level)
        print(f"Preparing {grader_name}...")
        path, count = prepare_requests(
            model, level, questions, answers, perturbations,
            skip_existing=args.skip_existing,
        )
        print(f"  -> {path} ({count:,} requests)")
        total_requests += count

    print(f"\nTotal: {total_requests:,} requests across {len(configs)} configs")
    print(f"\nNext steps:")
    for model, level in configs:
        name = _grader_name(model, level)
        print(f"  PYTHONPATH=src python3 -m scripts.submit_batch runs/batch_input/{name}.jsonl")


if __name__ == "__main__":
    main()
