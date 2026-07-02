"""Create the appropriate retriever based on environment settings."""

from __future__ import annotations

from loguru import logger

from app.catalog.loader import Catalog
from app.config import Settings
from app.retrieval.base import Retriever
from app.retrieval.keyword_search import KeywordSearch


def create_retriever(catalog: Catalog, settings: Settings) -> Retriever:
    mode = settings.retrieval_mode.lower()
    if mode == "keyword":
        logger.info("Using lightweight BM25 keyword retrieval")
        return KeywordSearch(catalog)

    logger.info("Using ChromaDB embedding retrieval")
    from app.retrieval.chroma_store import ChromaStore
    from app.retrieval.embeddings import EmbeddingService
    from app.retrieval.reranker import Reranker

    embeddings = EmbeddingService(settings)
    reranker = Reranker(settings)
    store = ChromaStore(catalog, settings, embeddings, reranker)
    if not store.is_indexed:
        logger.warning("Chroma index missing — building now (may use significant memory)")
        store.build()
    return store
