from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from django.contrib.auth import get_user_model
from django.core.paginator import Paginator, EmptyPage

from .entities import Message, ChatThread          
from chatbot.models import ChatSession, ChatMessage 

User = get_user_model()
DEFAULT_TITLE = "New Chat"


class ChatRepository(ABC):
    # ---------- 1. completions ----------
    @abstractmethod
    def get_or_create_thread(
        self,
        owner: User,
        *,
        session_id: Optional[int],
        title: str | None = None,
    ) -> ChatThread: ...

    # ---------- 2. list sessions ----------
    @abstractmethod
    def list_threads(
        self,
        owner: User,
        *,
        title_filter: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[ChatThread], int]: ...

    # ---------- 3. update title ----------
    @abstractmethod
    def update_thread_title(
        self,
        session_id: int,
        owner: User,
        *,
        new_title: str,
    ) -> None: ...

    # ---------- 4. delete session ----------
    @abstractmethod
    def delete_thread(self, session_id: int, owner: User) -> None: ...

    # ---------- 5. list messages ----------
    @abstractmethod
    def list_messages(
        self,
        session_id: int,
        owner: User,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Message], int]: ...

    # ----- existing helpers -------------
    @abstractmethod
    def add_user_message(self, session_id: int, *, content: str = "", image_data: str = "") -> None: ...
    @abstractmethod
    def add_assistant_message(self, session_id: int, *, content: str) -> None: ...
    @abstractmethod
    def append_image_url(self, session_id: int, url: str) -> None: ...


class DjangoChatRepository(ChatRepository):
    # ---------- completions ----------
    def get_or_create_thread(self, owner, *, session_id, title=None):
        print(session_id)
        if session_id:
            try:
                s = ChatSession.objects.get(pk=session_id, owner=owner)
            except ChatSession.DoesNotExist:
                s = ChatSession.objects.create(owner=owner, title=title or DEFAULT_TITLE)
        else:
            s = ChatSession.objects.create(owner=owner, title=title or DEFAULT_TITLE)
        return self._to_entity(s)

    # ---------- list sessions ----------
    def list_threads(self, owner, *, title_filter=None, before_id=None, page_size=20):
        qs = ChatSession.objects.filter(owner=owner)

        if title_filter:
            qs = qs.filter(title__icontains=title_filter)

        if before_id:
            try:
                before_session = qs.get(id=before_id)
            except ChatSession.DoesNotExist:
                return []

            qs = qs.filter(id__lt=before_session.id)

        # Order by ID descending (latest ID first)
        qs = qs.order_by("-id")[:page_size]

        sessions = [
            self._to_entity(s)
            for s in qs
        ]

        return sessions


    # ---------- update title ----------
    def update_thread_title(self, session_id, owner, *, new_title):
        ChatSession.objects.filter(pk=session_id, owner=owner).update(title=new_title)

    # ---------- delete ----------
    def delete_thread(self, session_id, owner):
        ChatSession.objects.filter(pk=session_id, owner=owner).delete()

    # ---------- list messages ----------
    def list_messages(self, session_id, owner, *, before_id=None, page_size=10):
        qs = ChatMessage.objects.filter(
            session_id=session_id,
            session__owner=owner,
        )

        # If before_id provided, only get messages older than that message
        if before_id:
            try:
                before_msg = qs.get(id=before_id)
            except ChatMessage.DoesNotExist:
                raise ValueError("Invalid before_id")
            qs = qs.filter(created_at__lt=before_msg.created_at)

        # Always order descending (newest first)
        qs = qs.order_by("-created_at")[:page_size]

        # We re-reverse so the frontend gets oldest->newest for appending
        msgs = [
            Message(
                id=m.id,
                role=m.role,
                content=m.content or "",
                timestamp=m.created_at,
                image_url=m.image_url
            )
            for m in reversed(qs)
        ]
        return msgs


    # ---------- helpers ----------
    def _to_entity(self, s: ChatSession) -> ChatThread:
        return ChatThread(id=s.id, title=s.title , created_at=s.created_at)

    # unchanged ↓
    def add_user_message(self, session_id, *, content=""):
        s = ChatMessage.objects.create(session_id=session_id, role="user", content=content)
        return s.id

    def add_assistant_message(self, session_id, *, content):
        s = ChatMessage.objects.create(session_id=session_id, role="assistant", content=content)
        return s.id

    def append_image_url(self, message_id, url):
        s = ChatMessage.objects.get(pk=message_id)
        s.image_url = url
        s.save()

    def get_message(self, message_id) -> Message:
        m = ChatMessage.objects.get(id=message_id)
        return Message(
            id=m.id,
            role=m.role,
            content=m.content or "",
            timestamp=m.created_at,
            image_url=m.image_url
        )