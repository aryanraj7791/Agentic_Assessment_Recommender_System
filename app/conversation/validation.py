"""Response and recommendation validation."""

from __future__ import annotations

from app.catalog.loader import Assessment, Catalog
from app.models import ChatResponse, Recommendation


class ResponseValidator:
    def __init__(self, catalog: Catalog, max_recommendations: int = 10):
        self.catalog = catalog
        self.max_recommendations = max_recommendations

    def validate_recommendations(self, assessments: list[Assessment]) -> list[Recommendation]:
        validated: list[Recommendation] = []
        seen_urls: set[str] = set()

        for item in assessments[: self.max_recommendations]:
            canonical = self.catalog.get_by_id(item.entity_id) or self.catalog.get_by_url(item.url)
            if canonical is None:
                continue
            url_key = canonical.url.rstrip("/")
            if url_key in seen_urls:
                continue
            seen_urls.add(url_key)
            validated.append(
                Recommendation(
                    name=canonical.name,
                    url=canonical.url,
                    test_type=canonical.test_type,
                )
            )
        return validated

    def build_response(
        self,
        reply: str,
        assessments: list[Assessment],
        end_of_conversation: bool,
        include_recommendations: bool,
    ) -> ChatResponse:
        recommendations = self.validate_recommendations(assessments) if include_recommendations else []
        if end_of_conversation and not recommendations:
            end_of_conversation = False
        if not reply.strip():
            reply = "How can I help you select SHL assessments from the catalog?"
        return ChatResponse(
            reply=reply.strip(),
            recommendations=recommendations,
            end_of_conversation=end_of_conversation,
        )
