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

        if (
            input_safety.exceeds_threshold(
                threshold=CONTENT_SAFETY_THRESHOLD
            )
            or input_safety.blocklist_match_detected
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
                    "Input content exceeded the configured "
                    "safety policy or matched an enterprise "
                    "blocklist."
                ),
            }

        else:

            # ---------------------------------
            # 3. Run secure RAG pipeline
            #
            # answer_question() includes:
            #
            # - direct Prompt Shield check
            # - query rewriting
            # - authorization filtering
            # - semantic hybrid retrieval
            # - document Prompt Shield check
            # - context construction
            # - grounded answer generation
            # ---------------------------------

            try:

                result = answer_question(
                    question=question,
                    auth=self.auth,
                    conversation_history=history,
                )

                result[
                    "guardrail_blocked"
                ] = False

                result[
                    "guardrail_reason"
                ] = None

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
                    "guardrail_reason": str(
                        error
                    ),
                }

        # -------------------------------------
        # 4. Check generated output for
        #    harmful content
        #
        # Only run when the request has not
        # already been blocked.
        # -------------------------------------

        if not result[
            "guardrail_blocked"
        ]:

            output_safety = (
                analyze_text_safety(
                    result["answer"]
                )
            )

            if (
                output_safety.exceeds_threshold(
                    threshold=(
                        CONTENT_SAFETY_THRESHOLD
                    )
                )
                or output_safety.blocklist_match_detected
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
                        "configured safety policy or matched "
                        "an enterprise blocklist."
                    ),
                }

        # -------------------------------------
        # 5. Store user message in the
        #    request-level ConversationSession
        #
        # When FastAPI uses Cosmos DB, this
        # in-memory session is rebuilt from
        # persisted Cosmos messages at the
        # start of every HTTP request.
        # -------------------------------------

        self.session.add_user_message(
            question
        )

        # -------------------------------------
        # 6. Store assistant response
        # -------------------------------------

        self.session.add_assistant_message(
            result["answer"]
        )

        # -------------------------------------
        # 7. Attach session ID
        # -------------------------------------

        result[
            "session_id"
        ] = self.session.session_id

        return result

    def get_history(
        self,
    ) -> list[dict]:
        """
        Return the current request-level
        conversation history.
        """

        return self.session.get_history()

    def get_session_id(
        self,
    ) -> str:
        """
        Return the current conversation
        session identifier.
        """

        return self.session.session_id

    def get_authorization_context(
        self,
    ) -> AuthorizationContext:
        """
        Return the authorization context used
        by this chat service.
        """

        return self.auth

    def load_history(
        self,
        messages: list[dict],
        session_id: str | None = None,
    ) -> None:
        """
        Restore persisted conversation history
        into the request-level ConversationSession.

        Cosmos DB is the persistent source of
        truth between HTTP requests.

        Flow:

        Cosmos DB
            ↓
        messages[]
            ↓
        load_history()
            ↓
        ConversationSession
            ↓
        query rewriting / conversational RAG
        """

        # -------------------------------------
        # 1. Remove any existing messages from
        #    the temporary ConversationSession
        # -------------------------------------

        self.session.clear()

        # -------------------------------------
        # 2. Restore the persistent Cosmos
        #    session ID
        # -------------------------------------

        if session_id:

            self.session.session_id = (
                session_id
            )

        # -------------------------------------
        # 3. Restore persisted messages
        #
        # IMPORTANT:
        # role and content must be read inside
        # this loop.
        # -------------------------------------

        for message in messages:

            role = message.get(
                "role"
            )

            content = message.get(
                "content",
                "",
            )

            if role == "user":

                self.session.add_user_message(
                    content
                )

            elif role == "assistant":

                self.session.add_assistant_message(
                    content
                )

    def clear_conversation(
        self,
    ) -> None:
        """
        Clear the current request-level
        conversation history.

        Persistent Cosmos sessions should be
        deleted through CosmosSessionStore,
        not through this method.
        """

        self.session.clear()