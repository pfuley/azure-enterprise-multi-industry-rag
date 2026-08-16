from abc import ABC, abstractmethod

from src.session.models import (
    PersistedMessage,
    PersistedSession,
)


class SessionStore(ABC):

    @abstractmethod
    def create_session(
        self,
        user_id: str,
        title: str | None = None,
    ) -> PersistedSession:
        pass

    @abstractmethod
    def get_session(
        self,
        session_id: str,
        user_id: str,
    ) -> PersistedSession | None:
        pass

    @abstractmethod
    def list_sessions(
        self,
        user_id: str,
    ) -> list[PersistedSession]:
        pass

    @abstractmethod
    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
    ) -> PersistedMessage:
        pass

    @abstractmethod
    def get_messages(
        self,
        session_id: str,
        user_id: str,
    ) -> list[PersistedMessage]:
        pass

    @abstractmethod
    def delete_session(
        self,
        session_id: str,
        user_id: str,
    ) -> bool:
        pass