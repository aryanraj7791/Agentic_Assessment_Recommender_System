"""Retriever protocol."""

from __future__ import annotations

from typing import Protocol

from app.catalog.loader import Assessment


class Retriever(Protocol):
    def search(self, query: str, top_k: int = 15) -> list[Assessment]: ...
