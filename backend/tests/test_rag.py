import pytest
from app.rag.prompt_builder import PromptBuilder, prompt_builder
from app.rag.retriever import RetrievedChunk


def test_build_rag_prompt():
    chunks = [
        RetrievedChunk(
            id="1",
            text="Python is a programming language",
            score=0.9,
            metadata={"source": "test.pdf", "page": 1}
        )
    ]
    
    prompt = prompt_builder.build_rag_prompt(
        query="What is Python?",
        retrieved_chunks=chunks,
        history=""
    )
    
    assert "Python is a programming language" in prompt
    assert "What is Python?" in prompt
    assert "[Source 1]" in prompt


def test_build_rag_prompt_empty_chunks():
    prompt = prompt_builder.build_rag_prompt(
        query="What is Python?",
        retrieved_chunks=[],
        history=""
    )
    
    assert "No relevant context found" in prompt


def test_extract_sources():
    chunks = [
        RetrievedChunk(
            id="1",
            text="Source 1 text",
            score=0.9,
            metadata={"source": "test.pdf", "page": 1}
        ),
        RetrievedChunk(
            id="2",
            text="Source 2 text",
            score=0.8,
            metadata={"source": "test.pdf", "page": 2}
        )
    ]
    
    sources = prompt_builder.extract_sources(chunks)
    
    assert len(sources) == 1
    assert sources[0]["source"] == "test.pdf"


def test_build_quiz_prompt():
    prompt = prompt_builder.build_quiz_prompt(
        context="Some educational content",
        num_questions=5
    )
    
    assert "5" in prompt
    assert "Some educational content" in prompt
