from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.quiz_service import quiz_service
from app.utils.logger import logger

router = APIRouter(prefix="/generate-quiz", tags=["Quiz"])


class QuizRequest(BaseModel):
    topic: Optional[str] = None
    context: Optional[str] = None
    num_questions: Optional[int] = 5


class QuizSubmitRequest(BaseModel):
    provided_answer: str
    correct_answer: str
    hint: str


class QuizSubmitResponse(BaseModel):
    is_correct: bool
    message: str
    hint: Optional[str] = None


class QuizResponse(BaseModel):
    questions: list
    topic: str
    num_generated: int


@router.post("/", response_model=QuizResponse)
async def generate_quiz(request: QuizRequest):
    if not request.topic and not request.context:
        raise HTTPException(
            status_code=400,
            detail="Either topic or context must be provided"
        )
    
    try:
        result = await quiz_service.generate_quiz(
            topic=request.topic,
            context=request.context,
            num_questions=request.num_questions
        )
        
        return QuizResponse(
            questions=[
                {
                    "question": q.question,
                    "options": q.options,
                    "answer": q.answer,
                    "hint": q.hint
                }
                for q in result.questions
            ],
            topic=result.topic,
            num_generated=result.num_generated
        )
        
    except Exception as e:
        logger.error(f"Quiz generation error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Quiz generation failed: {str(e)}"
        )


@router.post("/submit", response_model=QuizSubmitResponse)
async def submit_quiz_answer(request: QuizSubmitRequest):
    is_correct = request.provided_answer.strip().upper() == request.correct_answer.strip().upper()
    
    if is_correct:
        return QuizSubmitResponse(
            is_correct=True,
            message="The answer is correct"
        )
    else:
        return QuizSubmitResponse(
            is_correct=False,
            message="The answer is wrong",
            hint=request.hint
        )


@router.get("/topics")
async def get_available_topics():
    from app.services.ingestion_service import ingestion_service
    
    try:
        stats = await ingestion_service.get_collection_stats()
        
        return {
            "message": "Topics are extracted from ingested documents",
            "total_chunks": stats.get("total_chunks", 0),
            "tip": "Use the /chat endpoint to ask about specific topics"
        }
    except Exception as e:
        return {"error": str(e)}
