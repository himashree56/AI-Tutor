from fastapi import Depends

from app.core.config import settings
from app.memory.session_memory import memory_service
from app.rag.embeddings import embeddings_service


def get_embeddings_service():
    return embeddings_service


def get_memory_service():
    return memory_service


def get_settings():
    return settings
