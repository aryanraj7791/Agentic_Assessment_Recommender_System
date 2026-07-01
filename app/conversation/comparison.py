"""Catalog-grounded product comparison."""

from __future__ import annotations

import re

from app.catalog.loader import Assessment, Catalog
from app.conversation.state import ConversationState


class ComparisonEngine:
    def __init__(self, catalog: Catalog):
        self.catalog = catalog

    def compare(self, state: ConversationState, candidates: list[Assessment]) -> str:
        mentioned = self._extract_compared_products(state.latest_user_message)
        items = [self.catalog.get_by_name(name) for name in mentioned]
        items = [item for item in items if item is not None]

        if len(items) < 2 and len(candidates) >= 2:
            items = candidates[:2]
        if len(items) < 2:
            return (
                "I can compare SHL catalog products when you name two assessments. "
                "Which products would you like compared?"
            )

        left, right = items[0], items[1]
        return (
            f"**{left.name}** ({', '.join(left.keys) or 'N/A'}) focuses on: {left.description}\n\n"
            f"**{right.name}** ({', '.join(right.keys) or 'N/A'}) focuses on: {right.description}\n\n"
            "Both are distinct catalog products — choose based on whether you need the broader instrument "
            "or the specialized report/view."
        )

    @staticmethod
    def _extract_compared_products(text: str) -> list[str]:
        patterns = [
            r"difference between (.+?) and (.+?)[\?\.]",
            r"difference between (.+?) vs (.+?)[\?\.]",
            r"compare (.+?) and (.+?)[\?\.]",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return [match.group(1).strip(), match.group(2).strip()]
        return []
