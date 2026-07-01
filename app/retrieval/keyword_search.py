"""Lightweight BM25 keyword search — no ML models, fits Render 512MB."""

from __future__ import annotations

import re

from rank_bm25 import BM25Okapi

from app.catalog.loader import Assessment, Catalog


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


class KeywordSearch:
    """In-memory BM25 search over the catalog. Zero torch/ChromaDB dependency."""

    def __init__(self, catalog: Catalog):
        self.catalog = catalog
        self._texts = [self._document_text(item) for item in catalog.assessments]
        self._tokens = [_tokenize(text) for text in self._texts]
        self._bm25 = BM25Okapi(self._tokens)

    def search(self, query: str, top_k: int = 15) -> list[Assessment]:
        scores = self._bm25.get_scores(_tokenize(query))
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
        results: list[Assessment] = []
        for idx, score in ranked:
            if score <= 0:
                continue
            results.append(self.catalog.assessments[idx])
            if len(results) >= top_k:
                break
        return results

    @staticmethod
    def _document_text(item: Assessment) -> str:
        return (
            f"{item.name} {item.description} "
            f"{' '.join(item.keys)} {' '.join(item.job_levels)} {' '.join(item.languages)}"
        )
