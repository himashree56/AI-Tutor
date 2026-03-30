from typing import List, Dict, Any, AsyncGenerator, Optional
from dataclasses import dataclass

from app.rag.embeddings import embeddings_service
from app.rag.retriever import retriever_service, RetrievedChunk
from app.rag.prompt_builder import prompt_builder
from app.llm.local_model import llm_service
from app.memory.session_memory import memory_service
from app.core.config import settings
from app.utils.logger import logger


@dataclass
class ChatResponse:
    answer: str
    sources: List[Dict[str, Any]]
    retrieved_chunks: List[RetrievedChunk]
    latency_ms: float


class RAGPipeline:
    def __init__(self):
        self.retriever = retriever_service
        self.prompt_builder = prompt_builder
        self.llm = llm_service
        self.memory = memory_service

    async def process_query(
        self,
        query: str,
        session_id: str,
        top_k: Optional[int] = None,
        use_reranker: bool = True
    ) -> ChatResponse:
        import time
        start_time = time.time()
        
        retrieved_chunks = await self.retriever.retrieve(
            query=query,
            top_k=top_k or settings.retrieval_top_k,
            use_reranker=use_reranker
        )
        
        history = self.memory.get_conversation_history(session_id)
        
        prompt = self.prompt_builder.build_rag_prompt(
            query=query,
            retrieved_chunks=retrieved_chunks,
            history=history
        )
        
        answer = await self.llm.generate(prompt)
        
        sources = self.prompt_builder.extract_sources(retrieved_chunks)
        
        self.memory.add_message(session_id, "user", query)
        self.memory.add_message(session_id, "assistant", answer)
        
        latency_ms = (time.time() - start_time) * 1000
        
        logger.info(
            f"Query processed in {latency_ms:.2f}ms, "
            f"retrieved {len(retrieved_chunks)} chunks"
        )
        
        return ChatResponse(
            answer=answer,
            sources=sources,
            retrieved_chunks=retrieved_chunks,
            latency_ms=latency_ms
        )

    async def stream_query(
        self,
        query: str,
        session_id: str,
        top_k: Optional[int] = None,
        use_reranker: bool = True
    ) -> AsyncGenerator[str, None]:
        retrieved_chunks = await self.retriever.retrieve(
            query=query,
            top_k=top_k or settings.retrieval_top_k,
            use_reranker=use_reranker
        )
        
        history = self.memory.get_conversation_history(session_id)
        
        prompt = self.prompt_builder.build_rag_prompt(
            query=query,
            retrieved_chunks=retrieved_chunks,
            history=history
        )
        
        full_response = ""
        async for token in self.llm.stream_generate(prompt):
            full_response += token
            yield token
        
        self.memory.add_message(session_id, "user", query)
        self.memory.add_message(session_id, "assistant", full_response)
        
        logger.info(f"Stream completed, session: {session_id}")


rag_pipeline = RAGPipeline()
