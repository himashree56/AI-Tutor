import io
import PyPDF2
from typing import List, Tuple, Dict, Any
from app.utils.logger import logger
from app.utils.chunking import chunker

class PDFProcessor:
    def process_pdf(
        self,
        pdf_bytes: bytes,
        source_name: str
    ) -> List[Dict[str, Any]]:
        """
        Extracts text from PDF and returns chunks with page metadata using PyPDF2.
        """
        try:
            reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            page_texts = []
            
            for page_num, page in enumerate(reader.pages, 1):
                text = page.extract_text()
                if text and text.strip():
                    page_texts.append((page_num, text))
            
            if not page_texts:
                logger.warning(f"No text extracted from {source_name}")
                return []
            
            # Use Chunker to create hierarchical chunks with page metadata
            chunks = chunker.chunk_texts_with_pages(
                page_texts=page_texts,
                source_name=source_name
            )
            
            logger.info(f"Processed PDF {source_name}: {len(page_texts)} pages, {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Error processing PDF {source_name}: {e}")
            raise

pdf_processor = PDFProcessor()
