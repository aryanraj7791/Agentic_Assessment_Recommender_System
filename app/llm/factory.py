"""LLM provider factory."""

from __future__ import annotations

from app.config import Settings
from app.llm.base import LLMProvider
from app.llm.gemini import GeminiProvider
from app.llm.mock import MockProvider


def create_llm_provider(settings: Settings) -> LLMProvider:
    provider = settings.llm_provider.lower()
    if provider == "mock":
        return MockProvider()
    if provider == "gemini":
        return GeminiProvider(settings)
    raise ValueError(f"Unsupported LLM provider: {provider}")
