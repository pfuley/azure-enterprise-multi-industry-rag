from dataclasses import dataclass
from datetime import datetime


@dataclass
class PersistedMessage:
    id: str
    session_id: str
    role: str
    content: str
    sequence: int
    created_at: datetime


@dataclass
class PersistedSession:
    id: str
    session_id: str
    user_id: str
    created_at: datetime
    last_accessed_at: datetime
    title: str | None = None