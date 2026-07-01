import pytest

from app.config import Settings
from app.retrieval.keyword_search import KeywordSearch
from app.startup import initialize_app


@pytest.fixture(scope="module")
def retriever():
    settings = Settings(
        llm_provider="mock",
        use_reranker=False,
        retrieval_mode="keyword",
        lazy_init=False,
        catalog_path="data/shl_product_catalog.json",
    )
    initialize_app(settings)
    from app.startup import state

    assert state.catalog is not None
    assert state.retriever is not None
    return state.retriever


def test_retrieval_finds_java_assessment(retriever: KeywordSearch):
    results = retriever.search("Java developer Spring SQL backend", top_k=5)
    assert results
    joined = " ".join(item.name.lower() for item in results)
    assert "java" in joined or "spring" in joined


def test_retrieval_finds_opq(retriever: KeywordSearch):
    results = retriever.search("personality questionnaire leadership selection", top_k=5)
    assert any("OPQ" in item.name for item in results)
