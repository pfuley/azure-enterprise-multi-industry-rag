from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from src.api.auth import (
    get_authorization_context,
)
from src.api.models import (
    ChatRequest,
    ChatResponse,
    SessionDeleteResponse,
    SessionHistoryResponse,
    SessionListResponse,
    SessionSummaryResponse,
)
from src.rag.chat_service import (
    RAGChatService,
)
from src.security.authorization import (
    AuthorizationContext,
)
from src.session.cosmos_store import (
    CosmosSessionStore,
)


router = APIRouter()


# ---------------------------------------------------------
# Cosmos-backed persistent conversation store
#
# The store object is created once when this module loads.
# Conversation data itself is persisted in Azure Cosmos DB.
# ---------------------------------------------------------

session_store = CosmosSessionStore()


def _require_session(
    session_id: str,
    auth: AuthorizationContext,
):
    """
    Load a persistent session and enforce ownership.

    Knowing a session_id alone must never grant access.
    The authenticated user must own the session.
    """

    try:
        session = session_store.get_session(
            session_id=session_id,
            user_id=auth.user_id,
        )

    except PermissionError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_403_FORBIDDEN
            ),
            detail=str(error),
        ) from error

    if session is None:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=(
                "Chat session was not found."
            ),
        )

    return session


# =========================================================
# CHAT
# =========================================================

@router.post(
    "/chat",
    response_model=ChatResponse,
)
def chat(
    request: ChatRequest,

    auth: AuthorizationContext = Depends(
        get_authorization_context
    ),
) -> ChatResponse:
    """
    Send a message to the RAG assistant.

    If session_id is omitted:
        create a new persistent Cosmos session.

    If session_id is supplied:
        restore the existing conversation from Cosmos.
    """

    # -----------------------------------------------------
    # 1. Create or load conversation session
    # -----------------------------------------------------

    if request.session_id:

        persisted_session = (
            _require_session(
                session_id=request.session_id,
                auth=auth,
            )
        )

    else:

        # Use the first user question as the initial
        # conversation title for the React sidebar.
        title = (
            request.question[:60]
        )

        persisted_session = (
            session_store.create_session(
                user_id=auth.user_id,
                title=title,
            )
        )

    session_id = (
        persisted_session.session_id
    )

    # -----------------------------------------------------
    # 2. Load existing conversation history from Cosmos
    # -----------------------------------------------------

    try:
        persisted_messages = (
            session_store.get_messages(
                session_id=session_id,
                user_id=auth.user_id,
            )
        )

    except PermissionError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_403_FORBIDDEN
            ),
            detail=str(error),
        ) from error

    history = [
        {
            "role":
                message.role,

            "content":
                message.content,
        }
        for message in persisted_messages
    ]

    # -----------------------------------------------------
    # 3. Build request-level RAGChatService
    #
    # The Python object is temporary.
    # Cosmos DB is the persistent source of truth.
    # -----------------------------------------------------

    chat_service = RAGChatService(
        auth=auth
    )

    # -----------------------------------------------------
    # 4. Restore previous conversation into RAGChatService
    # -----------------------------------------------------

    chat_service.load_history(
        messages=history,
        session_id=session_id,
    )

    # -----------------------------------------------------
    # 5. Run secure RAG pipeline
    #
    # Includes:
    # - Content Safety
    # - Prompt Shields
    # - conversational query rewriting
    # - authorization-filtered Azure AI Search
    # - grounded generation
    # - output safety
    # -----------------------------------------------------

    result = chat_service.ask(
        request.question
    )

    # -----------------------------------------------------
    # 6. Persist new user message
    # -----------------------------------------------------

    session_store.add_message(
        session_id=session_id,
        role="user",
        content=request.question,
    )

    # -----------------------------------------------------
    # 7. Persist assistant answer
    # -----------------------------------------------------

    session_store.add_message(
        session_id=session_id,
        role="assistant",
        content=result[
            "answer"
        ],
    )

    # -----------------------------------------------------
    # 8. Return API response
    # -----------------------------------------------------

    return ChatResponse(
        answer=result[
            "answer"
        ],

        session_id=session_id,

        search_query=result[
            "search_query"
        ],

        guardrail_blocked=result[
            "guardrail_blocked"
        ],

        guardrail_reason=result.get(
            "guardrail_reason"
        ),

        sources=result[
            "sources"
        ],
    )


# =========================================================
# LIST USER SESSIONS
# =========================================================

@router.get(
    "/sessions",
    response_model=SessionListResponse,
)
def list_sessions(
    auth: AuthorizationContext = Depends(
        get_authorization_context
    ),
) -> SessionListResponse:
    """
    Return all persistent chat sessions owned
    by the authenticated user.

    Used by the React conversation sidebar.
    """

    sessions = (
        session_store.list_sessions(
            user_id=auth.user_id
        )
    )

    return SessionListResponse(
        sessions=[
            SessionSummaryResponse(
                session_id=(
                    session.session_id
                ),

                title=(
                    session.title
                ),

                created_at=(
                    session
                    .created_at
                    .isoformat()
                ),

                last_accessed_at=(
                    session
                    .last_accessed_at
                    .isoformat()
                ),
            )
            for session in sessions
        ]
    )


# =========================================================
# SESSION HISTORY
# =========================================================

@router.get(
    "/sessions/{session_id}/history",
    response_model=SessionHistoryResponse,
)
def get_session_history(
    session_id: str,

    auth: AuthorizationContext = Depends(
        get_authorization_context
    ),
) -> SessionHistoryResponse:
    """
    Return conversation history for one session.

    Session ownership is checked before any messages
    are returned.
    """

    # -----------------------------------------------------
    # 1. Verify session exists and belongs to user
    # -----------------------------------------------------

    _require_session(
        session_id=session_id,
        auth=auth,
    )

    # -----------------------------------------------------
    # 2. Load persisted messages
    # -----------------------------------------------------

    try:
        messages = (
            session_store.get_messages(
                session_id=session_id,
                user_id=auth.user_id,
            )
        )

    except PermissionError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_403_FORBIDDEN
            ),
            detail=str(error),
        ) from error

    # -----------------------------------------------------
    # 3. Convert persistence models into API response
    # -----------------------------------------------------

    response_messages = [
        {
            "role":
                message.role,

            "content":
                message.content,
        }
        for message in messages
    ]

    return SessionHistoryResponse(
        session_id=session_id,
        messages=response_messages,
    )


# =========================================================
# DELETE SESSION
# =========================================================

@router.delete(
    "/sessions/{session_id}",
    response_model=SessionDeleteResponse,
)
def delete_session(
    session_id: str,

    auth: AuthorizationContext = Depends(
        get_authorization_context
    ),
) -> SessionDeleteResponse:
    """
    Delete one conversation and all persisted messages
    belonging to that session.
    """

    try:
        deleted = (
            session_store.delete_session(
                session_id=session_id,
                user_id=auth.user_id,
            )
        )

    except PermissionError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_403_FORBIDDEN
            ),
            detail=str(error),
        ) from error

    if not deleted:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=(
                "Chat session was not found."
            ),
        )

    return SessionDeleteResponse(
        session_id=session_id,
        deleted=True,
    )