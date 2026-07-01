import pytest

from app.config import Settings
from app.retrieval.chroma_store import ChromaStore
from app.retrieval.embeddings import EmbeddingService
from app.retrieval.reranker import Reranker
from app.startup import initialize_app


@pytest.fixture(scope="module")
def store():
    settings = Settings(
        llm_provider="mock",
        use_reranker=False,
        catalog_path="data/shl_product_catalog.json",
        chroma_path="data/chroma",
    )
    initialize_app(settings)
    from app.startup import state

    assert state.catalog is not None
    assert state.store is not None
    return state.store


def test_retrieval_finds_java_assessment(store: ChromaStore):
    results = store.search("Java developer Spring SQL backend", top_k=5)
    assert results
    joined = " ".join(item.name.lower() for item in results)
    assert "java" in joined or "spring" in joined


def test_retrieval_finds_opq(store: ChromaStore):
    results = store.search("personality questionnaire leadership selection", top_k=5)
    assert any("OPQ" in item.name for item in results)
