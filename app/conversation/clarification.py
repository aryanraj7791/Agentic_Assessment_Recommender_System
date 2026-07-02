"""Clarification question manager."""

from __future__ import annotations

from app.conversation.constraints import HiringConstraints
from app.conversation.state import ConversationState


class ClarificationManager:
    def build_question(self, state: ConversationState, constraints: HiringConstraints) -> str:
        text = state.latest_user_message.lower()

        if constraints.role == "contact_center":
            return "Before I shape the stack — what language are the calls in?"
        if constraints.role == "healthcare" and "spanish" in text:
            return (
                "Some healthcare knowledge tests are English-only while personality measures support Spanish. "
                "Are your candidates functionally bilingual for a hybrid English-knowledge / Spanish-personality battery?"
            )

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
        if "java" in text:
            return (
            "Thanks! Could you clarify whether this is a graduate, junior, mid-level, or senior Java role? "
            "Also, is it primarily backend, full-stack, or another type of Java development?"
            )

        if "python" in text:
            return (
                "Could you tell me whether this is an entry-level, mid-level, or senior Python role? "
                "Also, what type of work is involved (backend, data science, automation, etc.)?"
            )
        
        if constraints.role:
            return (
                f"Thanks! I understand you're hiring for a {constraints.role.replace('_', ' ')} role. "
                "Could you clarify the seniority level (graduate, junior, mid, or senior) "
                "and any key technical skills or competencies you'd like to assess?"
            )

        return (
            "Happy to help. To recommend the right SHL assessments, could you share the role title, "
            "the seniority level, and the main technical skills or competencies you want to assess?"
        )
