"""LLM extraction package.

Ports the exploratory notebooks ``llm_stuff/llm_test_ED.ipynb`` and
``llm_test_EE.ipynb`` into callable functions the backend can invoke.
"""

from .extractor import extract_ed, extract_ee  # noqa: F401
