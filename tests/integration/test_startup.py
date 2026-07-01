"""Integration tests for startup and end-to-end initialization."""

from app.config import Settings
from app.startup import initialize_app, state


def test_initialize_app_builds_engine():
    settings = Settings(
        llm_provider="mock",
        use_reranker=False,
        catalog_path="data/shl_product_catalog.json",
        chroma_path="data/chroma",
    )
    engine = initialize_app(settings)
    assert engine is not None
    assert state.catalog is not None
    assert state.store is not None
    assert len(state.catalog) > 100
