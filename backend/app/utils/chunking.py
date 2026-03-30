from typing import List, Dict, Any, Tuple
import re

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import settings
from app.utils.logger import logger


class TextChunker:
    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None
    ):
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
        
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
            keep_separator=False
        )

    def chunk_text(
        self,
        text: str,
        source_name: str = "unknown",
        metadata: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        chunks = self.splitter.split_text(text)
        
        chunk_docs = []
        for i, chunk in enumerate(chunks):
            if not chunk.strip():
                continue
            
            chunk_id = f"{source_name}_chunk_{i}"
            
            doc = {
                "id": chunk_id,
                "text": chunk,
                "metadata": {
                    "source": source_name,
                    "chunk_id": i,
                    "total_chunks": len(chunks),
                    **(metadata or {})
                }
            }
            chunk_docs.append(doc)
        
        logger.info(f"Created {len(chunk_docs)} chunks from text")
        return chunk_docs

    def chunk_texts_with_pages(
        self,
        page_texts: List[Tuple[int, str]],
        source_name: str = "unknown"
    ) -> List[Dict[str, Any]]:
        all_chunks = []
        global_idx = 0  # Running counter across ALL pages to ensure unique IDs

        for page_num, page_text in page_texts:
            raw_chunks = self.splitter.split_text(page_text)

            for chunk_text in raw_chunks:
                if not chunk_text.strip():
                    continue

                chunk_id = f"{source_name}_chunk_{global_idx}"
                doc = {
                    "id": chunk_id,
                    "text": chunk_text,
                    "metadata": {
                        "source": source_name,
                        "chunk_id": global_idx,
                        "page": page_num,
                        "total_pages": len(page_texts),
                    }
                }
                all_chunks.append(doc)
                global_idx += 1

        logger.info(f"Created {len(all_chunks)} chunks from {len(page_texts)} pages for '{source_name}'")
        return all_chunks


chunker = TextChunker()
