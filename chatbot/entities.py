from dataclasses import dataclass
from datetime import datetime
from typing import List

@dataclass(frozen=True)
class Message:
    id: int
    role: str          # "user" / "assistant"
    content: str
    timestamp: datetime
    image_url: str

@dataclass
class ChatThread:
    id: int
    title: str
    created_at: datetime
