"""
LLMGrader — Zero-shot grading via LLM API (OpenAI, Anthropic, Google).

Grades student answers by sending a structured prompt to an LLM and parsing
the response into a GradeResult. Supports two information levels:
  - Livello 0: question + student answer only (no reference)
  - Livello 1: question + student answer + reference answer

The grader does NOT require fit() — it uses zero-shot prompting. The
EvaluationEngine's _grade_single() passes reference_answer as a kwarg;
when the grader is configured for Livello 0 it simply ignores it.

Supported providers:
  - "openai"    — GPT-5.4, GPT-5.4 mini, GPT-5.4 nano, etc.
  - "anthropic" — Claude Opus/Sonnet/Haiku 4.5/4.6
  - "google"    — Gemini 2.5 Pro/Flash/Flash-Lite

Rate limiting: uses exponential backoff with configurable max_retries.

Python 3.9 compatible: uses typing.Optional/Dict/List (not X | Y syntax).
"""

import json
import logging
import time
from typing import Any, Dict, Literal, Optional

from asag.graders.base import GradeResult, GraderInterface
from asag.schema.grade import LABEL_TO_SCORE

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Score mapping — LLM outputs a label string, we map to [0, 1]
# ---------------------------------------------------------------------------

# Canonical labels the LLM is instructed to output.
# Maps to LABEL_TO_SCORE from schema/grade.py for score normalization.
_VALID_LABELS = set(LABEL_TO_SCORE.keys())

# Fuzzy aliases to handle common LLM output variations
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


# ---------------------------------------------------------------------------
# Prompt templates
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
# Provider clients — lazy-initialized
# ---------------------------------------------------------------------------

def _call_openai(
    model: str,
    system_prompt: str,
    user_prompt: str,
    temperature: float,
    max_retries: int,
) -> str:
    """Call OpenAI Chat Completions API.

    Args:
        model:         Model ID (e.g. "gpt-5.4-mini").
        system_prompt: System message content.
        user_prompt:   User message content.
        temperature:   Sampling temperature.
        max_retries:   Max retry attempts on transient errors.

    Returns:
        Raw text content of the assistant response.

    Raises:
        RuntimeError: If all retries are exhausted.
    """
    from openai import OpenAI, APIError, RateLimitError

    client = OpenAI()
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=100,
            )
            return response.choices[0].message.content.strip()
        except RateLimitError:
            wait = 2 ** attempt
            logger.warning("OpenAI rate limit hit, retrying in %ds (attempt %d/%d)", wait, attempt + 1, max_retries)
            time.sleep(wait)
        except APIError as e:
            if attempt == max_retries - 1:
                raise RuntimeError(f"OpenAI API error after {max_retries} retries: {e}") from e
            wait = 2 ** attempt
            logger.warning("OpenAI API error, retrying in %ds: %s", wait, e)
            time.sleep(wait)
    raise RuntimeError(f"OpenAI API failed after {max_retries} retries")


def _call_anthropic(
    model: str,
    system_prompt: str,
    user_prompt: str,
    temperature: float,
    max_retries: int,
) -> str:
    """Call Anthropic Messages API.

    Args:
        model:         Model ID (e.g. "claude-haiku-4-5-20251001").
        system_prompt: System message content.
        user_prompt:   User message content.
        temperature:   Sampling temperature.
        max_retries:   Max retry attempts on transient errors.

    Returns:
        Raw text content of the assistant response.

    Raises:
        RuntimeError: If all retries are exhausted.
    """
    from anthropic import Anthropic, APIError, RateLimitError

    client = Anthropic()
    for attempt in range(max_retries):
        try:
            response = client.messages.create(
                model=model,
                max_tokens=100,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
            )
            return response.content[0].text.strip()
        except RateLimitError:
            wait = 2 ** attempt
            logger.warning("Anthropic rate limit hit, retrying in %ds (attempt %d/%d)", wait, attempt + 1, max_retries)
            time.sleep(wait)
        except APIError as e:
            if attempt == max_retries - 1:
                raise RuntimeError(f"Anthropic API error after {max_retries} retries: {e}") from e
            wait = 2 ** attempt
            logger.warning("Anthropic API error, retrying in %ds: %s", wait, e)
            time.sleep(wait)
    raise RuntimeError(f"Anthropic API failed after {max_retries} retries")


def _call_google(
    model: str,
    system_prompt: str,
    user_prompt: str,
    temperature: float,
    max_retries: int,
) -> str:
    """Call Google Gemini API.

    Args:
        model:         Model ID (e.g. "gemini-2.5-flash").
        system_prompt: System instruction.
        user_prompt:   User message content.
        temperature:   Sampling temperature.
        max_retries:   Max retry attempts on transient errors.

    Returns:
        Raw text content of the model response.

    Raises:
        RuntimeError: If all retries are exhausted.
    """
    from google import genai
    from google.genai import types

    client = genai.Client()
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=model,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=temperature,
                    max_output_tokens=100,
                ),
            )
            return response.text.strip()
        except Exception as e:
            if attempt == max_retries - 1:
                raise RuntimeError(f"Google API error after {max_retries} retries: {e}") from e
            wait = 2 ** attempt
            logger.warning("Google API error, retrying in %ds: %s", wait, e)
            time.sleep(wait)
    raise RuntimeError(f"Google API failed after {max_retries} retries")


_PROVIDER_CALLERS = {
    "openai": _call_openai,
    "anthropic": _call_anthropic,
    "google": _call_google,
}


# ---------------------------------------------------------------------------
# Response parsing
# ---------------------------------------------------------------------------

def _parse_llm_response(raw: str) -> GradeResult:
    """Parse LLM JSON response into a GradeResult.

    Handles common LLM quirks: markdown code fences, extra whitespace,
    label casing variations.

    Args:
        raw: Raw text response from the LLM.

    Returns:
        GradeResult with normalized label, score, and confidence.

    Raises:
        ValueError: If the response cannot be parsed into a valid GradeResult.
    """
    # Strip markdown code fences if present
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        # Remove opening fence (with optional language tag) and closing fence
        lines = cleaned.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        cleaned = "\n".join(lines).strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"LLM response is not valid JSON: {raw!r}"
        ) from e

    raw_label = str(data.get("label", "")).strip().lower()
    confidence = float(data.get("confidence", 0.5))

    # Resolve label via alias table
    label = _LABEL_ALIASES.get(raw_label)
    if label is None:
        raise ValueError(
            f"LLM returned unrecognized label {raw_label!r}. "
            f"Expected one of: {sorted(_LABEL_ALIASES.keys())}"
        )

    score = LABEL_TO_SCORE[label]
    confidence = max(0.0, min(1.0, confidence))

    return GradeResult(label=label, score=score, confidence=confidence)


# ---------------------------------------------------------------------------
# LLMGrader
# ---------------------------------------------------------------------------

class LLMGrader(GraderInterface):
    """Zero-shot LLM grader supporting multiple providers and information levels.

    The grader sends a structured prompt to an LLM API and parses the JSON
    response into a GradeResult. Two information levels control what context
    is provided:
      - level=0: only question + student answer (no reference)
      - level=1: question + student answer + reference answer

    The grader does not require fit() — it uses zero-shot prompting.

    Args:
        provider:     API provider: "openai", "anthropic", or "google".
        model:        Model ID (e.g. "gpt-5.4-mini", "claude-haiku-4-5-20251001",
                      "gemini-2.5-flash").
        level:        Information level: 0 (no reference) or 1 (with reference).
        temperature:  Sampling temperature. Default 0.0 for deterministic output.
        max_retries:  Max retry attempts on transient API errors. Default 5.

    Usage:
        grader = LLMGrader(provider="openai", model="gpt-5.4-mini", level=1)
        result = grader.grade(
            question="What happens when...",
            rubric=None,
            student_answer="The bulb lights up.",
            reference_answer="Current flows and the bulb lights up.",
        )
    """

    def __init__(
        self,
        provider: Literal["openai", "anthropic", "google"],
        model: str,
        level: int = 1,
        temperature: float = 0.0,
        max_retries: int = 5,
    ) -> None:
        if provider not in _PROVIDER_CALLERS:
            raise ValueError(
                f"Unknown provider {provider!r}. "
                f"Supported: {sorted(_PROVIDER_CALLERS.keys())}"
            )
        if level not in (0, 1):
            raise ValueError(f"level must be 0 or 1, got {level!r}")

        self._provider = provider
        self._model = model
        self._level = level
        self._temperature = temperature
        self._max_retries = max_retries
        self._caller = _PROVIDER_CALLERS[provider]

        # Counters for diagnostics
        self._call_count = 0
        self._parse_error_count = 0

    @property
    def grader_name(self) -> str:
        """Unique identifier encoding provider, model, and information level.

        Returns:
            str: e.g. "llm_openai_gpt-5.4-mini_level1"
        """
        return f"llm_{self._provider}_{self._model}_level{self._level}"

    def grade(
        self,
        question: str,
        rubric: Optional[str],
        student_answer: str,
        reference_answer: str = "",
    ) -> GradeResult:
        """Grade a student answer via LLM API call.

        For level=0, reference_answer is ignored even if provided.
        For level=1, reference_answer is included in the prompt.

        Args:
            question:         The question text shown to the student.
            rubric:           Optional rubric text (unused in current prompt design;
                              reserved for Livello 2 future extension).
            student_answer:   The raw text of the student's response.
            reference_answer: Reference answer. Used only when level=1.

        Returns:
            GradeResult with label, score in [0.0, 1.0], and confidence.

        Raises:
            RuntimeError: If the API call fails after max_retries.
            ValueError:   If the LLM response cannot be parsed after retry.
        """
        if self._level == 0:
            user_prompt = _USER_PROMPT_LEVEL0.format(
                question=question,
                student_answer=student_answer,
            )
        else:
            user_prompt = _USER_PROMPT_LEVEL1.format(
                question=question,
                reference_answer=reference_answer,
                student_answer=student_answer,
            )

        self._call_count += 1

        raw = self._caller(
            model=self._model,
            system_prompt=_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=self._temperature,
            max_retries=self._max_retries,
        )

        try:
            return _parse_llm_response(raw)
        except ValueError:
            self._parse_error_count += 1
            logger.warning(
                "Parse error on call %d (total parse errors: %d). Raw: %s",
                self._call_count,
                self._parse_error_count,
                raw[:200],
            )
            # Retry once with explicit instruction
            retry_prompt = (
                f"Your previous response was not valid JSON. "
                f"Please respond with ONLY a JSON object like: "
                f'{{"label": "correct", "confidence": 0.9}}\n\n'
                f"{user_prompt}"
            )
            raw_retry = self._caller(
                model=self._model,
                system_prompt=_SYSTEM_PROMPT,
                user_prompt=retry_prompt,
                temperature=self._temperature,
                max_retries=self._max_retries,
            )
            return _parse_llm_response(raw_retry)

    @property
    def diagnostics(self) -> Dict[str, Any]:
        """Return diagnostic counters for logging/debugging.

        Returns:
            Dict with call_count, parse_error_count, and configuration.
        """
        return {
            "provider": self._provider,
            "model": self._model,
            "level": self._level,
            "temperature": self._temperature,
            "call_count": self._call_count,
            "parse_error_count": self._parse_error_count,
        }


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Running LLMGrader self-test (parse logic only, no API calls)...")

    # Test response parsing
    valid = '{"label": "correct", "confidence": 0.95}'
    result = _parse_llm_response(valid)
    assert result.label == "correct"
    assert result.score == 1.0
    assert result.confidence == 0.95
    print(f"  Parse valid JSON: OK ({result})")

    # Test with markdown fences
    fenced = '```json\n{"label": "partially_correct_incomplete", "confidence": 0.7}\n```'
    result = _parse_llm_response(fenced)
    assert result.label == "partially_correct_incomplete"
    assert result.score == 0.5
    print(f"  Parse fenced JSON: OK ({result})")

    # Test alias resolution
    alias = '{"label": "incorrect", "confidence": 0.8}'
    result = _parse_llm_response(alias)
    assert result.label == "contradictory"
    assert result.score == 0.0
    print(f"  Parse alias label: OK ({result})")

    # Test grader_name
    grader = LLMGrader(provider="openai", model="gpt-5.4-mini", level=1)
    assert grader.grader_name == "llm_openai_gpt-5.4-mini_level1"
    print(f"  Grader name: OK ({grader.grader_name})")

    # Test level validation
    try:
        LLMGrader(provider="openai", model="test", level=2)
        raise AssertionError("Should have raised ValueError")
    except ValueError:
        print("  Level validation: OK (rejected level=2)")

    print("\nAll self-tests passed.")
