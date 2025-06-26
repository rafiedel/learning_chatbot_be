from __future__ import annotations

"""Domain-layer repository boundary and Django implementation.

This module decouples application logic from Django ORM by exposing an abstract
``ChatRepository`` interface that works with **entities** (defined in
``entities.py``) instead of models.  Infrastructure-specific details (Django
queries, JSON field handling, etc.) live inside ``DjangoChatRepository``.

Usage example (e.g. in a DRF view):

>>> repo = DjangoChatRepository()
>>> service = ChatService(repo)  # ChatService now depends on abstraction
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from django.contrib.auth import get_user_model

from entities import Message, ChatThread  # fileciteturn0file0
from chatbot.models import ChatSession, ChatMessage  # fileciteturn0file1

User = get_user_model()


class ChatRepository(ABC):
    """Boundary interface obeyed by any chat persistence mechanism."""

    # -- Sessions / Threads --------------------------------------------------
    @abstractmethod
    def get_thread(self, session_id: int, owner: User) -> ChatThread: ...

    @abstractmethod
    def create_thread(self, owner: User, title: str) -> ChatThread: ...

    @abstractmethod
    def list_threads(self, owner: User, *, title_filter: Optional[str] = None) -> List[ChatThread]: ...

    # -- Messages ------------------------------------------------------------
    @abstractmethod
    def add_user_message(
        self,
        session_id: int,
        *,
        content: str = "",
        image_data: str = "",
    ) -> None: ...

    @abstractmethod
    def add_assistant_message(self, session_id: int, *, content: str) -> None: ...

    # -- Misc ---------------------------------------------------------------
    @abstractmethod
    def append_image_url(self, session_id: int, url: str) -> None: ...


class DjangoChatRepository(ChatRepository):
    """Concrete repository backed by Django ORM models."""

    # -- Private helpers -----------------------------------------------------
    def _session_to_entity(self, session: ChatSession) -> ChatThread:
        """Convert a ``ChatSession`` ORM instance into a pure domain entity."""
        msgs = [
            Message(
                role=m.role,
                content=m.content or "",
                timestamp=m.created_at,
            )
            for m in session.messages.order_by("created_at")
        ]
        return ChatThread(id=session.id, messages=msgs)

    # -- Sessions / Threads --------------------------------------------------
    def get_thread(self, session_id: int, owner: User) -> ChatThread:
        session = ChatSession.objects.get(id=session_id, owner=owner)
        return self._session_to_entity(session)

    def create_thread(self, owner: User, title: str) -> ChatThread:
        session = ChatSession.objects.create(owner=owner, title=title)
        return self._session_to_entity(session)

    def list_threads(self, owner: User, *, title_filter: Optional[str] = None) -> List[ChatThread]:
        qs = ChatSession.objects.filter(owner=owner)
        if title_filter:
            qs = qs.filter(title__icontains=title_filter)
        return [self._session_to_entity(s) for s in qs.order_by("-created_at")]

    # -- Messages ------------------------------------------------------------
    def add_user_message(
        self,
        session_id: int,
        *,
        content: str = "",
        image_data: str = "",
    ) -> None:
        ChatMessage.objects.create(
            session_id=session_id,
            role="user",
            content=content,
            image_data=image_data,
        )

    def add_assistant_message(self, session_id: int, *, content: str) -> None:
        ChatMessage.objects.create(
            session_id=session_id,
            role="assistant",
            content=content,
        )

    # -- Misc ---------------------------------------------------------------
    def append_image_url(self, session_id: int, url: str) -> None:
        session = ChatSession.objects.get(id=session_id)
        session.image_urls.append(url)
        session.save()


__all__ = [
    "ChatRepository",
    "DjangoChatRepository",
]
