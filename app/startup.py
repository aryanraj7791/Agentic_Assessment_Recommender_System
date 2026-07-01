"""Application startup and shared state."""

from __future__ import annotations

import threading
from pathlib import Path

from loguru import logger

from app.catalog.preprocessor import load_catalog_dataframe, load_catalog_from_dataframe
from app.config import Settings, get_settings
from app.conversation.engine import ConversationEngine
from app.llm.factory import create_llm_provider
from app.logging_config import configure_logging
from app.retrieval.factory import create_retriever

_init_lock = threading.Lock()


class AppState:
    catalog = None
    retriever = None
    engine: ConversationEngine | None = None
    ready: bool = False
    init_error: str | None = None


state = AppState()


def initialize_app(settings: Settings | None = None) -> ConversationEngine:
    settings = settings or get_settings()
    configure_logging(settings)

    catalog_path = Path(settings.catalog_path)
    if not catalog_path.exists():
        raise FileNotFoundError(f"Catalog not found at {catalog_path}")

    logger.info("Loading catalog from {}", catalog_path)
    df = load_catalog_dataframe(catalog_path)
    catalog = load_catalog_from_dataframe(df)
    logger.info("Loaded {} assessments", len(catalog))

    retriever = create_retriever(catalog, settings)
    llm = create_llm_provider(settings)
    engine = ConversationEngine(catalog=catalog, retriever=retriever, llm=llm, settings=settings)

    state.catalog = catalog
    state.retriever = retriever
    state.engine = engine
    state.ready = True
    state.init_error = None
    logger.info("Conversation engine ready (retrieval_mode={})", settings.retrieval_mode)
    return engine


def initialize_app_background(settings: Settings | None = None) -> None:
    """Initialize in a background thread so Uvicorn can bind the port immediately."""

    def _run() -> None:
        try:
            initialize_app(settings)
        except Exception as exc:
            logger.exception("Background initialization failed")
            state.init_error = str(exc)

    thread = threading.Thread(target=_run, daemon=True, name="app-init")
    thread.start()


def ensure_initialized(settings: Settings | None = None) -> ConversationEngine:
    if state.engine is not None:
        return state.engine
    with _init_lock:
        if state.engine is None:
            return initialize_app(settings)
    return state.engine  # type: ignore[return-value]
