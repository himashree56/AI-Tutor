import pytest
from app.memory.session_memory import SessionMemoryService


@pytest.fixture
def memory_service():
    return SessionMemoryService()


def test_create_session(memory_service):
    session_id = memory_service.create_session()
    assert session_id is not None
    assert len(session_id) > 0


def test_add_message(memory_service):
    session_id = memory_service.create_session("test_session")
    memory_service.add_message(session_id, "user", "Hello")
    memory_service.add_message(session_id, "assistant", "Hi there")
    
    history = memory_service.get_messages(session_id)
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "assistant"


def test_get_conversation_history(memory_service):
    session_id = memory_service.create_session("test_session")
    memory_service.add_message(session_id, "user", "Question 1")
    memory_service.add_message(session_id, "assistant", "Answer 1")
    memory_service.add_message(session_id, "user", "Question 2")
    memory_service.add_message(session_id, "assistant", "Answer 2")
    
    history = memory_service.get_conversation_history(session_id)
    assert "Question 1" in history
    assert "Answer 1" in history


def test_clear_session(memory_service):
    session_id = memory_service.create_session("test_session")
    memory_service.add_message(session_id, "user", "Hello")
    
    memory_service.clear_session(session_id)
    messages = memory_service.get_messages(session_id)
    assert len(messages) == 0


def test_delete_session(memory_service):
    session_id = memory_service.create_session("test_session")
    memory_service.delete_session(session_id)
    
    messages = memory_service.get_messages(session_id)
    assert len(messages) == 0
