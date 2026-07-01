"""Clarification question manager."""

from __future__ import annotations

from app.conversation.constraints import HiringConstraints
from app.conversation.state import ConversationState


class ClarificationManager:
    def build_question(self, state: ConversationState, constraints: HiringConstraints) -> str:
        text = state.latest_user_message.lower()

        if "leadership" in text or "senior leadership" in text:
            return (
                "Happy to help narrow that down. Who is this meant for — role level, years of experience, "
                "and whether this is for selection or development?"
            )
        if "full-stack" in text or "job description" in text or "here's the jd" in text:
            return (
                "That role spans several skill areas. Is this backend-leaning, frontend-heavy, "
                "or a balanced full-stack role?"
            )
        if constraints.role == "contact_center":
            return "Before I shape the stack — what language are the calls in?"
        if constraints.role == "healthcare" and "spanish" in text:
            return (
                "Some healthcare knowledge tests are English-only while personality measures support Spanish. "
                "Are your candidates functionally bilingual for a hybrid English-knowledge / Spanish-personality battery?"
            )
        return (
            "Happy to help. To recommend the right SHL assessments, could you share the role title, "
            "seniority level, and the main skills or traits you need to measure?"
        )
