"""Optional cross-encoder reranking."""

from __future__ import annotations

from loguru import logger
from sentence_transformers import CrossEncoder

from app.catalog.loader import Assessment
from app.config import Settings


class Reranker:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._model: CrossEncoder | None = None

    @property
    def enabled(self) -> bool:
        return self.settings.use_reranker

    @property
    def model(self) -> CrossEncoder:
        if self._model is None:
            logger.info("Loading reranker model: {}", self.settings.reranker_model)
            self._model = CrossEncoder(self.settings.reranker_model)
        return self._model

    def rerank(self, query: str, candidates: list[Assessment], top_k: int = 10) -> list[Assessment]:
        if not candidates:
            return []
        if not self.enabled:
            return candidates[:top_k]

        pairs = [[query, f"{item.name}. {item.description}"] for item in candidates]
        scores = self.model.predict(pairs)
        ranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
        return [item for item, _ in ranked[:top_k]]
