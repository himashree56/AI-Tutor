from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from app.rag.embeddings import embeddings_service
from app.rag.pipeline import rag_pipeline
from app.memory.session_memory import memory_service
from app.utils.logger import logger
from app.utils.pdf_processor import pdf_processor
from app.utils.chunking import chunker


@dataclass
class IngestionResult:
    success: bool
    chunks_added: int
    source_name: str
    error: Optional[str] = None


class IngestionService:
    def __init__(self):
        self.collection_name = "documents"

    async def ingest_document(
        self,
        file_content: bytes,
        file_name: str,
    ) -> IngestionResult:
        try:
            source_name = file_name.replace(".pdf", "")

            chunks = pdf_processor.process_pdf(
                pdf_bytes=file_content,
                source_name=source_name,
            )

            if not chunks:
                return IngestionResult(
                    success=False,
                    chunks_added=0,
                    source_name=source_name,
                    error="No text extracted from document",
                )

            texts = [chunk["text"] for chunk in chunks]
            ids = [chunk["id"] for chunk in chunks]
            metadatas = [chunk["metadata"] for chunk in chunks]

            embeddings = await embeddings_service.embed_texts(texts)

            # Delete existing chunks for this source then upsert fresh ones
            deleted = await embeddings_service.delete_by_source(source_name)
            if deleted:
                logger.info(f"Removed {deleted} stale chunks for '{source_name}'")

            await embeddings_service.upsert_chunks(
                ids=ids,
                texts=texts,
                embeddings=embeddings,
                metadatas=metadatas,
            )

            logger.info(f"Ingested {len(chunks)} chunks from '{source_name}'")

            return IngestionResult(
                success=True,
                chunks_added=len(chunks),
                source_name=source_name,
            )

        except Exception as e:
            logger.error(f"Ingestion error for {file_name}: {e}")
            return IngestionResult(
                success=False,
                chunks_added=0,
                source_name=file_name,
                error=str(e),
            )

    async def ingest_text(
        self,
        text: str,
        source_name: str = "text_input",
    ) -> IngestionResult:
        try:
            chunks = chunker.chunk_text(text, source_name=source_name)

            if not chunks:
                return IngestionResult(
                    success=False,
                    chunks_added=0,
                    source_name=source_name,
                    error="No text to ingest",
                )

            texts = [chunk["text"] for chunk in chunks]
            ids = [chunk["id"] for chunk in chunks]
            metadatas = [chunk["metadata"] for chunk in chunks]

            embeddings = await embeddings_service.embed_texts(texts)

            await embeddings_service.upsert_chunks(
                ids=ids,
                texts=texts,
                embeddings=embeddings,
                metadatas=metadatas,
            )

            logger.info(f"Ingested {len(chunks)} chunks from text source '{source_name}'")

            return IngestionResult(
                success=True,
                chunks_added=len(chunks),
                source_name=source_name,
            )

        except Exception as e:
            logger.error(f"Text ingestion error: {e}")
            return IngestionResult(
                success=False,
                chunks_added=0,
                source_name=source_name,
                error=str(e),
            )

    async def get_collection_stats(self) -> Dict[str, Any]:
        try:
            count = await embeddings_service.count_documents()
            return {
                "collection": self.collection_name,
                "total_chunks": count,
            }
        except Exception as e:
            logger.error(f"Stats error: {e}")
            return {"error": str(e)}


ingestion_service = IngestionService()
