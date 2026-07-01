"""Integration tests for startup and end-to-end initialization."""

from app.config import Settings
from app.startup import initialize_app, state


def test_initialize_app_builds_engine():
    settings = Settings(
        llm_provider="mock",
        use_reranker=False,
        retrieval_mode="keyword",
        lazy_init=False,
        catalog_path="data/shl_product_catalog.json",
    )
    engine = initialize_app(settings)
    assert engine is not None
    assert state.catalog is not None
    assert state.retriever is not None
    assert state.ready is True
    assert len(state.catalog) > 100
