"""
asag.loaders — Dataset loader interface and implementations.

Re-exports the abstract base class and all concrete loaders so callers can use:
    from asag.loaders import DatasetLoader, SemEval2013Loader
"""

from asag.loaders.base import DatasetLoader
from asag.loaders.semeval2013 import SemEval2013Loader

__all__ = [
    "DatasetLoader",
    "SemEval2013Loader",
]
