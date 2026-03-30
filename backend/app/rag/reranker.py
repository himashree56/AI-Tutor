from typing import List, Optional, Tuple

from sentence_transformers import CrossEncoder

from app.core.config import settings
from app.utils.logger import logger


class RerankerService:
    def __init__(self):
        self.model_name = settings.reranker_model
        self.top_k = settings.reranker_top_k
        self._model: Optional[CrossEncoder] = None

    @property
    def model(self) -> CrossEncoder:
        if self._model is None:
            logger.info(f"Loading reranker model: {self.model_name}")
            self._model = CrossEncoder(self.model_name)
            logger.info("Reranker model loaded")
        return self._model

    def rerank(
        self,
        query: str,
        documents: List[str],
        doc_ids: Optional[List[str]] = None,
        top_k: Optional[int] = None
    ) -> List[Tuple[str, float, str]]:
        if not documents:
            return []

        k = top_k or self.top_k
        
        pairs = [[query, doc] for doc in documents]
        scores = self.model.predict(pairs)
        
        if doc_ids is None:
            doc_ids = [str(i) for i in range(len(documents))]
        
        scored_docs = list(zip(documents, scores, doc_ids))
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        
        return scored_docs[:k]


reranker_service = RerankerService()
