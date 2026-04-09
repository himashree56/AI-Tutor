from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import uuid

from langchain_classic.memory import ConversationBufferMemory
from langchain_core.messages import HumanMessage, AIMessage

from app.core.config import settings
from app.utils.logger import logger


@dataclass
class Session:
    session_id: str
    memory: ConversationBufferMemory = field(default_factory=lambda: ConversationBufferMemory(return_messages=True))
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)

    def add_message(self, role: str, content: str):
        if role == "user":
            self.memory.chat_memory.add_user_message(content)
        else:
            self.memory.chat_memory.add_ai_message(content)
        self.last_accessed = datetime.now()

    def get_history(self) -> str:
        return self.memory.load_memory_variables({})["history"]

    def is_expired(self) -> bool:
        expiry_time = self.last_accessed + timedelta(seconds=settings.memory_session_ttl)
        return datetime.now() > expiry_time


class SessionMemoryService:
    def __init__(self):
        self._sessions: Dict[str, Session] = {}

    def create_session(self, session_id: Optional[str] = None) -> str:
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        if session_id not in self._sessions:
            self._sessions[session_id] = Session(session_id=session_id)
            logger.info(f"Created new LangChain-based session: {session_id}")
        else:
            self._sessions[session_id].last_accessed = datetime.now()
        
        return session_id

    def add_message(self, session_id: str, role: str, content: str):
        if session_id not in self._sessions:
            self.create_session(session_id)
        
        self._sessions[session_id].add_message(role, content)

    def get_conversation_history(
        self,
        session_id: str,
        max_turns: Optional[int] = None
    ) -> str:
        if session_id not in self._sessions:
            return ""
        
        # LangChain memory returns a string by default if return_messages=False
        # Our implementation uses return_messages=True for flexibility, so we format it
        messages = self._sessions[session_id].memory.chat_memory.messages
        if max_turns:
            messages = messages[-max_turns*2:]
            
        history_parts = []
        for msg in messages:
            role = "User" if isinstance(msg, HumanMessage) else "Assistant"
            history_parts.append(f"{role}: {msg.content}")
            
        return "\n".join(history_parts)

    def get_messages(self, session_id: str) -> List[Dict]:
        if session_id not in self._sessions:
            return []
        
        messages = []
        for msg in self._sessions[session_id].memory.chat_memory.messages:
            messages.append({
                "role": "user" if isinstance(msg, HumanMessage) else "assistant",
                "content": msg.content
            })
        return messages

    def clear_session(self, session_id: str):
        if session_id in self._sessions:
            self._sessions[session_id].memory.clear()
            logger.info(f"Cleared LangChain memory for session: {session_id}")

    def delete_session(self, session_id: str):
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.info(f"Deleted session: {session_id}")

    def cleanup_expired(self):
        expired = [
            sid for sid, session in self._sessions.items()
            if session.is_expired()
        ]
        
        for sid in expired:
            self.delete_session(sid)

    def list_sessions(self) -> List[Dict]:
        return [
            {
                "session_id": sid,
                "message_count": len(session.memory.chat_memory.messages),
                "created_at": session.created_at.isoformat(),
                "last_accessed": session.last_accessed.isoformat()
            }
            for sid, session in self._sessions.items()
        ]


memory_service = SessionMemoryService()
