from dataclasses import dataclass, field
from uuid import uuid4

from src.conversation.summarizer import summarize_conversation


@dataclass
class ConversationSession:
    session_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    history: list[dict] = field(
        default_factory=list
    )

    summary: str = ""

    max_messages: int = 10

    summarize_count: int = 4

    def add_user_message(
        self,
        content: str,
    ) -> None:
        self._add_message(
            role="user",
            content=content,
        )

    def add_assistant_message(
        self,
        content: str,
    ) -> None:
        self._add_message(
            role="assistant",
            content=content,
        )

    def _add_message(
        self,
        role: str,
        content: str,
    ) -> None:
        if not content.strip():
            return

        self.history.append(
            {
                "role": role,
                "content": content,
            }
        )

        self._manage_history()

    def _manage_history(self) -> None:
        if len(self.history) <= self.max_messages:
            return

        messages_to_summarize = self.history[
            :self.summarize_count
        ]

        self.summary = summarize_conversation(
            messages=messages_to_summarize,
            existing_summary=self.summary,
        )

        self.history = self.history[
            self.summarize_count:
        ]

    def get_history(self) -> list[dict]:
        history = []

        if self.summary:
            history.append(
                {
                    "role": "system",
                    "content": (
                        "Conversation summary: "
                        f"{self.summary}"
                    ),
                }
            )

        history.extend(self.history)

        return history

    def clear(self) -> None:
        self.history.clear()
        self.summary = ""