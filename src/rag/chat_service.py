from src.conversation.session import ConversationSession
from src.guardrails.content_safety import analyze_text_safety
from src.guardrails.exceptions import GuardrailBlockedError
from src.rag.orchestrator import answer_question
from src.security.authorization import AuthorizationContext


CONTENT_SAFETY_THRESHOLD = 4


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
        # 1. Get conversation history
        # -------------------------------------

        history = self.session.get_history()

        # -------------------------------------
        # 2. Check user input for harmful
        #    content before running RAG
        # -------------------------------------

        input_safety = analyze_text_safety(
            question
        )

        if input_safety.exceeds_threshold(
            threshold=CONTENT_SAFETY_THRESHOLD
        ):
            result = {
                "answer": (
                    "I can't process that request because "
                    "it triggered an application safety control."
                ),
                "sources": [],
                "search_query": question,
                "retrieval_trace": [],
                "guardrail_blocked": True,
                "guardrail_reason": (
                    "Input content exceeded the "
                    "configured safety threshold."
                ),
            }

        else:

            # ---------------------------------
            # 3. Run secure RAG pipeline
            #
            # answer_question() currently
            # includes:
            #
            # - direct Prompt Shield check
            # - query rewriting
            # - authorization filtering
            # - semantic hybrid retrieval
            # - document Prompt Shield check
            # - context construction
            # - grounded generation
            # ---------------------------------

            try:
                result = answer_question(
                    question=question,
                    auth=self.auth,
                    conversation_history=history,
                )

                result["guardrail_blocked"] = False
                result["guardrail_reason"] = None

            except GuardrailBlockedError as error:
                result = {
                    "answer": (
                        "I can't process that request because "
                        "it triggered an application safety control."
                    ),
                    "sources": [],
                    "search_query": question,
                    "retrieval_trace": [],
                    "guardrail_blocked": True,
                    "guardrail_reason": str(error),
                }

        # -------------------------------------
        # 4. Check generated output for
        #    harmful content
        #
        # Only run this if the request has
        # not already been blocked.
        # -------------------------------------

        if not result["guardrail_blocked"]:
            output_safety = analyze_text_safety(
                result["answer"]
            )

            if output_safety.exceeds_threshold(
                threshold=CONTENT_SAFETY_THRESHOLD
            ):
                result = {
                    "answer": (
                        "The generated response was blocked "
                        "by an application safety control."
                    ),
                    "sources": [],
                    "search_query": result[
                        "search_query"
                    ],
                    "retrieval_trace": result[
                        "retrieval_trace"
                    ],
                    "guardrail_blocked": True,
                    "guardrail_reason": (
                        "Generated output exceeded the "
                        "configured safety threshold."
                    ),
                }

        # -------------------------------------
        # 5. Store the user message
        # -------------------------------------

        self.session.add_user_message(
            question
        )

        # -------------------------------------
        # 6. Store the final assistant response
        #
        # This stores either:
        # - normal grounded answer
        # - guardrail response
        # -------------------------------------

        self.session.add_assistant_message(
            result["answer"]
        )

        # -------------------------------------
        # 7. Attach session information
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