from typing import List, Dict, Any, Optional, AsyncGenerator
from dataclasses import dataclass

from app.rag.pipeline import rag_pipeline
from app.memory.session_memory import memory_service
from app.utils.logger import logger


@dataclass
class ChatResult:
    answer: str
    sources: List[Dict[str, Any]]
    session_id: str
    latency_ms: float


class ChatService:
    def __init__(self):
        self.rag_pipeline = rag_pipeline
        self.memory = memory_service

    async def chat(
        self,
        query: str,
        session_id: str,
        top_k: Optional[int] = None,
        use_reranker: bool = True
    ) -> ChatResult:
        self.memory.create_session(session_id)
        
        response = await self.rag_pipeline.process_query(
            query=query,
            session_id=session_id,
            top_k=top_k,
            use_reranker=use_reranker
        )
        
        return ChatResult(
            answer=response.answer,
            sources=response.sources,
            session_id=session_id,
            latency_ms=response.latency_ms
        )

    async def stream_chat(
        self,
        query: str,
        session_id: str,
        top_k: Optional[int] = None,
        use_reranker: bool = True
    ) -> AsyncGenerator[str, None]:
        self.memory.create_session(session_id)
        
        async for token in self.rag_pipeline.stream_query(
            query=query,
            session_id=session_id,
            top_k=top_k,
            use_reranker=use_reranker
        ):
            yield token

    def get_history(self, session_id: str) -> List[Dict]:
        return self.memory.get_messages(session_id)

    def clear_history(self, session_id: str):
        self.memory.clear_session(session_id)


chat_service = ChatService()
