"""
MongoDB Document Models
=======================
Lightweight Python wrappers that turn MongoDB raw dict documents into
attribute-accessible objects so that the existing API endpoint code
(current_user.id, current_user.role, chat.id, etc.) works unchanged.
"""
from bson import ObjectId
from datetime import datetime, timezone


class User:
    """Maps a MongoDB users-collection document to a Python object."""

    def __init__(self, doc: dict):
        self._doc = doc
        self.id: str = str(doc["_id"])          # str(ObjectId)
        self.email: str = doc.get("email", "")
        self.hashed_password: str = doc.get("hashed_password", "")
        self.full_name: str = doc.get("full_name", "")
        self.role: str = doc.get("role", "user")
        self.created_at: datetime = doc.get("created_at", datetime.now(timezone.utc))

    @staticmethod
    def new_doc(email: str, hashed_password: str, full_name: str, role: str = "user") -> dict:
        return {
            "email": email,
            "hashed_password": hashed_password,
            "full_name": full_name,
            "role": role,
            "created_at": datetime.now(timezone.utc),
        }


class Chat:
    """Maps a MongoDB chats-collection document to a Python object."""

    def __init__(self, doc: dict):
        self._doc = doc
        self.id: str = str(doc["_id"])
        self.user_id: str = str(doc.get("user_id", ""))
        self.title: str = doc.get("title", "New Chat")
        self.created_at: datetime = doc.get("created_at", datetime.now(timezone.utc))

    @staticmethod
    def new_doc(user_id: str, title: str = "New Chat") -> dict:
        return {
            "user_id": user_id,
            "title": title,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }


class Message:
    """Maps a MongoDB messages-collection document to a Python object."""

    def __init__(self, doc: dict):
        self._doc = doc
        self.id: str = str(doc["_id"])
        self.chat_id: str = str(doc.get("chat_id", ""))
        self.role: str = doc.get("role", "user")
        self.content: str = doc.get("content", "")
        self.sources: str = doc.get("sources", None)
        self.agent_logs: str = doc.get("agent_logs", None)
        self.created_at: datetime = doc.get("created_at", datetime.now(timezone.utc))

    @staticmethod
    def new_doc(chat_id: str, role: str, content: str,
                sources: str = None, agent_logs: str = None) -> dict:
        return {
            "chat_id": chat_id,
            "role": role,
            "content": content,
            "sources": sources,
            "agent_logs": agent_logs,
            "created_at": datetime.now(timezone.utc),
        }
