from dataclasses import dataclass
from typing import Optional
from uuid import UUID

@dataclass
class User:
    id: Optional[UUID]
    username: str
    email: str
