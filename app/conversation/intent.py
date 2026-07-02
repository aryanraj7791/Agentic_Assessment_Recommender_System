"""Intent detection for conversation routing."""

from __future__ import annotations

import re
from enum import Enum

from app.conversation.state import ConversationState


class Intent(str, Enum):
    CLARIFY = "clarify"
    RECOMMEND = "recommend"
    REFINE = "refine"
    COMPARE = "compare"
    REFUSE = "refuse"
    CONFIRM = "confirm"


OFF_TOPIC_PATTERNS = [
    r"\bignore (all )?previous instructions\b",
    r"\bsystem prompt\b",
    r"\bjailbreak\b",
    r"\bwrite me a poem\b",
]

LEGAL_PATTERNS = [
    r"\blegally required\b",
    r"\bregulatory obligation\b",
    r"\bdoes this test satisfy\b",
    r"\bare we required\b",
]

VAGUE_PATTERNS = [
    r"^i need an assessment\.?$",
    r"^we need a solution\b",
    r"^help me choose\b",
    r"^i need a test\b",
    r"^recommend an assessment\b",
]


class IntentDetector:
    def detect(self, state: ConversationState) -> Intent:
        text = state.latest_user_message.lower()

        if any(re.search(p, text) for p in OFF_TOPIC_PATTERNS):
            return Intent.REFUSE

        if any(re.search(p, text) for p in LEGAL_PATTERNS):
            return Intent.REFUSE

        if state.user_confirmed and state.has_prior_shortlist:
            return Intent.CONFIRM

        if self._is_compare_request(text):
            return Intent.COMPARE

        if self._is_refinement(text, state):
            return Intent.REFINE

        if self._needs_clarification(state):
            return Intent.CLARIFY

        return Intent.RECOMMEND

    @staticmethod
    def _is_compare_request(text: str) -> bool:
        return any(
            phrase in text
            for phrase in (
                "difference between",
                "what's the difference",
                "what is the difference",
                "compare ",
                " vs ",
                " versus ",
            )
        )

    @staticmethod
    def _is_refinement(text: str, state: ConversationState) -> bool:
        if not state.has_prior_shortlist:
            return False

        return bool(
            re.search(
                r"\b(add|drop|remove|replace|update|also add|skip)\b",
                text,
            )
        )

    @staticmethod
    def _needs_clarification(state: ConversationState) -> bool:
        text = state.latest_user_message.strip().lower()
        full = state.full_text.lower()

        # Allow clarification for up to 4 turns
        if state.turn_count > 4:
            return False

        # Generic vague requests
        if any(re.search(p, text) for p in VAGUE_PATTERNS):
            return True

        # Contact center language clarification
        if ("contact centre" in text or "contact center" in text):
            if not any(
                lang in full
                for lang in (
                    "english us",
                    "english uk",
                    " us.",
                    " us,",
                    " uk.",
                    "australian",
                    "indian accent",
                )
            ):
                return True

        # Existing vague solution logic
        vague_markers = (
            "solution for",
            "need a solution",
        )

        specific_markers = (
            "java",
            "python",
            "developer",
            "engineer",
            "graduate",
            "contact center",
            "contact centre",
            "sales",
            "hipaa",
            "excel",
            "plant operator",
            "job description",
            "here's the jd",
        )

        if any(v in text for v in vague_markers) and not any(
            s in text for s in specific_markers
        ):
            return True

        # Contact-center follow-up questions
        if "?" in state.latest_user_message:
            question_clarifiers = (
                "backend or frontend",
                "senior ic",
                "which language",
                "selection or development",
            )

            if any(q in text for q in question_clarifiers):
                return True

        # -------------------------------
        # NEW LOGIC
        # -------------------------------

        role_keywords = (
            "developer",
            "engineer",
            "manager",
            "analyst",
            "sales",
            "finance",
            "accountant",
            "operator",
            "executive",
            "consultant",
            "designer",
            "intern",
            "graduate",
            "leader",
            "architect",
            "administrator",
            "scientist",
            "tester",
            "qa",
            "support",
            "technician",
        )

        skill_keywords = (
            "java",
            "python",
            "sql",
            "aws",
            "docker",
            "react",
            "spring",
            "excel",
            "linux",
            "rust",
            "c++",
            "c#",
            "javascript",
            "typescript",
            "node",
            "golang",
            "scala",
            "kotlin",
        )

        seniority_keywords = (
            "graduate",
            "entry",
            "junior",
            "mid",
            "senior",
            "lead",
            "principal",
            "executive",
            "experienced",
            "manager",
        )

        has_role = any(word in text for word in role_keywords)
        has_skill = any(word in text for word in skill_keywords)
        has_seniority = any(word in text for word in seniority_keywords)

        # Very generic assessment requests
        if (
            "assessment" in text
            or "test" in text
            or "recommend" in text
        ) and not has_role:
            return True

        # Role present but insufficient information
        if has_role:
            score = int(has_skill) + int(has_seniority)

            if score < 2:
                return True

        return False