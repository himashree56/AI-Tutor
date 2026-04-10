import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.utils.logger import logger
from app.api.routes import ingest, chat, quiz


from app.rag.embeddings import embeddings_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting AI Tutor Backend...")
    logger.info(f"LLM Provider: {settings.llm_provider}")
    active_model = settings.openrouter_model if settings.llm_provider == "openrouter" else settings.ollama_model
    logger.info(f"Active Model: {active_model}")
    
    # Pre-load embedding models and connections in the background
    # so we don't block the server from accepting connections on port 8000
    asyncio.create_task(asyncio.to_thread(embeddings_service.initialize))
    
    yield
    
    logger.info("Shutting down AI Tutor Backend...")


app = FastAPI(
    title="AI Tutor Backend",
    description="A production-ready RAG-based AI Tutor with local LLM support",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(ingest.router)
app.include_router(chat.router)
app.include_router(quiz.router)


@app.get("/")
async def root():
    return {
        "name": "AI Tutor Backend",
        "version": "1.0.0",
        "status": "running",
        "features": [
            "PDF ingestion",
            "RAG-based chat",
            "Streaming responses",
            "Quiz generation",
            "Session memory",
            "Cloud LLM (OpenRouter)"
        ]
    }


@app.get("/health")
async def health_check():
    provider = settings.llm_provider
    model = settings.openrouter_model if provider == "openrouter" else settings.ollama_model
    
    return {
        "status": "healthy",
        "llm_provider": provider,
        "llm_model": model,
        "embedding_model": settings.embedding_model
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
