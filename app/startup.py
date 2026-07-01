"""Application startup and shared state."""

from __future__ import annotations

from pathlib import Path

from loguru import logger

from app.catalog.loader import Catalog
from app.catalog.preprocessor import load_catalog_dataframe, load_catalog_from_dataframe
from app.config import Settings, get_settings
from app.conversation.engine import ConversationEngine
from app.llm.factory import create_llm_provider
from app.logging_config import configure_logging
from app.retrieval.chroma_store import ChromaStore
from app.retrieval.embeddings import EmbeddingService
from app.retrieval.reranker import Reranker


class AppState:
    catalog: Catalog | None = None
    store: ChromaStore | None = None
    engine: ConversationEngine | None = None


state = AppState()


def initialize_app(settings: Settings | None = None) -> ConversationEngine:
    settings = settings or get_settings()
    configure_logging(settings)

    catalog_path = Path(settings.catalog_path)
    if not catalog_path.exists():
        raise FileNotFoundError(f"Catalog not found at {catalog_path}")

    logger.info("Loading and preprocessing catalog from {}", catalog_path)
    df = load_catalog_dataframe(catalog_path)
    catalog = load_catalog_from_dataframe(df)
    logger.info("Loaded {} assessments", len(catalog))

    embeddings = EmbeddingService(settings)
    reranker = Reranker(settings)
    store = ChromaStore(catalog, settings, embeddings, reranker)

    if not store.is_indexed:
        logger.info("Building ChromaDB index...")
        store.build()
    else:
        logger.info("Using existing ChromaDB index at {}", settings.chroma_path)

    llm = create_llm_provider(settings)
    engine = ConversationEngine(catalog=catalog, store=store, llm=llm, settings=settings)

    state.catalog = catalog
    state.store = store
    state.engine = engine
    return engine
