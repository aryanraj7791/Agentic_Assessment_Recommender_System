"""Constraint extraction from conversation text."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from app.conversation.state import ConversationState


@dataclass
class HiringConstraints:
    skills: set[str] = field(default_factory=set)
    role: str = ""
    seniority: str = ""
    language: str = ""
    industry: str = ""
    wants_personality: bool = True
    wants_cognitive: bool = False
    wants_simulation: bool = False
    wants_sjt: bool = False
    selection: bool = False
    development: bool = False
    drop_items: set[str] = field(default_factory=set)
    add_items: set[str] = field(default_factory=set)


SKILL_TERMS = (
    "java",
    "spring",
    "sql",
    "aws",
    "docker",
    "rest",
    "angular",
    "rust",
    "excel",
    "word",
    "hipaa",
    "python",
    "linux",
    "networking",
    "financial",
    "numerical",
)


class ConstraintExtractor:
    def extract(self, state: ConversationState) -> HiringConstraints:
        text = state.full_text.lower()
        latest = state.latest_user_message.lower()
        constraints = HiringConstraints()

        for term in SKILL_TERMS:
            if term in text:
                constraints.skills.add(term)

        if any(w in text for w in ("graduate", "final-year", "trainee", "management trainee")):
            constraints.seniority = "graduate"
        elif any(w in text for w in ("entry-level", "entry level", "contact centre", "contact center")):
            constraints.seniority = "entry"
        elif any(w in text for w in ("senior", "5+ years", "tech lead")):
            constraints.seniority = "senior"
        elif any(w in text for w in ("mid-level", "mid level", "4 years")):
            constraints.seniority = "mid"
        elif any(w in text for w in ("cxo", "director", "executive", "15 years", "leadership")):
            constraints.seniority = "executive"

        role_map = {
            "sales": ("sales", "re-skill", "talent audit"),
            "contact_center": ("contact centre", "contact center", "call center"),
            "safety": ("plant operator", "chemical facility", "safety-critical"),
            "healthcare": ("healthcare", "patient records", "bilingual"),
            "finance": ("financial analyst", "finance knowledge"),
        }
        for role, markers in role_map.items():
            if any(m in text for m in markers):
                constraints.role = role

        if "english us" in text or re.search(r"\bus\b", latest):
            constraints.language = "english_us"
        if "spanish" in text or "bilingual" in text:
            constraints.language = "spanish"

        constraints.wants_personality = not any(
            p in text for p in ("drop opq", "remove opq", "skip personality", "without opq")
        )
        constraints.wants_cognitive = any(
            w in text for w in ("cognitive", "verify g+", "reasoning ability")
        ) or constraints.seniority in {"senior", "executive", "graduate"}
        constraints.wants_simulation = "simulation" in text
        constraints.wants_sjt = any(
            w in text for w in ("situational judgement", "situational judgment", "graduate scenarios")
        )
        constraints.selection = "selection" in text
        constraints.development = any(w in text for w in ("development", "re-skill", "developmental feedback"))

        for item in ("rest", "opq", "verify g+", "angular", "docker", "aws"):
            if re.search(rf"\b(drop|remove)\s+{re.escape(item)}\b", text):
                constraints.drop_items.add(item)
        for item in ("personality", "aws", "docker", "simulation", "graduate scenarios", "verify g+"):
            if re.search(rf"\b(add|include)\s+{re.escape(item)}\b", text):
                constraints.add_items.add(item)

        return constraints
