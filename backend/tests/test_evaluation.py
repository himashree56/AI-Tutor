import pytest
from app.evaluation.metrics import EvaluationMetrics, EvaluationResult
from app.rag.retriever import RetrievedChunk


@pytest.fixture
def metrics():
    return EvaluationMetrics()


def test_context_relevance_empty_chunks(metrics):
    score = metrics.calculate_context_relevance("test query", [])
    assert score == 0.0


def test_context_relevance_with_chunks(metrics):
    chunks = [
        RetrievedChunk(
            id="1",
            text="This is a test document about machine learning",
            score=0.9,
            metadata={"source": "test.pdf"}
        )
    ]
    score = metrics.calculate_context_relevance("machine learning", chunks)
    assert score > 0.0


def test_faithfulness_empty_answer(metrics):
    score = metrics.calculate_answer_faithfulness("", [])
    assert score == 0.0


def test_faithfulness_matching_context(metrics):
    chunks = [
        RetrievedChunk(
            id="1",
            text="Python is a programming language",
            score=0.9,
            metadata={}
        )
    ]
    score = metrics.calculate_answer_faithfulness(
        "Python is a programming language",
        chunks
    )
    assert score > 0.5


def test_context_utilization(metrics):
    chunks = [
        RetrievedChunk(id="1", text="Python is popular", score=0.9, metadata={}),
        RetrievedChunk(id="2", text="Java is also popular", score=0.8, metadata={})
    ]
    score = metrics.calculate_context_utilization(chunks, "Python is very popular")
    assert 0.0 <= score <= 1.0


def test_evaluate_rag_response(metrics):
    chunks = [
        RetrievedChunk(
            id="1",
            text="The capital of France is Paris",
            score=0.95,
            metadata={"source": "geo.txt"}
        )
    ]
    
    result = metrics.evaluate_rag_response(
        query="What is the capital of France?",
        answer="The capital of France is Paris",
        retrieved_chunks=chunks,
        latency_ms=150.5
    )
    
    assert isinstance(result, EvaluationResult)
    assert result.latency_ms == 150.5
    assert result.faithfulness > 0
