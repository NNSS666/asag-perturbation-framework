"""
Tests for LLMGrader — parsing, constructor validation, interface compliance, and
grade() with mocked API calls.

No real API calls are made. Provider callers are mocked via unittest.mock.patch.
"""

import pytest
from unittest.mock import patch, call

from asag.graders.base import GradeResult, GraderInterface
from asag.graders.llm import LLMGrader, _parse_llm_response


# ---------------------------------------------------------------------------
# 1. _parse_llm_response tests
# ---------------------------------------------------------------------------


def test_parse_valid_json():
    """Valid JSON with canonical label parses correctly."""
    raw = '{"label": "correct", "confidence": 0.95}'
    result = _parse_llm_response(raw)
    assert result.label == "correct"
    assert result.score == 1.0
    assert result.confidence == 0.95


def test_parse_markdown_fenced_json():
    """JSON wrapped in markdown code fences parses correctly."""
    raw = '```json\n{"label": "partially_correct_incomplete", "confidence": 0.7}\n```'
    result = _parse_llm_response(raw)
    assert result.label == "partially_correct_incomplete"
    assert result.score == 0.5
    assert result.confidence == 0.7


@pytest.mark.parametrize(
    "raw_label, expected_label, expected_score",
    [
        ("incorrect", "contradictory", 0.0),
        ("wrong", "contradictory", 0.0),
        ("partial", "partially_correct_incomplete", 0.5),
        ("partially_correct", "partially_correct_incomplete", 0.5),
        ("off-topic", "irrelevant", 0.0),
        ("non domain", "non_domain", 0.0),
    ],
)
def test_parse_alias_resolution(raw_label, expected_label, expected_score):
    """Fuzzy label aliases resolve to canonical labels."""
    raw = f'{{"label": "{raw_label}", "confidence": 0.8}}'
    result = _parse_llm_response(raw)
    assert result.label == expected_label
    assert result.score == expected_score


def test_parse_invalid_json():
    """Non-JSON input raises ValueError."""
    with pytest.raises(ValueError, match="not valid JSON"):
        _parse_llm_response("this is not json at all")


def test_parse_unknown_label():
    """Unrecognized label raises ValueError."""
    raw = '{"label": "excellent", "confidence": 0.9}'
    with pytest.raises(ValueError, match="unrecognized label"):
        _parse_llm_response(raw)


# ---------------------------------------------------------------------------
# 2. Constructor validation tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("provider", ["openai", "anthropic", "google"])
def test_valid_providers(provider):
    """All three supported providers construct without error."""
    grader = LLMGrader(provider=provider, model="test-model", level=1)
    assert grader is not None


def test_invalid_provider():
    """Unknown provider raises ValueError."""
    with pytest.raises(ValueError, match="Unknown provider"):
        LLMGrader(provider="azure", model="test-model", level=1)


@pytest.mark.parametrize("level", [0, 1])
def test_valid_levels(level):
    """Levels 0 and 1 construct without error."""
    grader = LLMGrader(provider="openai", model="test-model", level=level)
    assert grader is not None


def test_invalid_level():
    """Level outside {0, 1} raises ValueError."""
    with pytest.raises(ValueError, match="level must be 0 or 1"):
        LLMGrader(provider="openai", model="test-model", level=2)


# ---------------------------------------------------------------------------
# 3. Interface compliance tests
# ---------------------------------------------------------------------------


def test_llm_grader_implements_interface():
    """LLMGrader must inherit from GraderInterface."""
    grader = LLMGrader(provider="openai", model="test-model", level=1)
    assert isinstance(grader, GraderInterface)


def test_llm_grader_has_no_fit():
    """LLMGrader must NOT have a fit() method.

    The EvaluationEngine checks hasattr(grader, 'fit') to decide whether
    to call it. LLMGrader is zero-shot and must not define fit().
    """
    grader = LLMGrader(provider="openai", model="test-model", level=1)
    assert not hasattr(grader, "fit")


# ---------------------------------------------------------------------------
# 4. grader_name format test
# ---------------------------------------------------------------------------


def test_grader_name_format():
    """grader_name must encode provider, model, and level."""
    grader_l1 = LLMGrader(provider="openai", model="gpt-5.4-mini", level=1)
    assert grader_l1.grader_name == "llm_openai_gpt-5.4-mini_level1"

    grader_l0 = LLMGrader(provider="google", model="gemini-2.5-flash", level=0)
    assert grader_l0.grader_name == "llm_google_gemini-2.5-flash_level0"


# ---------------------------------------------------------------------------
# 5. grade() with mocked API calls
# ---------------------------------------------------------------------------


def _mock_caller(return_values):
    """Create a mock caller that records calls and returns canned responses.

    Args:
        return_values: A string (single return) or list of strings (sequential returns).

    Returns:
        Tuple of (mock_fn, calls_list). calls_list captures (model, system_prompt,
        user_prompt, temperature, max_retries) for each call.
    """
    calls = []
    if isinstance(return_values, str):
        return_values = [return_values]
    call_idx = [0]

    def mock_fn(model, system_prompt, user_prompt, temperature, max_retries):
        calls.append({
            "model": model,
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "temperature": temperature,
            "max_retries": max_retries,
        })
        idx = call_idx[0]
        call_idx[0] += 1
        return return_values[idx]

    return mock_fn, calls


def test_grade_level0_ignores_reference():
    """Level 0 grader must NOT include reference_answer in the prompt."""
    mock_fn, calls = _mock_caller('{"label": "correct", "confidence": 0.9}')

    grader = LLMGrader(provider="openai", model="gpt-5.4-mini", level=0)
    grader._caller = mock_fn

    result = grader.grade(
        question="What happens when you close a circuit?",
        rubric=None,
        student_answer="The bulb lights up.",
        reference_answer="Current flows and the bulb lights up.",
    )

    assert isinstance(result, GradeResult)
    assert result.label == "correct"
    assert result.score == 1.0

    # Verify reference_answer is NOT in the user_prompt sent to the API
    assert len(calls) == 1
    user_prompt = calls[0]["user_prompt"]
    assert "Current flows and the bulb lights up" not in user_prompt
    assert "What happens when you close a circuit?" in user_prompt
    assert "The bulb lights up." in user_prompt


def test_grade_level1_includes_reference():
    """Level 1 grader must include reference_answer in the prompt."""
    mock_fn, calls = _mock_caller('{"label": "correct", "confidence": 0.85}')

    grader = LLMGrader(provider="openai", model="gpt-5.4-mini", level=1)
    grader._caller = mock_fn

    result = grader.grade(
        question="What happens when you close a circuit?",
        rubric=None,
        student_answer="The bulb lights up.",
        reference_answer="Current flows and the bulb lights up.",
    )

    assert isinstance(result, GradeResult)
    assert result.label == "correct"

    # Verify reference_answer IS in the user_prompt
    assert len(calls) == 1
    user_prompt = calls[0]["user_prompt"]
    assert "Current flows and the bulb lights up" in user_prompt


def test_grade_retry_on_parse_error():
    """grade() retries with explicit instruction on first parse failure."""
    mock_fn, calls = _mock_caller([
        "I think the answer is correct",  # not JSON — triggers retry
        '{"label": "correct", "confidence": 0.9}',  # valid retry
    ])

    grader = LLMGrader(provider="openai", model="gpt-5.4-mini", level=1)
    grader._caller = mock_fn

    result = grader.grade(
        question="Test question",
        rubric=None,
        student_answer="Test answer",
        reference_answer="Reference",
    )

    assert result.label == "correct"
    assert len(calls) == 2
    assert grader._parse_error_count == 1
