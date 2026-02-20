"""
Leakage diagnostic for LOQO (Leave-One-Question-Out) cross-validation.

Purpose: Scientific integrity check that confirms the held-out question's
identity does NOT appear in the training-side data. This must run before every
LOQO fold to detect two classes of contamination:

  1. ID leakage:     the held-out question_id appears as the question_id of any
                     training QuestionRecord — indicates the LOQO split is broken.
  2. Prompt leakage: the verbatim text of the held-out question's prompt appears
                     as a substring of any training-side question prompt or
                     reference answer — indicates the question text leaked into
                     the training corpus.

Note on reference answer overlap: It is EXPECTED and CORRECT that different
questions in the same Beetle/SciEntsBank domain share reference answer phrases
(e.g., "current flows through the circuit" is a valid answer to multiple questions
about electricity). Reference answers are therefore NOT included in Check 2 —
only the question prompt (the query the grader must answer) is checked. This
is the conservative-but-correct choice that avoids false positives on real data.

See RESEARCH.md Pitfall 4 for the full motivation.

Python 3.9 compatible — uses typing.List (not list[...]).
"""

import logging
from typing import List

from asag.schema.records import QuestionRecord

logger = logging.getLogger(__name__)


def assert_no_leakage(
    train_questions: List[QuestionRecord],
    held_out_question: QuestionRecord,
) -> None:
    """Assert that no held-out question information leaks into the training set.

    Runs two checks:

      Check 1 — ID isolation:
        Verifies that held_out_question.question_id does not appear as the
        question_id of ANY QuestionRecord in train_questions. A failure here
        indicates the LOQO split itself is incorrect.

      Check 2 — Prompt text isolation:
        Verifies that the verbatim text of held_out_question.prompt does not
        appear as a substring of any training QuestionRecord's prompt or any
        training-side reference answer.

        Reference answers are intentionally excluded from the held-out set in
        this check: in the SemEval Beetle/SciEntsBank corpus, multiple questions
        share valid reference answer phrases (e.g., physics domain truisms), so
        checking reference answers would produce false positives on correct splits.

    Args:
        train_questions:   List of QuestionRecords used for training in this fold.
        held_out_question: The QuestionRecord being held out for testing.

    Raises:
        AssertionError: If any leakage is detected, with a descriptive message
                        indicating which check failed and the offending text.
    """
    held_out_id = held_out_question.question_id
    held_out_prompt = held_out_question.prompt

    for train_q in train_questions:
        # --- Check 1: ID isolation ---
        assert train_q.question_id != held_out_id, (
            f"Leakage detected (ID): held-out question_id '{held_out_id}' "
            f"appears in training QuestionRecord '{train_q.question_id}'. "
            f"The LOQO split is incorrect — held-out question must not be in "
            f"the training set."
        )

        # --- Check 2: Prompt text isolation ---
        # The prompt is the text the grader must generalize to; if it appears
        # verbatim in the training corpus, the model may overfit to its keywords.
        if not held_out_prompt.strip():
            continue  # Skip empty prompts (edge case for malformed records)

        # Check against training-side question prompt
        assert held_out_prompt not in train_q.prompt, (
            f"Leakage detected (prompt text): prompt of held-out question "
            f"'{held_out_id}' appears verbatim in training question prompt "
            f"'{train_q.question_id}'. "
            f"Held-out prompt (first 80 chars): {held_out_prompt[:80]!r}. "
            f"Training prompt (first 80 chars): {train_q.prompt[:80]!r}."
        )

        # Check against each training-side reference answer
        for ref_ans in train_q.reference_answers:
            assert held_out_prompt not in ref_ans, (
                f"Leakage detected (prompt in ref): prompt of held-out question "
                f"'{held_out_id}' appears verbatim in a reference answer of "
                f"training question '{train_q.question_id}'. "
                f"Held-out prompt (first 80 chars): {held_out_prompt[:80]!r}. "
                f"Ref answer (first 80 chars): {ref_ans[:80]!r}."
            )


# ---------------------------------------------------------------------------
# Self-test (run with: PYTHONPATH=src python3 src/asag/splitters/leakage.py)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Running leakage diagnostic self-test...")

    q_held = QuestionRecord(
        question_id="beetle_abc123",
        prompt="What causes the bulb to light up?",
        reference_answers=["Current flows through the circuit."],
        corpus="beetle",
    )

    q_train1 = QuestionRecord(
        question_id="beetle_def456",
        prompt="What happens when a switch is open?",
        reference_answers=["No current flows, the circuit is broken."],
        corpus="beetle",
    )

    q_train2 = QuestionRecord(
        question_id="beetle_ghi789",
        prompt="How does a resistor affect current?",
        # Shared reference answer — this is EXPECTED and should NOT trigger leakage
        reference_answers=["Current flows through the circuit."],
        corpus="beetle",
    )

    # Should pass — shared reference answer is NOT a leakage (domain overlap is ok)
    assert_no_leakage([q_train1, q_train2], q_held)
    print("  PASS: clean split (shared reference answer correctly allowed).")

    # Should fail — ID leakage (held-out question in training list)
    try:
        assert_no_leakage([q_held, q_train1], q_held)
        raise RuntimeError("Expected AssertionError for ID leakage, got none.")
    except AssertionError as exc:
        print("  PASS: ID leakage correctly detected:", str(exc)[:70], "...")

    # Should fail — prompt text leakage (held-out prompt appears in training ref answer)
    q_contaminated_ref = QuestionRecord(
        question_id="beetle_zzz999",
        prompt="Another question about electricity",
        reference_answers=["What causes the bulb to light up? [contaminated]"],
        corpus="beetle",
    )
    try:
        assert_no_leakage([q_contaminated_ref], q_held)
        raise RuntimeError("Expected AssertionError for prompt-in-ref leakage, got none.")
    except AssertionError as exc:
        print("  PASS: prompt-in-ref leakage correctly detected:", str(exc)[:70], "...")

    # Should fail — prompt text leakage (held-out prompt appears in training prompt)
    q_contaminated_prompt = QuestionRecord(
        question_id="beetle_yyy888",
        prompt="What causes the bulb to light up? [extended version]",
        reference_answers=["A different reference answer."],
        corpus="beetle",
    )
    try:
        assert_no_leakage([q_contaminated_prompt], q_held)
        raise RuntimeError("Expected AssertionError for prompt-in-prompt leakage, got none.")
    except AssertionError as exc:
        print("  PASS: prompt-in-prompt leakage correctly detected:", str(exc)[:70], "...")

    print("\nAll self-tests passed.")
