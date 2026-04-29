"""
Vector Service (FAISS)
Semantic search for database context.
"""

import os
import json
import logging
import numpy as np
import faiss
from openai import AsyncOpenAI

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

INDEX_PATH = os.path.join(settings.vector_store_path, "schema_index.faiss")
METADATA_PATH = os.path.join(settings.vector_store_path, "schema_meta.json")


class VectorService:
    def __init__(self):
        self.enabled = settings.has_openai_key
        self.dimension = 3072  # text-embedding-3-large default
        
        if self.enabled:
            self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        
        os.makedirs(settings.vector_store_path, exist_ok=True)
        self.index = self._load_or_create_index()
        self.metadata = self._load_metadata()

    def _load_or_create_index(self):
        if os.path.exists(INDEX_PATH):
            return faiss.read_index(INDEX_PATH)
        return faiss.IndexFlatL2(self.dimension)

    def _load_metadata(self) -> dict:
        if os.path.exists(METADATA_PATH):
            with open(METADATA_PATH, "r") as f:
                return json.load(f)
        return {"items": []}

    def _save(self):
        faiss.write_index(self.index, INDEX_PATH)
        with open(METADATA_PATH, "w") as f:
            json.dump(self.metadata, f)

    async def get_embedding(self, text: str) -> list[float]:
        if not self.enabled:
            return [0.0] * self.dimension
            
        res = await self.client.embeddings.create(
            input=[text],
            model=settings.openai_embedding_model
        )
        return res.data[0].embedding

    async def add_documents(self, documents: list[dict]):
        """docs is list of dict with 'text' and 'meta'."""
        if not self.enabled or not documents:
            return

        texts = [d["text"] for d in documents]
        
        # Get embeddings
        res = await self.client.embeddings.create(
            input=texts,
            model=settings.openai_embedding_model
        )
        embeddings = np.array([item.embedding for item in res.data]).astype('float32')

        # Add to index
        self.index.add(embeddings)
        
        # Save metadata
        for i, doc in enumerate(documents):
            self.metadata["items"].append(doc["meta"])
            
        self._save()

    async def search(self, query: str, k: int = 3) -> list[dict]:
        if not self.enabled or self.index.ntotal == 0:
            return []

        emb = await self.get_embedding(query)
        emb_arr = np.array([emb]).astype('float32')
        
        distances, indices = self.index.search(emb_arr, k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1 and idx < len(self.metadata["items"]):
                results.append({
                    "meta": self.metadata["items"][idx],
                    "distance": float(distances[0][i])
                })
                
        return results

# Singleton
vector_service = VectorService()
