"""
LLM integration for the HTSA engine.

Provider-agnostic — works with any OpenAI-compatible chat completions endpoint.
Zero external dependencies beyond the Python standard library.
"""

from .advisor import LLMAdvisor
from .client import ChatCompletionsClient

__all__ = ["LLMAdvisor", "ChatCompletionsClient"]
