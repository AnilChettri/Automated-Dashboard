"""
Vector Service (FAISS)
Semantic search for database context.
"""

import os
import json
import logging
import numpy as np
import faiss
import google.generativeai as genai

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

INDEX_PATH = os.path.join(settings.vector_store_path, "schema_index.faiss")
METADATA_PATH = os.path.join(settings.vector_store_path, "schema_meta.json")


class VectorService:
    def __init__(self):
        self.enabled = settings.has_gemini_key
        self.dimension = 768  # text-embedding-004 default
        
        if self.enabled:
            genai.configure(api_key=settings.gemini_api_key)
        
        os.makedirs(settings.vector_store_path, exist_ok=True)
        self.index = self._load_or_create_index()
        self.metadata = self._load_metadata()

    def _load_or_create_index(self):
        if os.path.exists(INDEX_PATH):
            idx = faiss.read_index(INDEX_PATH)
            if idx.d == self.dimension:
                return idx
            else:
                logger.warning(f"Index dimension mismatch ({idx.d} != {self.dimension}). Recreating index.")
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
            
        res = await genai.embed_content_async(
            model=settings.gemini_embedding_model,
            content=text,
            task_type="retrieval_document"
        )
        return res["embedding"]

    async def add_documents(self, documents: list[dict]):
        """docs is list of dict with 'text' and 'meta'."""
        if not self.enabled or not documents:
            return

        texts = [d["text"] for d in documents]
        
        # Get embeddings
        res = await genai.embed_content_async(
            model=settings.gemini_embedding_model,
            content=texts,
            task_type="retrieval_document"
        )
        embeddings = np.array(res["embedding"]).astype('float32')

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
