from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from app.rag.retriever import RetrievedChunk
from app.utils.logger import logger


@dataclass
class EvaluationResult:
    faithfulness: float
    relevance: float
    context_utilization: float
    latency_ms: float
    details: Dict[str, Any]


class EvaluationMetrics:
    def __init__(self):
        self.faithfulness_threshold = 0.5
        self.relevance_threshold = 0.5

    def calculate_context_relevance(
        self,
        query: str,
        retrieved_chunks: List[RetrievedChunk]
    ) -> float:
        if not retrieved_chunks:
            return 0.0
        
        query_words = set(query.lower().split())
        scores = []
        
        for chunk in retrieved_chunks:
            chunk_words = set(chunk.text.lower().split())
            intersection = query_words & chunk_words
            score = len(intersection) / max(len(query_words), 1)
            scores.append(score * chunk.score)
        
        return sum(scores) / len(scores) if scores else 0.0

    def calculate_answer_faithfulness(
        self,
        answer: str,
        retrieved_chunks: List[RetrievedChunk]
    ) -> float:
        if not answer or not retrieved_chunks:
            return 0.0
        
        answer_lower = answer.lower()
        context_text = " ".join(chunk.text.lower() for chunk in retrieved_chunks)
        
        answer_words = set(answer_lower.split())
        context_words = set(context_text.split())
        
        answer_in_context = sum(
            1 for word in answer_words if word in context_words and len(word) > 3
        )
        
        if not answer_words:
            return 0.0
        
        return answer_in_context / len(answer_words)

    def calculate_context_utilization(
        self,
        retrieved_chunks: List[RetrievedChunk],
        answer: str
    ) -> float:
        if not retrieved_chunks:
            return 0.0
        
        answer_lower = answer.lower()
        used_sources = 0
        
        for chunk in retrieved_chunks:
            chunk_words = set(chunk.text.lower().split())
            answer_words = set(answer_lower.split())
            
            overlap = len(chunk_words & answer_words)
            
            if overlap > 5:
                used_sources += 1
        
        return used_sources / len(retrieved_chunks) if retrieved_chunks else 0.0

    def evaluate_rag_response(
        self,
        query: str,
        answer: str,
        retrieved_chunks: List[RetrievedChunk],
        latency_ms: float
    ) -> EvaluationResult:
        context_relevance = self.calculate_context_relevance(query, retrieved_chunks)
        faithfulness = self.calculate_answer_faithfulness(answer, retrieved_chunks)
        context_utilization = self.calculate_context_utilization(retrieved_chunks, answer)
        
        avg_relevance = (
            context_relevance * 0.4 +
            faithfulness * 0.3 +
            context_utilization * 0.3
        )
        
        return EvaluationResult(
            faithfulness=round(faithfulness, 3),
            relevance=round(avg_relevance, 3),
            context_utilization=round(context_utilization, 3),
            latency_ms=round(latency_ms, 2),
            details={
                "context_relevance": round(context_relevance, 3),
                "retrieved_chunks_count": len(retrieved_chunks),
                "avg_chunk_score": round(
                    sum(c.score for c in retrieved_chunks) / len(retrieved_chunks)
                    if retrieved_chunks else 0, 3
                ),
                "answer_length": len(answer.split())
            }
        )


evaluation_metrics = EvaluationMetrics()
