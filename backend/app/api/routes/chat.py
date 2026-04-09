from typing import Optional
import json

from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import StreamingResponse

from app.services.chat_service import chat_service
from app.memory.session_memory import memory_service
from app.evaluation.metrics import evaluation_metrics
from app.utils.logger import logger

from pydantic import BaseModel

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    query: str
    session_id: str
    top_k: Optional[int] = None
    use_reranker: bool = True


@router.post("/")
async def chat(request: ChatRequest = Body(...)):
    query = request.query
    session_id = request.session_id
    top_k = request.top_k
    use_reranker = request.use_reranker
    
    if not query.strip():
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty"
        )
    
    try:
        result = await chat_service.chat(
            query=query,
            session_id=session_id,
            top_k=top_k,
            use_reranker=use_reranker
        )
        
        evaluation = evaluation_metrics.evaluate_rag_response(
            query=query,
            answer=result.answer,
            retrieved_chunks=[],
            latency_ms=result.latency_ms
        )
        
        return {
            "answer": result.answer,
            "sources": result.sources,
            "session_id": result.session_id,
            "latency_ms": result.latency_ms,
            "evaluation": {
                "faithfulness": evaluation.faithfulness,
                "relevance": evaluation.relevance,
                "context_utilization": evaluation.context_utilization
            }
        }
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Chat processing failed: {str(e)}"
        )


@router.post("/stream")
async def stream_chat(request: ChatRequest = Body(...)):
    query = request.query
    session_id = request.session_id
    top_k = request.top_k
    use_reranker = request.use_reranker
    
    if not query.strip():
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty"
        )
    
    async def event_generator():
        try:
            async for token in chat_service.stream_chat(
                query=query,
                session_id=session_id,
                top_k=top_k,
                use_reranker=use_reranker
            ):
                yield f"data: {json.dumps({'token': token})}\n\n"
            
            yield f"data: {json.dumps({'done': True})}\n\n"
            
        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )


@router.get("/history/{session_id}")
async def get_history(session_id: str):
    history = chat_service.get_history(session_id)
    
    return {
        "session_id": session_id,
        "messages": history,
        "message_count": len(history)
    }


@router.delete("/history/{session_id}")
async def clear_history(session_id: str):
    chat_service.clear_history(session_id)
    
    return {
        "success": True,
        "message": f"History cleared for session: {session_id}"
    }
