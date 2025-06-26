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
        if session_id:
            try:
                s = ChatSession.objects.get(pk=session_id, owner=owner)
            except ChatSession.DoesNotExist:
                s = ChatSession.objects.create(owner=owner, title=title or DEFAULT_TITLE)
        else:
            s = ChatSession.objects.create(owner=owner, title=title or DEFAULT_TITLE)
        return self._to_entity(s)

    # ---------- list sessions ----------
    def list_threads(self, owner, *, title_filter=None, page=1, page_size=20):
        qs = ChatSession.objects.filter(owner=owner)
        if title_filter:
            qs = qs.filter(title__icontains=title_filter)
        pages = Paginator(qs.order_by("-created_at"), page_size)
        try:
            page_obj = pages.page(page)
        except EmptyPage:
            page_obj = pages.page(pages.num_pages)
        return [self._to_entity(s) for s in page_obj], pages.num_pages

    # ---------- update title ----------
    def update_thread_title(self, session_id, owner, *, new_title):
        ChatSession.objects.filter(pk=session_id, owner=owner).update(title=new_title)

    # ---------- delete ----------
    def delete_thread(self, session_id, owner):
        ChatSession.objects.filter(pk=session_id, owner=owner).delete()

    # ---------- list messages ----------
    def list_messages(self, session_id, owner, *, page=1, page_size=20):
        qs = ChatMessage.objects.filter(session_id=session_id, session__owner=owner).order_by("created_at")
        pages = Paginator(qs, page_size)
        try:
            page_obj = pages.page(page)
        except EmptyPage:
            page_obj = pages.page(pages.num_pages)
        msgs = [Message(role=m.role, content=m.content or "", timestamp=m.created_at) for m in page_obj]
        return msgs, pages.num_pages

    # ---------- helpers ----------
    def _to_entity(self, s: ChatSession) -> ChatThread:
        msgs = [Message(role=m.role, content=m.content or "", timestamp=m.created_at)
                for m in s.messages.order_by("created_at")]
        return ChatThread(id=s.id, messages=msgs)

    # unchanged ↓
    def add_user_message(self, session_id, *, content=""):
        s = ChatMessage.objects.create(session_id=session_id, role="user", content=content)
        return s.id

    def add_assistant_message(self, session_id, *, content):
        ChatMessage.objects.create(session_id=session_id, role="assistant", content=content)

    def append_image_url(self, message_id, url):
        s = ChatMessage.objects.get(pk=message_id)
        s.image_url = url
        s.save()
