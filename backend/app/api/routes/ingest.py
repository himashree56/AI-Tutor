from typing import List, Optional

from fastapi import UploadFile, File, HTTPException, APIRouter
from pydantic import BaseModel

from app.services.ingestion_service import ingestion_service
from app.rag.embeddings import embeddings_service
from app.utils.logger import logger

router = APIRouter(prefix="/ingest", tags=["Ingestion"])


class IngestTextRequest(BaseModel):
    text: str
    source_name: str = "text_input"


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    collection: Optional[str] = None,
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    content = await file.read()

    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Empty file")

    if len(content) > 50 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds 50MB limit")

    result = await ingestion_service.ingest_document(
        file_content=content,
        file_name=file.filename,
    )

    if not result.success:
        raise HTTPException(status_code=500, detail=result.error)

    return {
        "success": True,
        "message": "Document ingested successfully",
        "chunks_added": result.chunks_added,
        "source": result.source_name,
    }


@router.post("/text")
async def ingest_text(request: IngestTextRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    result = await ingestion_service.ingest_text(
        text=request.text,
        source_name=request.source_name,
    )

    if not result.success:
        raise HTTPException(status_code=500, detail=result.error)

    return {
        "success": True,
        "message": "Text ingested successfully",
        "chunks_added": result.chunks_added,
        "source": result.source_name,
    }


@router.get("/stats")
async def get_stats():
    stats = await ingestion_service.get_collection_stats()
    return stats


@router.delete("/reset")
async def reset_collection():
    try:
        await embeddings_service.drop_collection()
        return {"success": True, "message": "Collection reset successfully"}
    except Exception as e:
        logger.error(f"Reset error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
