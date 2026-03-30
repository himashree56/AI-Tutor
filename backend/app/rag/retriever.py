from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from app.rag.embeddings import embeddings_service
from app.rag.reranker import reranker_service
from app.core.config import settings
from app.utils.logger import logger


@dataclass
class RetrievedChunk:
    id: str
    text: str
    score: float
    metadata: Dict[str, Any]


class RetrieverService:
    def __init__(self):
        self.top_k = settings.retrieval_top_k
        self.score_threshold = settings.retrieval_score_threshold

    async def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        use_reranker: bool = True,
        collection_name: Optional[str] = None,  # kept for API compat, unused
    ) -> List[RetrievedChunk]:
        k = top_k or self.top_k

        query_embedding = await embeddings_service.embed_query(query)

        raw_results = await embeddings_service.vector_search(
            query_embedding=query_embedding,
            top_k=k,
        )

        if not raw_results:
            logger.warning("No documents retrieved from MongoDB vector search")
            return []

        documents = [r["text"] for r in raw_results]
        scores = [float(r.get("score", 0.0)) for r in raw_results]
        ids = [str(r["_id"]) for r in raw_results]
        metadatas = [r.get("metadata", {}) for r in raw_results]

        if use_reranker and len(documents) > 1:
            reranked = reranker_service.rerank(
                query=query,
                documents=documents,
                doc_ids=ids,
                top_k=min(k, settings.reranker_top_k),
            )
            # reranked is List[Tuple[doc_text, score, doc_id]]
            meta_map = {doc_id: meta for doc_id, meta in zip(ids, metadatas)}

            chunks = [
                RetrievedChunk(
                    id=doc_id,
                    text=doc,
                    score=float(score),
                    metadata=meta_map.get(doc_id, {}),
                )
                # Reranker scores (logits) can be negative. 
                # We relax the threshold here as the reranker has already narrowed down from top vector matches.
                for doc, score, doc_id in reranked
                if float(score) >= -5.0 
            ]
        else:
            chunks = [
                RetrievedChunk(
                    id=ids[i],
                    text=documents[i],
                    score=scores[i],
                    metadata=metadatas[i],
                )
                for i, score in enumerate(scores)
                if score >= self.score_threshold
            ]

        logger.info(f"Retrieved {len(chunks)} chunks for query")
        return chunks

    async def get_context_for_query(
        self, query: str, top_k: Optional[int] = None
    ) -> str:
        chunks = await self.retrieve(query, top_k=top_k)
        if not chunks:
            return ""

        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            source = chunk.metadata.get("source", "Unknown")
            page = chunk.metadata.get("page", "N/A")
            context_parts.append(
                f"[Source {i}] (Page {page}, {source}):\n{chunk.text}"
            )

        return "\n\n".join(context_parts)


retriever_service = RetrieverService()
