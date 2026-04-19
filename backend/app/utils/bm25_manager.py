import os
import pickle
import numpy as np
from typing import List, Dict, Any, Optional
from rank_bm25 import BM25Okapi
from app.utils.logger import logger
from app.core.config import settings

class BM25Manager:
    def __init__(self, index_dir: str = "./data/bm25"):
        self.index_dir = index_dir
        os.makedirs(self.index_dir, exist_ok=True)
        self.indexes: Dict[str, BM25Okapi] = {}
        self.corpus: Dict[str, List[Dict[str, Any]]] = {}

    def _get_index_path(self, source_name: str) -> str:
        return os.path.join(self.index_dir, f"{source_name}.pkl")

    def index_documents(self, source_name: str, chunks: List[Dict[str, Any]]):
        """
        Creates a BM25 index for a specific source document.
        chunks: List of dictionaries with 'text', 'id', 'metadata'
        """
        try:
            texts = [c["text"] for c in chunks]
            tokenized_corpus = [doc.lower().split() for doc in texts]
            
            bm25 = BM25Okapi(tokenized_corpus)
            
            # Save to disk
            data = {
                "bm25": bm25,
                "chunks": chunks
            }
            
            with open(self._get_index_path(source_name), "wb") as f:
                pickle.dump(data, f)
            
            self.indexes[source_name] = bm25
            self.corpus[source_name] = chunks
            
            logger.info(f"BM25 index created and saved for '{source_name}' ({len(chunks)} chunks)")
        except Exception as e:
            logger.error(f"Failed to create BM25 index for {source_name}: {e}")

    def load_index(self, source_name: str) -> bool:
        """Loads a BM25 index from disk if it exists."""
        path = self._get_index_path(source_name)
        if os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    data = pickle.load(f)
                    self.indexes[source_name] = data["bm25"]
                    self.corpus[source_name] = data["chunks"]
                return True
            except Exception as e:
                logger.error(f"Failed to load BM25 index for {source_name}: {e}")
        return False

    def search(self, query: str, top_k: int = 10, source_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search across all loaded indexes.
        If source_filter is provided, only searches that source.
        """
        tokenized_query = query.lower().split()
        all_results = []

        # Ensure all available indexes are loaded into memory if not already
        if not source_filter:
            for file in os.listdir(self.index_dir):
                if file.endswith(".pkl"):
                    s_name = file.replace(".pkl", "")
                    if s_name not in self.indexes:
                        self.load_index(s_name)
        else:
            if source_filter not in self.indexes:
                self.load_index(source_filter)

        sources_to_search = [source_filter] if source_filter else list(self.indexes.keys())

        for s_name in sources_to_search:
            if s_name not in self.indexes:
                continue
            
            bm25 = self.indexes[s_name]
            chunks = self.corpus[s_name]
            
            scores = bm25.get_scores(tokenized_query)
            
            for i, score in enumerate(scores):
                if score > 0:
                    res = chunks[i].copy()
                    res["bm25_score"] = float(score)
                    res["source"] = s_name
                    all_results.append(res)

        # Sort by BM25 score and limit
        all_results.sort(key=lambda x: x["bm25_score"], reverse=True)
        return all_results[:top_k]

    def delete_index(self, source_name: str):
        path = self._get_index_path(source_name)
        if os.path.exists(path):
            os.remove(path)
        if source_name in self.indexes:
            del self.indexes[source_name]
        if source_name in self.corpus:
            del self.corpus[source_name]

bm25_manager = BM25Manager()
