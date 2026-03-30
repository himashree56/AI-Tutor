from typing import List, Optional, Dict, Any
import asyncio
import httpx
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer

from app.core.config import settings
from app.utils.logger import logger


class EmbeddingsService:
    def __init__(self):
        # Default to openrouter if configured, otherwise local
        self.provider = settings.embedding_provider or "openrouter"
        self.model_name = settings.embedding_model
        self.openrouter_model = settings.openrouter_embedding_model
        self.api_key = settings.openrouter_api_key

        # Cache
        self._model: Optional[SentenceTransformer] = None
        self._pinecone: Optional[Pinecone] = None

    # ─── Embedding models ────────────────────────────────────────────────────

    @property
    def local_model(self) -> SentenceTransformer:
        if self._model is None:
            logger.info(f"Loading local embedding model: {self.model_name}")
            self._model = SentenceTransformer(
                settings.embedding_model, device=settings.embedding_device
            )
        return self._model

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if self.provider == "openrouter":
            return await self._embed_openrouter(texts)
        embeddings = self.local_model.encode(
            texts,
            batch_size=settings.embedding_batch_size,
            convert_to_numpy=True,
        )
        return embeddings.tolist()

    async def embed_query(self, query: str) -> List[float]:
        if self.provider == "openrouter":
            results = await self._embed_openrouter([query])
            return results[0]
        embedding = self.local_model.encode(query, convert_to_numpy=True)
        return embedding.tolist()

    async def _embed_openrouter(self, texts: List[str]) -> List[List[float]]:
        if not self.api_key or "your_openrouter_api_key_here" in self.api_key:
            raise ValueError("OpenRouter API key is missing for embeddings")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {"model": self.openrouter_model, "input": texts}

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    "https://openrouter.ai/api/v1/embeddings",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                if "data" not in data:
                    logger.error(f"OpenRouter embedding unexpected response: {data}")
                    raise ValueError(f"OpenRouter embedding unexpected response: {data}")
                return [item["embedding"] for item in data["data"]]
            except Exception as e:
                logger.error(f"OpenRouter embedding error: {e}")
                raise

    # ─── Pinecone Client ─────────────────────────────────────────────────────

    @property
    def pinecone_index(self):
        if self._pinecone is None:
            logger.info("Connecting to Pinecone...")
            if not settings.pinecone_api_key or settings.pinecone_api_key == "your_pinecone_api_key":
                logger.error("PINECONE_API_KEY is not set or invalid!")
            self._pinecone = Pinecone(api_key=settings.pinecone_api_key)
        return self._pinecone.Index(settings.pinecone_index_name)

    # ─── CRUD operations ──────────────────────────────────────────────────────

    async def upsert_chunks(
        self,
        ids: List[str],
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]],
    ) -> int:
        """Upsert chunks into Pinecone. Returns number of chunks written."""
        vectors = []
        for i in range(len(ids)):
            meta = metadatas[i].copy()
            meta["text"] = texts[i]
            vectors.append({
                "id": ids[i],
                "values": embeddings[i],
                "metadata": meta
            })
        
        batch_size = 100
        count = 0
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            await asyncio.to_thread(self.pinecone_index.upsert, vectors=batch)
            count += len(batch)
        return count

    async def delete_by_source(self, source_name: str) -> int:
        """Delete all chunks belonging to a source document."""
        try:
            await asyncio.to_thread(
                self.pinecone_index.delete,
                filter={"source": {"$eq": source_name}}
            )
            return 1
        except Exception as e:
            logger.error(f"Pinecone delete error: {e}")
            return 0

    async def vector_search(
        self, query_embedding: List[float], top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """Run Pinecone query and return matching documents with scores."""
        try:
            response = await asyncio.to_thread(
                self.pinecone_index.query,
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            results = []
            for match in response.matches:
                meta = match.metadata or {}
                text = meta.get("text", "")
                
                # Exclude the implicit text from metadata dictionary logic
                clean_meta = {k: v for k, v in meta.items() if k != "text"}
                
                results.append({
                    "_id": match.id,
                    "text": text,
                    "metadata": clean_meta,
                    "score": match.score,
                })
            return results
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []

    async def count_documents(self) -> int:
        try:
            stats = await asyncio.to_thread(self.pinecone_index.describe_index_stats)
            return stats.total_vector_count
        except Exception as e:
            logger.error(f"Failed to get index stats: {e}")
            return 0

    async def drop_collection(self):
        """Drop all vectors in the collection (full reset)."""
        try:
            await asyncio.to_thread(self.pinecone_index.delete, delete_all=True)
            logger.info(f"Collection '{settings.pinecone_index_name}' content deleted.")
        except Exception as e:
            logger.error(f"Pinecone drop collection error: {e}")

    def close(self):
        # Pinecone doesn't require explicit closure
        self._pinecone = None


embeddings_service = EmbeddingsService()
