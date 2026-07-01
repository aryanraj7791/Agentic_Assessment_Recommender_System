"""Embedding model loader with hardware-aware fallback."""

from __future__ import annotations

from loguru import logger
from sentence_transformers import SentenceTransformer

from app.config import Settings


class EmbeddingService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.model_name = settings.embedding_model
        self._model: SentenceTransformer | None = None

    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            self._model = self._load_with_fallback()
        return self._model

    def _load_with_fallback(self) -> SentenceTransformer:
        try:
            logger.info("Loading embedding model: {}", self.settings.embedding_model)
            return SentenceTransformer(self.settings.embedding_model)
        except Exception as exc:
            logger.warning(
                "Failed to load {} ({}). Falling back to {}.",
                self.settings.embedding_model,
                exc,
                self.settings.embedding_fallback_model,
            )
            self.model_name = self.settings.embedding_fallback_model
            return SentenceTransformer(self.settings.embedding_fallback_model)

    def encode(self, texts: list[str]) -> list[list[float]]:
        vectors = self.model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return vectors.tolist()

    def encode_query(self, text: str) -> list[float]:
        return self.encode([text])[0]
