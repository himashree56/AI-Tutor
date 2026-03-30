import os
from pathlib import Path
from typing import Literal, Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # ── Pinecone Vector Search ──────────────────────────────────────────────
    pinecone_api_key: str = "your_pinecone_api_key"
    pinecone_index_name: str = "ai-tutor"

    # ── Embedding ───────────────────────────────────────────────────────────
    embedding_provider: Literal["local", "openrouter"] = "local"
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_device: Literal["cpu", "cuda"] = "cpu"
    embedding_batch_size: int = 32

    # OpenRouter Embedding
    openrouter_embedding_model: str = "openai/text-embedding-3-small"

    # ── Reranker & Retrieval ────────────────────────────────────────────────
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    reranker_top_k: int = 10

    retrieval_top_k: int = 20
    retrieval_score_threshold: float = 0.3

    # ── Chunking ────────────────────────────────────────────────────────────
    chunk_size: int = 1000
    chunk_overlap: int = 200

    # ── LLM Provider ────────────────────────────────────────────────────────
    llm_provider: Literal["ollama", "huggingface", "openrouter"] = "ollama"

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "mistral"
    ollama_temperature: float = 0.7
    ollama_top_p: float = 0.9
    ollama_max_tokens: int = 2048
    ollama_num_ctx: int = 4096

    # OpenRouter
    openrouter_api_key: Optional[str] = None
    openrouter_model: str = "google/gemma-2-9b-it:free"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    # HuggingFace
    hf_model_name: str = "mistralai/Mistral-7B-Instruct-v0.2"
    hf_device_map: str = "auto"

    # ── Quiz ────────────────────────────────────────────────────────────────
    quiz_num_questions: int = 5
    quiz_temperature: float = 0.8

    # ── Logging ─────────────────────────────────────────────────────────────
    log_level: str = "INFO"
    log_file: Path = Path("./logs/app.log")

    # ── Memory ──────────────────────────────────────────────────────────────
    max_memory_turns: int = 10
    memory_session_ttl: int = 3600

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.log_file = Path(self.log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)


settings = Settings()
