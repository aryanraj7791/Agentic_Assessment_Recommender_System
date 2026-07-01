"""Gemini 2.5 Flash provider using the official Google GenAI SDK."""

from __future__ import annotations

import json
from typing import Any

from google import genai
from google.genai import types
from loguru import logger

from app.config import Settings
from app.llm.base import LLMProvider


class GeminiProvider(LLMProvider):
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = genai.Client(api_key=settings.gemini_api_key)

    async def generate_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        if not self.settings.gemini_api_key:
            logger.warning("GEMINI_API_KEY missing; returning empty JSON payload.")
            return {}

        response = await self.client.aio.models.generate_content(
            model=self.settings.gemini_model,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.2,
                response_mime_type="application/json",
            ),
        )
        text = response.text or "{}"
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            logger.error("Gemini returned invalid JSON: {}", text[:200])
            return {}
