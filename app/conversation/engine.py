"""Main conversation engine coordinating all subsystems."""

from __future__ import annotations

from loguru import logger

from app.catalog.loader import Assessment, Catalog
from app.config import Settings
from app.conversation.clarification import ClarificationManager
from app.conversation.comparison import ComparisonEngine
from app.conversation.constraints import ConstraintExtractor
from app.conversation.intent import Intent, IntentDetector
from app.conversation.recommendation import RecommendationEngine
from app.conversation.state import ConversationState, reconstruct_state
from app.conversation.validation import ResponseValidator
from app.llm.base import LLMProvider
from app.models import ChatMessage, ChatResponse
from app.retrieval.base import Retriever

SYSTEM_PROMPT = """You are an SHL assessment recommender. Only discuss SHL Individual Test Solutions.
Write concise, professional replies. Never invent products or URLs.
When asked legal or off-topic questions, refuse politely.
Return JSON: {"reply": "..."}"""


class ConversationEngine:
    def __init__(
        self,
        catalog: Catalog,
        retriever: Retriever,
        llm: LLMProvider,
        settings: Settings,
    ):
        self.catalog = catalog
        self.retriever = retriever
        self.llm = llm
        self.settings = settings
        self.intent_detector = IntentDetector()
        self.constraint_extractor = ConstraintExtractor()
        self.clarification_manager = ClarificationManager()
        self.recommendation_engine = RecommendationEngine(catalog, retriever)
        self.comparison_engine = ComparisonEngine(catalog)
        self.validator = ResponseValidator(catalog, settings.max_recommendations)

    async def handle(self, messages: list[ChatMessage]) -> ChatResponse:
        state = reconstruct_state(messages)
        constraints = self.constraint_extractor.extract(state)
        intent = self.intent_detector.detect(state)
        logger.info("Detected intent={} turn={}", intent.value, state.turn_count)

        if intent == Intent.REFUSE:
            return self._refuse(state)

        if intent == Intent.CLARIFY:
            reply = self.clarification_manager.build_question(state, constraints)
            llm_reply = await self._llm_reply(state, reply)
            return self.validator.build_response(llm_reply, [], False, include_recommendations=False)

        retrieved = self.retriever.search(state.full_text, top_k=self.settings.max_recommendations)

        if intent == Intent.COMPARE:
            comparison = self.comparison_engine.compare(state, retrieved)
            llm_reply = await self._llm_reply(state, comparison)
            prior = self.catalog.resolve_references(state.prior_shortlist_names) or retrieved
            return self.validator.build_response(
                llm_reply,
                prior,
                end_of_conversation=False,
                include_recommendations=state.has_prior_shortlist,
            )

        assessments: list[Assessment]
        end = state.user_confirmed

        if intent == Intent.REFINE:
            assessments = self.recommendation_engine.refine(state, constraints, self.settings.max_recommendations)
            reply = "Updated shortlist based on your changes."
        elif intent == Intent.CONFIRM:
            assessments = self.catalog.resolve_references(state.prior_shortlist_names) or retrieved
            reply = "Confirmed — here is your final SHL shortlist from the catalog."
            end = True
        else:
            assessments = self.recommendation_engine.recommend(state, constraints, self.settings.max_recommendations)
            reply = self._format_recommendation_reply(assessments, constraints)

        llm_reply = await self._llm_reply(state, reply, assessments)
        return self.validator.build_response(
            llm_reply,
            assessments,
            end_of_conversation=end,
            include_recommendations=intent in {Intent.RECOMMEND, Intent.REFINE, Intent.CONFIRM},
        )

    async def _llm_reply(
        self,
        state: ConversationState,
        fallback: str,
        assessments: list[Assessment] | None = None,
    ) -> str:
        context = ""
        if assessments:
            context = "\n".join(
                f"- {item.name}: {item.description[:180]}" for item in assessments[:8]
            )
        user_prompt = (
            f"Conversation:\n{state.full_text}\n\n"
            f"Draft reply:\n{fallback}\n\n"
            f"Catalog context:\n{context}\n\n"
            "Return JSON with a polished reply field only."
        )
        payload = await self.llm.generate_json(SYSTEM_PROMPT, user_prompt)
        return str(payload.get("reply") or fallback).strip()

    def _refuse(self, state: ConversationState) -> ChatResponse:
        text = state.latest_user_message.lower()
        if any(w in text for w in ("legal", "required", "regulatory", "hipaa")):
            reply = (
                "Those are legal compliance questions outside what I can advise on. "
                "I can help you select SHL assessments, but not interpret regulatory obligations."
            )
        else:
            reply = (
                "I can only help with selecting SHL assessments from the official product catalog. "
                "Tell me about the role, seniority, and skills you want to assess."
            )
        return self.validator.build_response(reply, [], False, include_recommendations=False)

    @staticmethod
    def _format_recommendation_reply(assessments: list[Assessment], constraints) -> str:
        if not assessments:
            return "I couldn't find a confident match yet — could you share a bit more about the role?"
        lines = ["Based on your requirements, here are SHL assessments from the catalog:"]
        for idx, item in enumerate(assessments, start=1):
            lines.append(f"{idx}. {item.name} ({item.test_type})")
        if "rust" in constraints.skills:
            lines.append(
                "Note: there is no Rust-specific test in the catalog — the closest options are listed above."
            )
        return "\n".join(lines)
