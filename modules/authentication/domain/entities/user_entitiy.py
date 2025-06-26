from dataclasses import dataclass
from typing import Optional
from uuid import UUID

@dataclass
class UserEntity:
    id: Optional[UUID]
    username: str
    email: str
