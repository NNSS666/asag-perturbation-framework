"""
Gaming perturbation generators — rubric keyword echoing and fluent wrong extension.

Gaming perturbations simulate adversarial students who try to game automated graders
by superficially matching the rubric (keyword echoing) or sounding authoritative
while being factually wrong (fluent wrong extension).

Generators:
  RubricKeywordEchoingGenerator  — appends reference-answer keywords not present
                                   in the student answer to simulate keyword stuffing
  FluentWrongExtensionGenerator  — appends a confident but factually incorrect
                                   domain statement picked from a curated pool

Both generators use random.Random(seed) for reproducibility.
"""

import random
from typing import List

from asag.perturbations.generators import PerturbationGenerator
from asag.schema.records import AnswerRecord, QuestionRecord

# ---------------------------------------------------------------------------
# Shared stopwords for keyword extraction
# ---------------------------------------------------------------------------

_STOPWORDS = frozenset({
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "this", "that", "these", "those", "is",
    "are", "was", "were", "be", "been", "being", "have", "has", "had",
    "it", "its",
})

# ---------------------------------------------------------------------------
# Fluent wrong extension — curated pool of domain-appropriate wrong statements
# ---------------------------------------------------------------------------

WRONG_STATEMENTS: List[str] = [
    # Physics / circuits (Beetle dataset)
    "This is because electrical resistance causes current to flow faster through "
    "thinner wires.",
    "The voltage across an open switch is always zero.",
    "Batteries produce electrons from chemical energy stored in the plastic casing.",
    "Current flows from the negative terminal to the positive terminal inside "
    "the battery.",
    "Resistance and voltage are always equal in a simple circuit.",
    "A bulb glows brighter when connected in series because it receives more "
    "current.",
    "Insulators allow a small amount of current to flow when the voltage is "
    "high enough.",
    "The electric field inside a conductor is proportional to the current "
    "flowing through it.",
    "Parallel circuits always have higher total resistance than series circuits.",
    "A switch completes the circuit by generating additional electrons.",
    # Biology (SciEntsBank dataset)
    "Photosynthesis primarily occurs in the root cells of plants.",
    "Mitosis produces four genetically unique daughter cells.",
    "Carbon dioxide is absorbed through the stomata and converted directly into "
    "glucose without any enzyme involvement.",
    "Mammals obtain energy by converting sunlight into glucose through their skin.",
    "DNA replication occurs after cell division to restore the genetic material.",
    "Predators always outnumber their prey in a stable ecosystem.",
    "The cell membrane is made of a single layer of protein molecules.",
    "All bacteria are harmful to human health.",
    "Plants absorb oxygen during the day to fuel photosynthesis.",
    "The heart pumps blood to the lungs through the aorta.",
    # Chemistry
    "Ionic bonds form when two nonmetal atoms share electrons equally.",
    "The pH of pure water is approximately 3.5 at room temperature.",
    "Oxidation always results in a loss of oxygen atoms from a compound.",
    "Catalysts increase the activation energy required for a chemical reaction.",
    "Acids always have a pH greater than 7 at standard conditions.",
    "All metals dissolve readily in water to form alkaline solutions.",
    # Earth science
    "Sedimentary rocks are formed primarily by volcanic activity.",
    "The water cycle begins when precipitation falls upward from the ground.",
    "Earthquakes only occur at convergent plate boundaries.",
    "The Moon's gravitational pull is stronger than Earth's due to its proximity.",
]

# Connecting phrases for appending wrong statements
_CONNECTORS: List[str] = [
    "Furthermore, ",
    "Additionally, ",
    "Moreover, ",
    "Also, ",
    "In addition, ",
]


class RubricKeywordEchoingGenerator(PerturbationGenerator):
    """Append reference-answer keywords not present in the student answer.

    Simulates a student who keyword-stuffs by appending terms from the reference
    answer that are absent from their own response. Two variants are generated
    with different keyword counts to provide diversity:
      Variant 0: 3-4 keywords (random.Random(seed).sample)
      Variant 1: 5-6 keywords (random.Random(seed+1).sample)

    If the reference answer has no terms not already present in the student
    answer, returns an empty list.
    """

    family = "gaming"
    type_name = "rubric_keyword_echoing"
    n_variants = 2

    def generate(
        self,
        answer: AnswerRecord,
        question: QuestionRecord,
        seed: int,
    ) -> List[str]:
        """Return up to 2 keyword-echoed variants.

        Args:
            answer:   Source AnswerRecord.
            question: QuestionRecord; reference_answers[0] is used as rubric source.
            seed:     Controls keyword sampling.

        Returns:
            List of 0, 1, or 2 strings.
        """
        if not question.reference_answers:
            return []

        ref_text = question.reference_answers[0]
        student_tokens = {
            w.lower().strip(".,;:!?\"'")
            for w in answer.student_answer.split()
        }

        # Extract unique reference content terms not in student answer
        ref_unique: List[str] = sorted({
            w.lower().strip(".,;:!?\"'")
            for w in ref_text.split()
            if len(w.strip(".,;:!?\"'")) >= 4
            and w.lower().strip(".,;:!?\"'") not in _STOPWORDS
            and w.lower().strip(".,;:!?\"'") not in student_tokens
            and w.strip(".,;:!?\"'").isalpha()
        })

        if not ref_unique:
            return []

        variants: List[str] = []
        base = answer.student_answer

        # Variant 0: 3-4 keywords
        rng0 = random.Random(seed)
        count0 = min(rng0.randint(3, 4), len(ref_unique))
        if count0 > 0:
            keywords0 = rng0.sample(ref_unique, count0)
            variants.append(base + " " + " ".join(keywords0))

        # Variant 1: 5-6 keywords (different seed offset for diversity)
        rng1 = random.Random(seed + 1)
        count1 = min(rng1.randint(5, 6), len(ref_unique))
        if count1 > 0:
            keywords1 = rng1.sample(ref_unique, count1)
            variants.append(base + " " + " ".join(keywords1))

        return variants


class FluentWrongExtensionGenerator(PerturbationGenerator):
    """Append a confident but factually incorrect domain statement.

    Picks one statement from the WRONG_STATEMENTS pool using random.Random(seed)
    and appends it to the student answer with a connecting phrase.

    The generated text sounds authoritative and fluent but contains a clear
    factual error — designed to test whether graders can distinguish correctness
    from confident-sounding prose.
    """

    family = "gaming"
    type_name = "fluent_wrong_extension"
    n_variants = 1

    def generate(
        self,
        answer: AnswerRecord,
        question: QuestionRecord,
        seed: int,
    ) -> List[str]:
        """Return 1 fluent-wrong-extended variant.

        Args:
            answer:   Source AnswerRecord.
            question: QuestionRecord (unused by this generator).
            seed:     Controls which wrong statement and connector are chosen.

        Returns:
            List with exactly 1 string.
        """
        rng = random.Random(seed)
        connector = rng.choice(_CONNECTORS)
        wrong_statement = rng.choice(WRONG_STATEMENTS)
        return [f"{answer.student_answer} {connector}{wrong_statement}"]
