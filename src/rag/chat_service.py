from src.conversation.session import (
    ConversationSession,
)
from src.rag.orchestrator import answer_question
from src.security.authorization import (
    AuthorizationContext,
)


class RAGChatService:

    def __init__(
        self,
        auth: AuthorizationContext,
    ):
        self.auth = auth

        self.session = ConversationSession()

    def ask(
        self,
        question: str,
    ) -> dict:

        # -------------------------------------
        # 1. Get conversation context
        # -------------------------------------

        history = self.session.get_history()

        # -------------------------------------
        # 2. Run secure RAG pipeline
        # -------------------------------------

        result = answer_question(
            question=question,
            auth=self.auth,
            conversation_history=history,
        )

        # -------------------------------------
        # 3. Store user message
        # -------------------------------------

        self.session.add_user_message(
            question
        )

        # -------------------------------------
        # 4. Store assistant response
        # -------------------------------------

        self.session.add_assistant_message(
            result["answer"]
        )

        # -------------------------------------
        # 5. Add session information
        # -------------------------------------

        result["session_id"] = (
            self.session.session_id
        )

        return result

    def get_history(
        self,
    ) -> list[dict]:
        return self.session.get_history()

    def get_session_id(
        self,
    ) -> str:
        return self.session.session_id

    def get_authorization_context(
        self,
    ) -> AuthorizationContext:
        return self.auth

    def clear_conversation(
        self,
    ) -> None:
        self.session.clear()