"""Deterministic LLM fallback for tests and offline development."""

from __future__ import annotations

from typing import Any

from app.llm.base import LLMProvider


class MockProvider(LLMProvider):
    async def generate_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        del system_prompt
        if "Draft reply:" in user_prompt:
            draft = user_prompt.split("Draft reply:", 1)[1].split("Catalog context:", 1)[0].strip()
            if draft:
                return {"reply": draft}

        lower = user_prompt.lower()
        if "legally required" in lower or "regulatory obligation" in lower:
            return {"reply": "I cannot provide legal advice.", "tone": "refuse"}
        if "difference between" in lower:
            return {"reply": "Here is a catalog-grounded comparison.", "tone": "compare"}
        if "we need a solution" in lower and "turn count" in lower and "1" in lower[:120]:
            return {"reply": "Who is this meant for?", "tone": "clarify"}
        return {"reply": "Here are SHL assessments that fit your requirements.", "tone": "recommend"}
