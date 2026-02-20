"""
Abstract base class for all ASAG dataset loaders (DATA-04).

Design: Every new dataset is a new subclass of DatasetLoader — no pipeline
changes needed. The interface forces callers to receive data in canonical schema
types (QuestionRecord, AnswerRecord) regardless of the original format.

Adding a new dataset:
    1. Subclass DatasetLoader
    2. Implement load() to return (questions, answers) in canonical schema
    3. Implement corpus_name property
    4. No other changes needed — loaders plug in without modifying the pipeline

Example:
    class MyDatasetLoader(DatasetLoader):
        @property
        def corpus_name(self) -> str:
            return "my_dataset"

        def load(self) -> Tuple[List[QuestionRecord], List[AnswerRecord]]:
            # ... load data, map to canonical types, return
            return questions, answers
"""

from abc import ABC, abstractmethod
from typing import List, Tuple

from asag.schema.records import AnswerRecord, QuestionRecord


class DatasetLoader(ABC):
    """Abstract base class that every dataset loader must implement.

    A new dataset = a new subclass. No pipeline modifications required.
    The load() method must return all available data (all rows, all splits
    concatenated) in canonical schema form. Split-specific logic belongs in
    the splitter layer (asag.splitters), not here.
    """

    @abstractmethod
    def load(self) -> Tuple[List[QuestionRecord], List[AnswerRecord]]:
        """Load the dataset and return (questions, answers) in canonical schema.

        Returns:
            questions: One QuestionRecord per unique question. reference_answers
                       collects all distinct reference answers for that question.
            answers:   One AnswerRecord per student response. gold_score is
                       normalized to [0.0, 1.0] by the loader.

        Note:
            Concatenate ALL available splits (e.g. HuggingFace train/test_ua/
            test_uq/test_ud) — do NOT filter by split name. Splitting for
            Protocol A (LOQO) and Protocol B (within-question) is handled
            downstream by the splitter layer.
        """
        ...

    @property
    @abstractmethod
    def corpus_name(self) -> str:
        """Human-readable corpus identifier used in run directory naming.

        Returns:
            A short, filesystem-safe string, e.g. "semeval2013_beetle" or
            "semeval2013_scientsbank". Used to auto-name experiment output
            directories (runs/<timestamp>_<corpus_name>_seed<N>/).
        """
        ...
