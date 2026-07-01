import pytest

from app.config import Settings
from app.conversation.constraints import ConstraintExtractor
from app.conversation.intent import Intent, IntentDetector
from app.conversation.state import reconstruct_state
from app.models import ChatMessage


@pytest.fixture
def settings():
    return Settings(llm_provider="mock", use_reranker=False)


def test_intent_detects_vague_query():
    messages = [ChatMessage(role="user", content="We need a solution for senior leadership.")]
    state = reconstruct_state(messages)
    intent = IntentDetector().detect(state)
    assert intent == Intent.CLARIFY


def test_intent_detects_compare():
    messages = [
        ChatMessage(role="user", content="What is the difference between OPQ and GSA?"),
    ]
    state = reconstruct_state(messages)
    intent = IntentDetector().detect(state)
    assert intent == Intent.COMPARE


def test_intent_detects_refusal():
    messages = [ChatMessage(role="user", content="Are we legally required under HIPAA to test all staff?")]
    state = reconstruct_state(messages)
    intent = IntentDetector().detect(state)
    assert intent == Intent.REFUSE


def test_constraint_extractor_finds_java_skills():
    messages = [
        ChatMessage(role="user", content="Hiring senior Java developer with Spring, SQL, AWS, and Docker."),
    ]
    state = reconstruct_state(messages)
    constraints = ConstraintExtractor().extract(state)
    assert "java" in constraints.skills
    assert "spring" in constraints.skills
    assert constraints.seniority == "senior"


def test_state_reconstruction_turn_count():
    messages = [
        ChatMessage(role="user", content="Hello"),
        ChatMessage(role="assistant", content="Hi"),
        ChatMessage(role="user", content="Need Java tests"),
    ]
    state = reconstruct_state(messages)
    assert state.turn_count == 3
    assert state.latest_user_message == "Need Java tests"
