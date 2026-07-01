import pytest

from app.config import Settings
from app.conversation.engine import ConversationEngine
from app.models import ChatMessage
from app.startup import initialize_app


@pytest.fixture(scope="module")
def engine():
    settings = Settings(
        llm_provider="mock",
        use_reranker=False,
        retrieval_mode="keyword",
        lazy_init=False,
        catalog_path="data/shl_product_catalog.json",
    )
    return initialize_app(settings)


@pytest.mark.asyncio
async def test_graduate_trainee_flow(engine: ConversationEngine):
    response = await engine.handle(
        [
            ChatMessage(
                role="user",
                content="We run a graduate management trainee scheme. Need cognitive, personality, and SJT.",
            )
        ]
    )
    assert response.recommendations
    names = [item.name for item in response.recommendations]
    assert any("Verify" in name for name in names)


@pytest.mark.asyncio
async def test_contact_center_clarifies_first(engine: ConversationEngine):
    response = await engine.handle(
        [
            ChatMessage(
                role="user",
                content="We're screening 500 entry-level contact centre agents. What should we use?",
            )
        ]
    )
    assert response.recommendations == []
    assert "language" in response.reply.lower() or "share" in response.reply.lower()
