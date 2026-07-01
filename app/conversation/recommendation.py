"""Rule-assisted recommendation engine backed by retrieval."""

from __future__ import annotations

from app.catalog.loader import Assessment, Catalog
from app.conversation.constraints import HiringConstraints
from app.conversation.state import ConversationState
from app.retrieval.chroma_store import ChromaStore

DEFAULT_PERSONALITY = "Occupational Personality Questionnaire OPQ32r"
DEFAULT_COGNITIVE = "SHL Verify Interactive G+"
DEFAULT_GRADUATE_SJT = "Graduate Scenarios"

ROLE_PRODUCTS: dict[str, list[str]] = {
    "leadership": [
        DEFAULT_PERSONALITY,
        "OPQ Universal Competency Report 2.0",
        "OPQ Leadership Report",
    ],
    "sales": [
        "Global Skills Assessment",
        "Global Skills Development Report",
        DEFAULT_PERSONALITY,
        "OPQ MQ Sales Report",
        "Sales Transformation 2.0 - Individual Contributor",
    ],
    "contact_center": [
        "SVAR - Spoken English (US) (New)",
        "Contact Center Call Simulation (New)",
        "Entry Level Customer Serv-Retail & Contact Center",
        "Customer Service Phone Simulation",
    ],
    "safety": [
        "Dependability and Safety Instrument (DSI)",
        "Manufac. & Indust. - Safety & Dependability 8.0",
        "Workplace Health and Safety (New)",
    ],
    "healthcare": [
        "HIPAA (Security)",
        "Medical Terminology (New)",
        "Microsoft Word 365 - Essentials (New)",
        "Dependability and Safety Instrument (DSI)",
        DEFAULT_PERSONALITY,
    ],
    "finance": [
        "SHL Verify Interactive – Numerical Reasoning",
        "Financial Accounting (New)",
        "Basic Statistics (New)",
        DEFAULT_GRADUATE_SJT,
        DEFAULT_PERSONALITY,
    ],
}

SKILL_PRODUCTS: dict[str, list[str]] = {
    "java": ["Core Java (Advanced Level) (New)", "Spring (New)", "SQL (New)"],
    "spring": ["Spring (New)"],
    "sql": ["SQL (New)"],
    "aws": ["Amazon Web Services (AWS) Development (New)"],
    "docker": ["Docker (New)"],
    "rust": [
        "Smart Interview Live Coding",
        "Linux Programming (General)",
        "Networking and Implementation (New)",
    ],
    "excel": ["MS Excel (New)", "Microsoft Excel 365 (New)"],
    "word": ["MS Word (New)", "Microsoft Word 365 (New)"],
}


class RecommendationEngine:
    def __init__(self, catalog: Catalog, store: ChromaStore):
        self.catalog = catalog
        self.store = store

    def recommend(
        self,
        state: ConversationState,
        constraints: HiringConstraints,
        max_items: int = 10,
    ) -> list[Assessment]:
        names = self._rule_based_names(state, constraints)
        retrieved = self.store.search(state.full_text, top_k=max_items)
        resolved = self.catalog.resolve_references(names)
        combined = self._dedupe((resolved or []) + retrieved)
        return combined[:max_items]

        retrieved = self.store.search(state.full_text, top_k=max_items)
        if constraints.wants_personality and DEFAULT_PERSONALITY not in [a.name for a in retrieved]:
            opq = self.catalog.get_by_name(DEFAULT_PERSONALITY)
            if opq and constraints.seniority in {"senior", "mid", "executive", "graduate"}:
                retrieved = [opq, *retrieved]
        return self._dedupe(retrieved)[:max_items]

    def refine(
        self,
        state: ConversationState,
        constraints: HiringConstraints,
        max_items: int = 10,
    ) -> list[Assessment]:
        base = self.catalog.resolve_references(state.prior_shortlist_names)
        updated = self.recommend(state, constraints, max_items=max_items)

        if constraints.drop_items:
            drop_terms = constraints.drop_items
            updated = [
                item
                for item in updated
                if not any(term in item.name.lower() or term in item.description.lower() for term in drop_terms)
            ]

        if not updated and base:
            return base[:max_items]
        return self._dedupe(updated or base)[:max_items]

    def _rule_based_names(self, state: ConversationState, constraints: HiringConstraints) -> list[str]:
        text = state.full_text.lower()
        names: list[str] = []

        def extend(items: list[str]) -> None:
            for item in items:
                if item not in names:
                    names.append(item)

        if constraints.role and constraints.role in ROLE_PRODUCTS:
            extend(ROLE_PRODUCTS[constraints.role])
        if constraints.seniority == "executive" or "senior leadership" in text:
            extend(ROLE_PRODUCTS["leadership"])
        if "rust" in constraints.skills:
            extend(SKILL_PRODUCTS["rust"])
        for skill in ("java", "spring", "sql", "aws", "docker"):
            if skill in constraints.skills and skill not in constraints.drop_items:
                extend(SKILL_PRODUCTS.get(skill, []))
        if "excel" in text and "word" in text:
            if constraints.wants_simulation:
                extend(
                    [
                        "Microsoft Excel 365 (New)",
                        "Microsoft Word 365 (New)",
                        "MS Excel (New)",
                        "MS Word (New)",
                    ]
                )
            else:
                extend(["MS Excel (New)", "MS Word (New)"])
        if constraints.seniority == "graduate" and "management trainee" in text:
            extend([DEFAULT_COGNITIVE, DEFAULT_GRADUATE_SJT])
        if constraints.wants_sjt:
            extend([DEFAULT_GRADUATE_SJT])
        if constraints.wants_cognitive and "verify" not in constraints.drop_items:
            extend([DEFAULT_COGNITIVE])
        if constraints.wants_personality and "opq" not in constraints.drop_items:
            extend([DEFAULT_PERSONALITY])
        if "industrial" in text and constraints.role == "safety":
            names = [
                n
                for n in names
                if "DSI" not in n or "8.0" in n
            ] or ["Manufac. & Indust. - Safety & Dependability 8.0", "Workplace Health and Safety (New)"]
        if "drop the opq" in text or "drop opq" in text:
            names = [n for n in names if "OPQ" not in n or "Report" in n]
        return names

    @staticmethod
    def _dedupe(items: list[Assessment]) -> list[Assessment]:
        seen: set[str] = set()
        unique: list[Assessment] = []
        for item in items:
            if item.entity_id not in seen:
                seen.add(item.entity_id)
                unique.append(item)
        return unique
