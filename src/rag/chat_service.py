from src.conversation.session import ConversationSession
from src.rag.orchestrator import answer_question


class RAGChatService:

    def __init__(
        self,
        industry: str,
        department: str | None = None,
        classification: str | None = None,
    ):
        self.industry = industry
        self.department = department
        self.classification = classification

        self.session = ConversationSession()

    def ask(
        self,
        question: str,
    ) -> dict:

        # -----------------------------------------
        # 1. Get current conversation context
        # -----------------------------------------

        history = self.session.get_history()

        # -----------------------------------------
        # 2. Run the complete RAG pipeline
        # -----------------------------------------

        result = answer_question(
            question=question,
            industry=self.industry,
            department=self.department,
            classification=self.classification,
            conversation_history=history,
        )

        # -----------------------------------------
        # 3. Save the latest user message
        # -----------------------------------------

        self.session.add_user_message(
            question
        )

        # -----------------------------------------
        # 4. Save the assistant response
        # -----------------------------------------

        self.session.add_assistant_message(
            result["answer"]
        )

        # -----------------------------------------
        # 5. Attach session information
        # -----------------------------------------

        result["session_id"] = self.session.session_id

        return result

    def get_history(self) -> list[dict]:
        return self.session.get_history()

    def get_session_id(self) -> str:
        return self.session.session_id

    def clear_conversation(self) -> None:
        self.session.clear()