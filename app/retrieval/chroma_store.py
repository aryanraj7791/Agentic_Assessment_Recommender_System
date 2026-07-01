"""ChromaDB persistent vector store."""

from __future__ import annotations

from pathlib import Path

import chromadb
from loguru import logger

from app.catalog.loader import Assessment, Catalog
from app.config import Settings
from app.retrieval.embeddings import EmbeddingService
from app.retrieval.reranker import Reranker

COLLECTION_NAME = "shl_assessments"


class ChromaStore:
    def __init__(
        self,
        catalog: Catalog,
        settings: Settings,
        embeddings: EmbeddingService,
        reranker: Reranker,
    ):
        self.catalog = catalog
        self.settings = settings
        self.embeddings = embeddings
        self.reranker = reranker
        Path(settings.chroma_path).mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=settings.chroma_path)
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    @property
    def is_indexed(self) -> bool:
        return self.collection.count() >= len(self.catalog)

    def build(self) -> None:
        logger.info("Building ChromaDB index for {} assessments", len(self.catalog))
        if self.collection.count() > 0:
            self.client.delete_collection(COLLECTION_NAME)
            self.collection = self.client.get_or_create_collection(
                name=COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"},
            )

        ids: list[str] = []
        documents: list[str] = []
        metadatas: list[dict] = []

        for item in self.catalog.assessments:
            ids.append(item.entity_id)
            documents.append(self._document_text(item))
            metadatas.append(self._metadata(item))

        batch_size = 64
        for start in range(0, len(ids), batch_size):
            end = start + batch_size
            batch_embeddings = self.embeddings.encode(documents[start:end])
            self.collection.add(
                ids=ids[start:end],
                documents=documents[start:end],
                metadatas=metadatas[start:end],
                embeddings=batch_embeddings,
            )

        logger.info("ChromaDB index built with {} documents", self.collection.count())

    def search(self, query: str, top_k: int = 15) -> list[Assessment]:
        query_embedding = self.embeddings.encode_query(query)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k * 2, max(top_k, 20)),
            include=["metadatas", "distances"],
        )

        ids = results.get("ids", [[]])[0]
        candidates = [self.catalog.get_by_id(entity_id) for entity_id in ids]
        candidates = [item for item in candidates if item is not None]
        return self.reranker.rerank(query, candidates, top_k=top_k)

    @staticmethod
    def _document_text(item: Assessment) -> str:
        return f"""
        Assessment Name:
        {item.name}

        Description:
        {item.description}

        Categories:
        {", ".join(item.keys)}

        Job Levels:
        {", ".join(item.job_levels)}

        Languages:
        {", ".join(item.languages)}

        Duration:
        {item.duration}

        Adaptive:
        {item.adaptive}

        Remote:
        {item.remote}

        Test Type:
        {item.test_type}

        URL:
        {item.url}
        """

    @staticmethod
    def _metadata(item: Assessment) -> dict:
        return {
            "entity_id": item.entity_id,
            "name": item.name,
            "url": item.url,
            "test_type": item.test_type,
            "duration": item.duration or "N/A",
            "job_levels": ", ".join(item.job_levels),
            "languages": ", ".join(item.languages),
            "categories": ", ".join(item.keys),
            "description": item.description[:500],
            "remote": item.remote,
            "adaptive": item.adaptive,
        }
