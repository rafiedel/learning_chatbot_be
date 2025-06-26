from dataclasses import dataclass
from datetime import datetime
from typing import List

@dataclass(frozen=True)
class Message:
    role: str          # "user" / "assistant"
    content: str
    timestamp: datetime

@dataclass
class ChatThread:
    id: int
    messages: List[Message]
